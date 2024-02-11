import asyncio
import cv2 as cv
import math
from ultralytics import YOLO
import datetime

class Target:
    def __init__(self, score, frame, CameraHandler, YOLO):
        x1 = YOLO.x1
        x2 = YOLO.x2
        y1 = YOLO.y1
        y2 = YOLO.y2
        self.tracker = cv.legacy.TrackerMedianFlow_create()
        self.tracker.init(frame, (x1,y1,x2-x1,y2-y1))
        self.wh = (x2-x1)+(y2-y1)
        self.frame = frame
        self.score = score
        self.target_coords = None
        self.target_yaw_angle = None
        asyncio.ensure_future(self.follow(CameraHandler=CameraHandler, YOLO=YOLO))

    async def follow(self, CameraHandler, YOLO):
        while True:
            frame = CameraHandler.read_frame()
            ok, bbox = self.tracker.update(frame)
            if ok == True:
                (x, y, w, h) = [int(v) for v in bbox]
                self.target_coords = (int(x+w/2) - 160, 160 - int(y+h/2))
                #self.calculate_distance_to_target()
                
                if self.wh / (w+h) < 0.8 or self.wh / (w+h) > 1.2 or x+y < 10: YOLO.detection_threshold = 0.3
                cv.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 1)
                cv.putText(frame, str('CAPTURE'), (10, 30), cv.QT_FONT_NORMAL, 1, (255, 255, 255))
                print(f"YOLO: detected at {datetime.datetime.now()}")
            else: YOLO.detection_threshold = 0.3
            
            self.frame = frame
            cv.imshow('detected', frame)
            if chr(cv.waitKey(1)&255) == 'q':
                break
            await asyncio.sleep(0.01)

    def calculate_target_yaw_angle(self):
        self.target_yaw_angle = round(math.atan2(self.target_coords[0], self.target_coords[1]) * 180 / math.pi, 2)

class YoloHandler:
    target = None
    target_coords = (0,0)
    target_yaw_angle = 0.0
    target_distance = 0.0
    tracker = None
    detection_threshold = 0.3
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    def __init__(self, CameraHandler):
        self.model = YOLO('yolov5nu.onnx')
        self.model(CameraHandler.read_frame(), verbose=False)
        self.target = None
        
    def calculate_distance_to_target(self):
        self.target_yaw_angle = round(math.atan2(self.target_coords[0], self.target_coords[1]) * 180 / math.pi, 2)

    async def detect(self, CameraHandler, StageHandler):
        
        while True:
            frame = CameraHandler.read_frame()
            results = self.model(frame, verbose=False)
            for result in results:
                for r in result.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = r
                    if score > self.detection_threshold and int(class_id) == 0:
                        self.x1 = int(x1)
                        self.y1 = int(y1)
                        self.x2 = int(x2)
                        self.y2 = int(y2)
                        #cv.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (255, 255, 0), 2)
                        if not StageHandler.target_detected: StageHandler.target_detected = True    
                        self.detection_threshold = score
                        if self.target == None:
                            self.target = Target(score=score, frame=frame, CameraHandler=CameraHandler, YOLO=self)
                        else:
                            self.target.tracker = cv.legacy.TrackerMedianFlow_create()
                            self.target.tracker.init(frame, (x1,y1,x2-x1,y2-y1))
                            self.target.wh = x2-x1 + y2-y1
                        if not StageHandler.target_captured: StageHandler.target_captured = True
#
            #if self.target.frame: frame = self.target.frame
            #if StageHandler.target_captured == True:
            #    ok, bbox = self.tracker.update(frame)
            #    if ok == True:
            #        (x, y, w, h) = [int(v) for v in bbox]
            #        
            #        self.target_coords = (int(x+w/2) - 200, 200 - int(y+h/2))
            #        self.calculate_distance_to_target()
            #        cv.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 1)
            #        cv.putText(frame, str('CAPTURE'), (10, 30), cv.QT_FONT_NORMAL, 1, (255, 255, 255))
            #        print(f"VISION: target validated with rate {score}")
            #        #print(f"x: {x1}-{x2} y: {y1}-{y2} score: {round(score, 2)}")
            
            #if not self.Target:
            

            await asyncio.sleep(0.05)

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
                    self.target_coords = (int(x+w/2) - 160, 160 - int(y+h/2))
                    print(x)
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

