import asyncio
import cv2 as cv
import math
from ultralytics import YOLO
import datetime

class YoloHandler:
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    def __init__(self):
        self.model = YOLO('yolov5nu.onnx')

    async def detect(self, CameraHandler):
        while True:
            frame = CameraHandler.read_frame()
            results = self.model(frame, verbose=False)
            for result in results:
                for r in result.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = r
                    if score > 0.30 and int(class_id) == 0:
                        self.x1 = x1
                        self.y1 = y1
                        self.x2 = x2
                        self.y2 = y2
                        cv.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
            cv.imshow('detected', frame)
            print(f"YOLO: detected at {datetime.datetime.now()}")
            if chr(cv.waitKey(1)&255) == 'q':
                break
            await asyncio.sleep(0.01)

class VisionHandler:
    target = None
    target_coords = (0,0)
    target_yaw_angle = 0.0
    target_distance = 0.0
    tracker = None
    detection_threshold = 0.3

    def __init__(self, Config):
        self.model = YOLO("yolov8n.pt")
        if (Config["sim_mode"]): 
            self.target = cv.imread(Config["sim_camera_config"]["target_img_path"], cv.COLOR_BGRA2RGB)
        else:
            pass

    async def process_image(self, CameraHandler, StageHandler):
        while True:
            image = cv.cvtColor(CameraHandler.image, cv.COLOR_BGRA2RGB)
            if StageHandler.stage == 1 and StageHandler.target_detected == False:
                self.detect_target(image, StageHandler)

            if StageHandler.target_captured == True:
                self.validate_target(image)
                ok, bbox = self.tracker.update(image)
                if ok == True:
                    (x, y, w, h) = [int(v) for v in bbox]
                    self.target_coords = (int(x+w/2) - 200, 200 - int(y+h/2))
                    self.calculate_distance_to_target()
                    cv.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 1)
                    cv.putText(image, str('CAPTURE'), (10, 30), cv.QT_FONT_NORMAL, 1, (255, 255, 255))

            cv.imshow('CV', image)
            if cv.waitKey(33) & 0xFF in (
                ord('q'), 
                27, 
            ):
                break
            await asyncio.sleep(0.1)

    def calculate_distance_to_target(self):
        self.target_yaw_angle = round(math.atan2(self.target_coords[0], self.target_coords[1]) * 180 / math.pi, 2)

    def validate_target(self, image):
        results = self.model(image, verbose=False)
        for result in results:
            for r in result.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                x1 = int(x1)
                x2 = int(x2)
                y1 = int(y1)
                y2 = int(y2)
                class_id = int(class_id)
                if score > self.detection_threshold and class_id == 0.0:
                    print(f"VISION: target validated with rate {score}")
                    print(f"x: {x1}-{x2} y: {y1}-{y2} score: {round(score, 2)}")
                    self.detection_threshold = score      
                    self.tracker = cv.legacy.TrackerMedianFlow_create()
                    self.tracker.init(image, (x1, y1, x2-x1, y2-y1))


    def detect_target(self, image, StageHandler):
        results = self.model(image, verbose=False)
        for result in results:
            for r in result.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                x1 = int(x1)
                x2 = int(x2)
                y1 = int(y1)
                y2 = int(y2)
                class_id = int(class_id)
                if score > self.detection_threshold and class_id == 0.0:
                    print("VISION: target detected")
                    print(f"x: {x1}-{x2} y: {y1}-{y2} score: {round(score, 2)}")
                    StageHandler.target_detected = True
                    self.tracker = cv.legacy.TrackerMedianFlow_create()
                    self.tracker.init(image, (x1, y1, x2-x1, y2-y1))
                    StageHandler.target_captured = True

class Target:
    def __init__(self, score, target_coords):
        self.score = score
        self.target_coords = target_coords
        self.target_yaw_angle = self.calculate_target_yaw_angle()

    def calculate_target_yaw_angle(self):
        self.target_yaw_angle = round(math.atan2(self.target_coords[0], self.target_coords[1]) * 180 / math.pi, 2)