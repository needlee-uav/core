import cv2 as cv
import numpy as np
import time
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
        child_conn.send(["READY"])
        if self.config.cameramode == "vision":
            while True:
                frame, net_img = self.read_frame()
                if len(frame) > 0:
                    detections = self.detect(frame=frame, net_img=net_img)
                    child_conn.send([frame, detections])

        elif self.config.cameramode == "stream":
            while True:
                frame, net_img = self.read_frame()
                if len(frame) > 0:
                    child_conn.send([frame, []])

    # CAMERA OPTIONS
    def pick_camera_option(self):
        if self.config.mode == "visiontest":
            self.cap = cv.VideoCapture(
                f"./camera/sim_camera/samples/{self.config.visiontest}.mp4"
            )
            self.read_frame = self.read_cap
        elif self.config.run == "sim":
            self.video = SimVideo()
            self.read_frame = self.read_sim_video

        while len(self.read_frame()[0]) == 0:
            time.sleep(1)

    def read_cap(self):
        ret, frame = self.cap.read()
        if ret:
            net_img = frame
            if self.config.run == "main":
                net_img = self.jetson_utils.cudaFromNumpy(frame)
            return frame, net_img
        else:
            return [], []

    def read_sim_video(self):
        if self.video.frame_available():
            frame = self.video.frame()
            net_img = frame
            return frame, net_img
        else:
            return [], []

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

        self.tracker = Tracker()

    def detect_sim(self, frame, net_img):
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