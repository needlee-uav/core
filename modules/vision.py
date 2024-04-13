import asyncio
import cv2 as cv
import math
from ultralytics import YOLO
import datetime
import threading, queue

class VisionHandler:
    def __init__(self, Pilot):
        self.Pilot = Pilot
        self.model = YOLO("yolov5nu.onnx")
        asyncio.ensure_future(self.vision())

    async def vision(self):
        while True:
            results = self.model(self.Pilot.params.img, verbose=False)
            for result in results:
                for r in result.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = r
                    if score > 0.30 and int(class_id) == 0:
                        self.Pilot.params.box = [x1, x2, y1, y2]
            await asyncio.sleep(0.4)
