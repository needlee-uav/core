import jetson_inference
import jetson_utils
import cv2
import time, datetime
import subprocess

class Camera:
    ready = False

    def run(self, child_conn):
        subprocess.Popen('export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1', shell=True)
            
        self.camera = jetson_utils.videoSource("/dev/video0", options={'width': 640, 'height': 480, 'framerate': 45}) 
        self.net = jetson_inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

        self.count = 15
        self.bgr_img = jetson_utils.cudaAllocMapped(width=640, height=480, format="bgr8")
        self.cv_img = None
        self.time_ = datetime.datetime.now()
        self.detections = None
        self.camera.Capture(format='rgb8') 
        
        while self.count > 0:
            self.count = self.count - 1
            img = self.camera.Capture(format='rgb8') 

            if img is None: # capture timeout
                continue
            else:
                self.ready = True
                jetson_utils.cudaConvertColor(img, self.bgr_img)
                self.cv_img = jetson_utils.cudaToNumpy(self.bgr_img)
                jetson_utils.cudaDeviceSynchronize()

                self.detections = self.net.Detect(img, 640, 480)
                if len(self.detections) > 0:
                    for detection in self.detections:
                        if detection.ClassID == 1:
                            print(self.count)  
                            #child_conn.send([self.cv_img, [f"{self.count}: {int(detection.Left)} {int(detection.Top)} {int(detection.Right)} {int(detection.Bottom)} {detection.Confidence}"]])

            now = datetime.datetime.now() 
            print(f"delta {datetime.datetime.now()  - self.time_}")
            self.time_ = now
        
        
   
