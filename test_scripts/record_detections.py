import jetson_inference
import jetson_utils
import cv2 as cv
import numpy as np

size = 640
count = 210 
net = jetson_inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson_utils.gstCamera(size, size, "/dev/video0")

with open("detections.txt","w") as f: 
	while count > 0:
		count = count - 1
		img, width, height = camera.CaptureRGBA()

		aimg = jetson_utils.cudaToNumpy(img, width, height, 4)
		frame = cv.cvtColor(aimg.astype(np.uint8), cv.COLOR_RGBA2BGR)
		cv.imwrite(f"{count}_{size}px.png", frame)
		detections = net.Detect(img, size, size)

		if len(detections) > 0:
			for detection in detections:
				if detection.ClassID == 1:
					print(count)
					f.write(f"{count}: {int(detection.Left)} {int(detection.Top)} {int(detection.Right)} {int(detection.Bottom)} {detection.Confidence}")
					f.write('\n')
