import cv2 as cv
import numpy as np
import time, subprocess, jetson_utils, jetson_inference

class Target:
    detected = False
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    confidence = 0

class Tracker:
    cv_box = [0,0,0,0]
    tracker = False

    def update(self, box):
        self.cv_box = box

    def destroy(self):
        self.tracker = False

    def track(self, frame):
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
            box = self.cv_box
            self.tracker.init(frame, (
                box[0],
                box[1],
                box[2]-box[0],
                box[3]-box[1]
            ))

class Camera:
    box = []
    frame = []
    confidence = 0
    net = False

    def __init__(self, config):
        self.frame = np.zeros([config.camera.width, config.camera.height, 3],dtype=np.uint8)
        self.frame.fill(255)
        self.config = config
        self.w = self.config.camera.width
        self.h = self.config.camera.height

    def run(self, child_conn):
        subprocess.Popen('export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1', shell=True)
        self.camera = jetson_utils.videoSource("/dev/video0", options={'width': 640, 'height': 480, 'framerate': 45}) 
        self.bgr_img = jetson_utils.cudaAllocMapped(width=640, height=480, format="bgr8")
        
        if self.config.cameramode == "vision":
            self.net = jetson_inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
            self.tracker = Tracker()
        
        self.camera.Capture(format='rgb8') 
        child_conn.send(["READY"])
        print("CAM READY")
        if self.config.cameramode == "stream":
            while True:
                img = self.camera.Capture(format='rgb8') 
                if img is None: # capture timeout
                    continue
                jetson_utils.cudaConvertColor(img, self.bgr_img)
                cv_img = jetson_utils.cudaToNumpy(self.bgr_img)
                jetson_utils.cudaDeviceSynchronize()
                child_conn.send([cv_img, []])

        elif self.config.cameramode == "vision":
            while True:
                img = self.camera.Capture(format='rgb8') 
                if img is None: # capture timeout
                    continue
                jetson_utils.cudaConvertColor(img, self.bgr_img)
                cv_img = jetson_utils.cudaToNumpy(self.bgr_img)
                jetson_utils.cudaDeviceSynchronize()
                detections = self.net.Detect(img, 640, 480)
                d = []
                
                if len(detections) > 0:
                    for detection in detections:
                        if detection.ClassID == 1:
                            self.tracker.update([
                                int(detection.Left),
                                int(detection.Top),
                                int(detection.Right),
                                int(detection.Bottom)
                            ])
                            d = [
                                True,
                                int(detection.Left),
                                int(detection.Top),
                                int(detection.Right),
                                int(detection.Bottom),
                                round(float(detection.Confidence), 2)
                            ]
                            self.tracker.destroy()
                else: 
                    self.tracker.track(frame=cv_img)
                    d =  [False] + self.tracker.cv_box + [0]

                child_conn.send([cv_img, d])

    # def read_cap(self):
    #     ret, frame = self.cap.read()
    #     if ret:
    #         net_img = frame
    #         if self.config.run == "main":
    #             net_img = self.jetson_utils.cudaFromNumpy(frame)
    #         return frame, net_img
    #     else:
    #         return [], []
   