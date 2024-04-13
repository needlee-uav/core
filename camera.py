import cv2 as cv
import numpy as np
import mss
from PIL import Image
from ultralytics import YOLO
import datetime

def view_camera_video(child_conn, config):
    img = np.zeros([500,500,3],dtype=np.uint8)
    img.fill(255)
    model = YOLO("yolov5nu.onnx")
    sct = mss.mss()
    source = sct.monitors[1]
    while True:
        print(datetime.datetime.now())
        screenShot = sct.grab(source)
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.bgra,
            'raw',
            'BGRX'
        )
        img = cv.cvtColor(np.array(img)[600:1000, 1500:1900], cv.COLOR_BGRA2RGB)
        results = model(img, verbose=False)
        sent = False
        for result in results:
            for r in result.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                if score > 0.30 and int(class_id) == 0:
                    child_conn.send([x1, y1, x2, y2, img])
                    sent = True
        if not sent: child_conn.send([0, 0, 0, 0, img])
