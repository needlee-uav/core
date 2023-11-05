from picamera2 import Picamera2
import time
import cv2 as cv

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()
time.sleep(0.1)

while True:
    im = camera.capture_array()
    
    cv.imshow("test", im)
    cv.waitKey(1)