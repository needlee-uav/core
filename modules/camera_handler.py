import asyncio, queue, threading, time, cv2 as cv
import numpy as np
import mss
from PIL import Image
# sudo libcamera-vid -n -t 0 --width 320 --height 320 --framerate 10 --mode 320:320:10 --inline --listen -o tcp://127.0.0.1:8888

class CameraHandler:
    def __init__(self, Pilot):
        self.Pilot = Pilot
        self.img = np.zeros([100,100,3],dtype=np.uint8)
        self.img.fill(255)
        self.Pilot.params.img = self.img
        asyncio.ensure_future(self.view_camera_video())

    async def view_camera_video(self):
        while self.Pilot.params.server.enable_camera == False:
            await asyncio.sleep(0.1)
        if self.Pilot.config.sim:
            self.sct = mss.mss()
            self.source = self.sct.monitors[1]
            self.read_frame = self.read_sim_frame
        else:
            self.cap = cv.VideoCapture(self.Pilot.config.vision.camera_address)
            self.cap.set(cv.CAP_PROP_FPS, 10)
            self.cap.set(cv.CAP_PROP_BUFFERSIZE, 0)
            self.q = queue.Queue()
            t = threading.Thread(target=self._reader)
            t.daemon = True
            t.start()

        while True:
            self.read_frame()
            await asyncio.sleep(0.1)

    def read_frame(self):
        self.img = self.q.get()
        self.Pilot.params.img = self.img
        return self.img

    def read_sim_frame(self):
        monitor = self.sct.monitors[1]
        screenShot = self.sct.grab(monitor)
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.bgra,
            'raw',
            'BGRX'
        )
        self.img = cv.cvtColor(np.array(img)[600:1000, 1500:1900], cv.COLOR_BGRA2RGB)
        self.Pilot.params.img = self.img
        return self.img

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
