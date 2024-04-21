import cv2 as cv
import numpy as np
import datetime

def view_camera_video(child_conn, config):
    img = np.zeros([config.vision.width, config.vision.height, 3],dtype=np.uint8)
    img.fill(255)
    if config.sim:
        import mss
        from PIL import Image
        from ultralytics import YOLO
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
                #some sorting logic
                for r in result.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = r
                    if score > 0.30 and int(class_id) == 0 and not sent:
                        child_conn.send([x1, y1, x2, y2, img])
                        sent = True
            if not sent: child_conn.send([0, 0, 0, 0, img])

    else:
        import jetson_interface
        import jetson_utils
        model = jetson_interface.detectNet(config.vision.model, threshold=0.5)
        camera = jetson_utils.gstCamera(config.vision.width, config.vision.height, config.vision.camera_address)
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
                        child_conn.send([int(d.Left), int(d.Top), int(d.Right), int(d.Bottom), frame])
                        sent = True
            if not sent: child_conn.send([0, 0, 0, 0, frame])
