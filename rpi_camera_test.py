import cv2 as cv, queue, threading, time, asyncio

class TestVideoCapture:
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
    
async def show(cap):
    while True:
        frame = cap.read_frame()
        cv.imshow('frame', frame)
        if chr(cv.waitKey(1)&255) == 'q':
            break
        await asyncio.sleep(0.01)

async def do_things():
    while True:
        time.sleep(0.1)
        await asyncio.sleep(0.1)

async def run():
    cap = TestVideoCapture('tcp://127.0.0.1:8888')
    asyncio.ensure_future(show(cap))
    asyncio.ensure_future(do_things())
    while True:
        await asyncio.sleep(1)

asyncio.run(run())