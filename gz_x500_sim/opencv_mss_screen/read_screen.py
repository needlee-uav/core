import numpy as np
import cv2 as cv
import mss
from PIL import Image

with mss.mss() as sct:
    target = cv.imread('target.png', cv.IMREAD_UNCHANGED)

    monitor = sct.monitors[1]
    while True:
        screenShot = sct.grab(monitor)
        img = Image.frombytes(
            'RGB', 
            (screenShot.width, screenShot.height), 
            screenShot.rgb, 
        )

        picture = np.array(img)[650:1000, 1500:1900]
        result = cv.matchTemplate(picture, target, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if (max_val > 0.8): 
            top_left = max_loc
            bottom_right = (top_left[0] + target.shape[1], top_left[1] + target.shape[1])
            cv.rectangle(picture, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
        
        cv.imshow('test', picture)
        if cv.waitKey(33) & 0xFF in (
            ord('q'), 
            27, 
        ):
            break