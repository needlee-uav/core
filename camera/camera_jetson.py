import cv2 as cv
import numpy as np
import datetime
from camera.camera import Tracker, Target

class JetsonModel:
    import jetson_interface
    import jetson_utils

    def __init__(self, config, child_conn):
        #TODO w/h from config
        self.w = 640
        self.h = 360
        self.classPerson = 1
        self.child_conn = child_conn
        self.camera = self.jetson_utils.gstCamera(config.vision.width, config.vision.height, config.vision.camera_address)
        self.model = self.jetson_interface.detectNet(config.vision.model, threshold=0.5)
        self.tracker = Tracker()
        self.target = Target()

    def run(self):
        if self.novision:
            while True:
                img, width, height = self.camera.CaptureRGBA()
                aimg = self.jetson_utils.cudaToNumpy(img, width, height, 4)
                frame = cv.cvtColor(aimg.astype(np.uint8), cv.COLOR_RGBA2BGR)
                self.child_conn.send([0, 0, 0, 0, frame, 0])

        while True:
            img, width, height = self.camera.CaptureRGBA()
            aimg = self.jetson_utils.cudaToNumpy(img, width, height, 4)
            frame = cv.cvtColor(aimg.astype(np.uint8), cv.COLOR_RGBA2BGR)
            detections = self.model.Detect(img, width, height)
            self.process_detections(detections)
            self.send(frame)

    def send(self, frame):
        if self.target.detected == False:
            self.tracker.track(
                [
                    self.target.x1,
                    self.target.y1,
                    self.target.x2,
                    self.target.y2
                ], 
                frame)
            
            self.child_conn.send([
                self.target.x1,
                self.target.y1,
                self.target.x2,
                self.target.y2,
                frame, 
                self.target.confidence
            ])
        else:
            self.tracker.track(False, frame)
            self.child_conn.send([
                self.tracker.cv_box[0],
                self.tracker.cv_box[1],
                self.tracker.cv_box[2],
                self.tracker.cv_box[3],
                frame,
                0
            ])

    def process_detections(self, detections):
        for d in detections:
            if d.ClassID == self.classPerson:
                self.target.x1 = int(d.Left)
                self.target.y1 = int(d.Top)
                self.target.x2 = int(d.Right)
                self.target.y2 = int(d.Bottom)
                self.target.detected = True
                #TODO
                # if confidence > 0 and confidence > self.target.confidence: 
                self.target.confidence = 0.5
                return
            else:
                self.target.detected = False
                self.target.confidence = 0.0
