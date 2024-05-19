import cv2 as cv
import numpy as np
import datetime
from camera.sim_video import SimVideo

def view_camera_video(child_conn, config):
    img = np.zeros([config.vision.width, config.vision.height, 3],dtype=np.uint8)
    img.fill(255)
    novision = True if not config.vision.model else False
    
    if config.sim:
        run_sim(novision, child_conn)
    else:
        run_jetson(novision, config, child_conn)

class Tracker:
    cv_box = [0,0,0,0]
    tracker = False
    def track(self, net_box, frame):
        if net_box == False:
            if self.tracker != False:
                ok, bbox = self.tracker.update(frame)
                if ok == True:
                    (x, y, w, h) = [int(v) for v in bbox]
                    self.cv_box = [x, y, x+w, y+h]
                else:
                    self.cv_box = [0,0,0,0]
                    self.tracker = False
        else:
            self.tracker = cv.legacy.TrackerMedianFlow_create()
            self.tracker.init(frame, (
                net_box[0],
                net_box[1],
                net_box[2]-net_box[0],
                net_box[3]-net_box[1]
            ))

def run_sim(novision, child_conn):
    net = None
    prototxt = "./camera/MobileNetSSD_deploy.prototxt"
    caffe_model = "./camera/MobileNetSSD_deploy.caffemodel"
    classPerson = 15
    if not novision:
        net = cv.dnn.readNetFromCaffe(prototxt, caffe_model)
    
    video = SimVideo()
    if novision:
        while True:
            if not video.frame_available():
                continue
            frame = video.frame()
            child_conn.send([0, 0, 0, 0, frame, 0])
    tracker = Tracker()
    while True:
        if not video.frame_available():
            continue
        frame = video.frame()
        width = frame.shape[1]
        height = frame.shape[0]
        blob = cv.dnn.blobFromImage(frame, scalefactor = 1/127.5, size = (640, 360), mean = (127.5, 127.5, 127.5), swapRB=True, crop=False)
        net.setInput(blob)
        detections = net.forward()
        sent = False
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.3 and int(detections[0, 0, i, 1]) == classPerson:
                x1 = int(detections[0, 0, i, 3] * width)
                y1 = int(detections[0, 0, i, 4] * height)
                x2 = int(detections[0, 0, i, 5] * width)
                y2 = int(detections[0, 0, i, 6] * height)
                tracker.track([x1, y1, x2, y2], frame)
                child_conn.send([x1, y1, x2, y2, frame, confidence])
                sent = True
            
        if not sent:
            tracker.track(False, frame)
            child_conn.send([
                tracker.cv_box[0],
                tracker.cv_box[1],
                tracker.cv_box[2],
                tracker.cv_box[3],
                frame,
                0
            ])
        # cv.imshow('window', frame)
        # if cv.waitKey(10) & 0xFF == ord('q'): break

def run_jetson(novision, config, child_conn):
    #TODO add tracker
    import jetson_interface
    import jetson_utils
        
    camera = jetson_utils.gstCamera(config.vision.width, config.vision.height, config.vision.camera_address)
    if novision:
        while True:
            img, width, height = camera.CaptureRGBA()
            aimg = jetson_utils.cudaToNumpy(img, width, height, 4)
            frame = cv.cvtColor(aimg.astype(np.uint8), cv.COLOR_RGBA2BGR)
            child_conn.send([0, 0, 0, 0, frame, 0])
            
    model = jetson_interface.detectNet(config.vision.model, threshold=0.5)
    while True:
        img, width, height = camera.CaptureRGBA()
        aimg = jetson_utils.cudaToNumpy(img, width, height, 4)
        frame = cv.cvtColor(aimg.astype(np.uint8), cv.COLOR_RGBA2BGR)
        detections = model.Detect(img, width, height)
        sent = False
        if len(detections) > 0:
            #some sorting logic
            for d in detections:
                if d.ClassID == 1 and not sent:
                    child_conn.send([int(d.Left), int(d.Top), int(d.Right), int(d.Bottom), frame, 0])
                    sent = True
        if not sent: child_conn.send([0, 0, 0, 0, frame, 0])


