import asyncio, queue, threading, time, cv2 as cv
import numpy as np
import mss
from PIL import Image

class CameraHandler:
    def __init__(self, tcp_source) -> None:
        self.cap = cv.VideoCapture(tcp_source)
        self.cap.set(cv.CAP_PROP_FPS, 24)
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

class CameraTestScreen:
    async def show_frame(self, CameraHandler):
        while True:
            frame = CameraHandler.read_frame()
            cv.imshow('frame', frame)
            if chr(cv.waitKey(1)&255) == 'q': break
            await asyncio.sleep(0.05)

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

    async def read_sim_image(self):
        monitor = self.sct.monitors[1]
        while True:
            screenShot = self.sct.grab(monitor)
            img = Image.frombytes(
                'RGB', 
                (screenShot.width, screenShot.height), 
                screenShot.bgra, 
                'raw', 
                'BGRX'
            )
            self.image = np.array(img)[600:1000, 1500:1900]
                
            await asyncio.sleep(0.1)

    