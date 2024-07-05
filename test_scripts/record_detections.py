import jetson_inference, jetson_utils
import cv2 as cv
import numpy as np
import subprocess, datetime

subprocess.Popen('export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1', shell=True)
count = 210 
net = jetson_inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson_utils.videoSource("/dev/video0", options={'width': 640, 'height': 480, 'framerate': 45}) 
bgr_img = jetson_utils.cudaAllocMapped(width=640, height=480, format="bgr8")
cv_img = None
time_ = datetime.datetime.now()
detections = None
camera.Capture(format='rgb8') 


with open("images/detections.txt","w") as f: 
	while count > 0:
		count = count - 1
		img = camera.Capture(format='rgb8') 
		if img is None: # capture timeout
			continue
		else:
			jetson_utils.cudaConvertColor(img, bgr_img)
			cv_img = jetson_utils.cudaToNumpy(bgr_img)
			jetson_utils.cudaDeviceSynchronize()

			detections = net.Detect(img, 640, 480)
			if len(detections) > 0:
				for detection in detections:
					if detection.ClassID == 1:
						print(count)
						f.write(f"{count}: {int(detection.Left)} {int(detection.Top)} {int(detection.Right)} {int(detection.Bottom)} {detection.Confidence}")
						f.write('\n')
		now = datetime.datetime.now() 
		print(f"delta {datetime.datetime.now()  - time_}")
		time_ = now