import cv2 as cv
import numpy as np
import datetime
import time
from camera.sim_video import SimVideo
from camera.camera import Tracker, Target

class SimModel:
    def __init__(self, config, child_conn):
        
        self.net = False
        self.child_conn = child_conn

        if config.camera.model:
            self.classPerson = 15
            prototxt = f"./camera/sim_camera/{config.camera.model}.prototxt"
            caffe_model = f"./camera/sim_camera/{config.camera.model}.caffemodel"
            self.net = cv.dnn.readNetFromCaffe(prototxt, caffe_model)
            self.tracker = Tracker()
            self.target = Target()
            
        if config.mode == "visiontest":
            file_path = f"./camera/sim_camera/samples/{config.visiontest}.mp4"
            self.cap = cv.VideoCapture(file_path)
            self.read_frame = self.read_cap
        else:
            self.video = SimVideo()
            self.read_frame = self.read_sim_video

    def run(self):
        while len(self.read_frame()) == 0:
            time.sleep(1)
        frame = self.read_frame()
        self.w = int(frame.shape[1])
        self.h = int(frame.shape[0])
        print(self.h)
        print(self.w)
        
        while True:
            frame = self.read_frame()
            if len(frame) > 0:
                blob = cv.dnn.blobFromImage(frame, scalefactor = 1/127.5, size = (self.w, self.h), mean = (127.5, 127.5, 127.5), swapRB=True, crop=False)
                self.net.setInput(blob)
                detections = self.net.forward()
                self.process_detections(detections)
                self.send(frame)

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
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.3 and int(detections[0, 0, i, 1]) == self.classPerson:
                self.target.confidence = round(confidence, 2)
                self.target.x1 = int(detections[0, 0, i, 3] * self.w)
                self.target.y1 = int(detections[0, 0, i, 4] * self.h)
                self.target.x2 = int(detections[0, 0, i, 5] * self.w)
                self.target.y2 = int(detections[0, 0, i, 6] * self.h)
                self.target.detected = True
                return
            else:
                self.target.detected = False