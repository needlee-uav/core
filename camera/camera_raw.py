import cv2 as cv
import numpy as np
import datetime, time
from camera.sim_video import SimVideo

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
        self.pick_camera_option()
        self.init_cv()

        if self.config.cameramode == "vision":
            while True:
                frame = self.read_frame()
                if len(frame) > 0:
                    detections = self.detect(frame=frame)
                    child_conn.send([frame, detections])

        elif self.config.cameramode == "stream":
            while True:
                frame = self.read_frame()
                if len(frame) > 0:
                    child_conn.send([frame, []])

    # CAMERA OPTIONS
    def pick_camera_option(self):
        if self.config.mode == "visiontest":
            if self.config.visiontest == 101 and self.config.run == "main":
                import jetson_utils
                self.jetson_utils = jetson_utils
                self.camera = self.jetson_utils.gstCamera(self.w, self.h, self.config.camera.camera_address)
                self.read_frame = self.read_camera_video
            else:
                self.cap = cv.VideoCapture(
                    f"./camera/sim_camera/samples/{self.config.visiontest}.mp4"
                )
                self.read_frame = self.read_cap

        elif self.config.run == "sim":
            self.video = SimVideo()
            self.read_frame = self.read_sim_video
            
        elif self.config.run == "main":
            import jetson_utils
            self.jetson_utils = jetson_utils
            self.camera = self.jetson_utils.gstCamera(self.w, self.h, self.config.camera.camera_address)
            self.read_frame = self.read_camera_video

        while len(self.read_frame()) == 0:
            time.sleep(1)

    def read_cap(self):
        ret, frame = self.cap.read()
        if ret:
            return frame
        else:
            return []

    def read_sim_video(self):
        if self.video.frame_available():
            frame = self.video.frame()
            return frame
        else:
            return []
        
    def read_camera_video(self):
        try:
            img, width, height = self.camera.CaptureRGBA()
            aimg = self.jetson_utils.cudaToNumpy(img, width, height, 4)
            frame = cv.cvtColor(aimg.astype(np.uint8), cv.COLOR_RGBA2BGR)
            return frame
        except:
            return []
        

    # VISION OPTIONS
    def init_cv(self):
        if self.config.cameramode != "vision":
            self.net = False
        
        elif self.config.run == "sim":
            self.classPerson = 15
            self.net = cv.dnn.readNetFromCaffe(
                f"./camera/sim_camera/{self.config.camera.model}.prototxt",
                f"./camera/sim_camera/{self.config.camera.model}.caffemodel"
            )
            self.detect = self.detect_sim

        elif self.config.run == "main":
            import jetson_inference
            self.jetson_inference = jetson_inference
            self.classPerson = 1
            self.net = self.jetson_inference.detectNet(self.config.camera.model, threshold=0.5)
            self.detect = self.detect_main

        self.tracker = Tracker()

    def detect_sim(self, frame):
        blob = cv.dnn.blobFromImage(frame, scalefactor = 1/127.5, size = (self.w, self.h), mean = (127.5, 127.5, 127.5), swapRB=True, crop=False)
        self.net.setInput(blob)
        detections = self.process_sim_detections(self.net.forward())
        if not detections:
            self.tracker.track(frame=frame)
            return [False] + self.tracker.cv_box + [0]
        else:
            self.tracker.destroy()
            return detections
    

    def process_sim_detections(self, detections):
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.3 and int(detections[0, 0, i, 1]) == self.classPerson:
                self.tracker.update([
                    int(detections[0, 0, i, 3] * self.w),
                    int(detections[0, 0, i, 4] * self.h),
                    int(detections[0, 0, i, 5] * self.w),
                    int(detections[0, 0, i, 6] * self.h)
                ])
                return [
                    True,
                    int(detections[0, 0, i, 3] * self.w),
                    int(detections[0, 0, i, 4] * self.h),
                    int(detections[0, 0, i, 5] * self.w),
                    int(detections[0, 0, i, 6] * self.h),
                    round(float(confidence), 2)
                ]
            
    def detect_main(self, frame):
        detections = self.net.Detect(frame, self.w, self.h)
        detections = self.process_main_detections(detections)
        if not detections:
            self.tracker.track(frame=frame)
            return [False] + self.tracker.cv_box + [0]
        else:
            self.tracker.destroy()
            return detections
    
    def process_main_detections(self, detections):
        for d in detections:
            if d.ClassID == self.classPerson:
                self.tracker.update([
                    int(d.Left),
                    int(d.Top),
                    int(d.Right),
                    int(d.Bottom)
                ])
                return [
                    True,
                    int(d.Left),
                    int(d.Top),
                    int(d.Right),
                    int(d.Bottom),
                    30
                ]
        