#pip3 install --upgrade flask-socketio==5.1.2 
#pip3 install --upgrade python-socketio==5.6.0
#pip3 install --upgrade python-engineio==4.3.2
import socketio, time, datetime
import cv2
import requests
import sys
import json
import base64
from time import sleep
import random

file_path = 'people.mp4'
delay = 1
window_name = 'frame'

cap = cv2.VideoCapture(file_path)

def recalc_log():
	return {"lat": 41.6938, "lon": 44.8015, "alt": 2, "h": 192, "pitch": -20, "roll": -0}

sio = socketio.Client(engineio_logger=True)
@sio.event
def connect():
	print("CONNECTED")
	print(f"cap is opened: {cap.isOpened()}")
	log = recalc_log()
	log["id"] = "UAV-1234"
	log["test_mode"] = True
	sio.emit('vehicle_sign_in', data=log)
	sio.emit('move_map_to_vehicle', data=recalc_log())
	while(cap.isOpened()):
		time.sleep(0.1)
		ret,img=cap.read()
		log = recalc_log()
		if ret:
			img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
			frame = cv2.imencode('.jpg', img)[1].tobytes()
			frame= base64.encodebytes(frame).decode("utf-8")
			sio.emit('stream', data={"frame": frame, "log": log, "shape": {"w": 640, "h": 360}})
			sleep(0)
		else:
			break

@sio.event
def disconnect():
	print("DISCONNECTED")
	
if __name__ == '__main__':
	connected = False
	while not connected:
		try:
			sio.connect('https://needlee.uc.r.appspot.com/', transports='websocket')
			#sio.connect('http://0.0.0.0:8080/', transports='polling')
			print("Socket established")
			connected = True
			sio.wait()
		except Exception as ex:
			print("Failed to establish initial connnection to server:", type(ex).__name__)
			time.sleep(2)

	
	
