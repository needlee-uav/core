import jetson_inference
import jetson_utils
import cv2
import time, datetime
import subprocess, os

class Camera:
    ready = False
    folder = f"{datetime.datetime.now()}"
    if not os.path.exists("/home/jetson/Desktop/images"):
        os.makedirs("/home/jetson/Desktop/images")
    if not os.path.exists(f"/home/jetson/Desktop/images/{folder}"):
        os.makedirs(f"/home/jetson/Desktop/images/{folder}")

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
        with open(f"/home/jetson/Desktop/images/{self.folder}/detections.txt","w") as f: 
            while self.count > 0:
                self.count = self.count - 1
                img = self.camera.Capture(format='rgb8') 

                if img is None: # capture timeout
                    continue
                else:
                    if not self.ready: 
                        child_conn.send(["READY"])
                        self.ready = True
                    jetson_utils.cudaConvertColor(img, self.bgr_img)
                    self.cv_img = jetson_utils.cudaToNumpy(self.bgr_img)
                    jetson_utils.cudaDeviceSynchronize()
                    cv2.imwrite(f"/home/jetson/Desktop/images/{self.folder}/img{self.count}.png", self.cv_img)
                    self.detections = self.net.Detect(img, 640, 480)
                    if len(self.detections) > 0:
                        for detection in self.detections:
                            if detection.ClassID == 1:
                                print(self.count)  
                                f.write(f"{self.count}: {int(detection.Left)} {int(detection.Top)} {int(detection.Right)} {int(detection.Bottom)} {detection.Confidence}")
                                f.write('\n')

                now = datetime.datetime.now() 
                print(f"delta {datetime.datetime.now()  - self.time_}")
                self.time_ = now
        
        child_conn.send(["DONE"])
        return       
   