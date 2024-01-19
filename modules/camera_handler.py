import asyncio, queue, threading, time, cv2 as cv
import numpy as np
import mss
from PIL import Image
# sudo libcamera-vid -n -t 0 --width 332 --height 332 --framerate 10 --mode 332:332:10 --inline --listen -o tcp://127.0.0.1:8888
class CameraHandler:
    def __init__(self, Config) -> None:
        self.cap = cv.VideoCapture('tcp://127.0.0.1:8888')
        self.cap.set(cv.CAP_PROP_FPS, 10)
        self.cap.set(cv.CAP_PROP_BUFFERSIZE, 0)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()
    
    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret: break
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)
    
    def read_frame(self):
        return self.q.get()

class SimCameraHandler:
    config = {}
    image = None
    sct = mss.mss()
    source = None

    def __init__(self, Config):
        self.set_config(Config=Config)
        self.source = self.sct.monitors[1]
        screenShot = self.sct.grab(self.source)
        img = Image.frombytes(
            'RGB', 
            (screenShot.width, screenShot.height), 
            screenShot.rgb, 
        )
        self.image = np.array(img)[600:1000, 1500:1900]

    def set_config(self, Config):
        if (Config["sim_mode"]): 
            self.config = Config["sim_camera_config"]
        else:
            self.config = Config["camera_config"]

    def read_frame(self):
        monitor = self.sct.monitors[1]
        
        screenShot = self.sct.grab(monitor)
        img = Image.frombytes(
            'RGB', 
            (screenShot.width, screenShot.height), 
            screenShot.bgra, 
            'raw', 
            'BGRX'
        )
        self.image = cv.cvtColor(np.array(img)[600:1000, 1500:1900], cv.COLOR_BGRA2RGB)
        return self.image
            

    