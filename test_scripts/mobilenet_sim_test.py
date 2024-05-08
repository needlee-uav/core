# https://github.com/djmv/MobilNet_SSD_opencv
# https://medium.com/@tauseefahmad12/object-detection-using-mobilenet-ssd-e75b177567ee
import numpy as np
import cv2 
import datetime

prototxt = "MobileNetSSD_deploy.prototxt"
caffe_model = "MobileNetSSD_deploy.caffemodel"
net = cv2.dnn.readNetFromCaffe(prototxt, caffe_model)
classNames = { 0: 'background',
    15: 'person'}

file_path = 'client_test/people.mp4'
cap = cv2.VideoCapture(file_path)

while True:
    ret, frame = cap.read()
    if ret:
        width = frame.shape[1] 
        height = frame.shape[0]
        blob = cv2.dnn.blobFromImage(frame, scalefactor = 1/127.5, size = (640, 640), mean = (127.5, 127.5, 127.5), swapRB=True, crop=False)
        net.setInput(blob)
        detections = net.forward()
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5 and int(detections[0, 0, i, 1]) == 15:
                x_top_left = int(detections[0, 0, i, 3] * width) 
                y_top_left = int(detections[0, 0, i, 4] * height)
                x_bottom_right = int(detections[0, 0, i, 5] * width)
                y_bottom_right = int(detections[0, 0, i, 6] * height)
                cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right),(0, 255, 0))

        cv2.imshow("frame", frame)
        if cv2.waitKey(1) >= 0:  
            break
        print(datetime.datetime.now())
