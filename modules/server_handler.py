import requests
import asyncio
import socketio, time, datetime
import threading
import cv2
import base64

class WebSocketHandler:
    def __init__(self, server_config, CameraHandler, SensorsHandler, StageHandler):
        self.CameraHandler = CameraHandler
        self.SensorsHandler = SensorsHandler
        self.StageHandler = StageHandler
        self.server_config = server_config
        self.connected = False
        self.ready = False
        self.test_mode = None
        self.home = None
        self.route = None

    def start_websocket(self):
        t = threading.Thread(target=self._handler)
        t.start()

    def _handler(self):
        sio = socketio.Client(engineio_logger=True)
        
        @sio.event
        def connect():
            print("CONNECTED!")
            self.connected = True
            while self.SensorsHandler.position["lat"] == 0.0:
                time.sleep(1)
            sio.emit('vehicle_sign_in', data={
                "id": self.server_config["drone_id"],
                "lat": self.SensorsHandler.position["lat"],
                "lon": self.SensorsHandler.position["lon"],
                "alt": self.SensorsHandler.rel_alt,
                "h": self.SensorsHandler.heading
            })
            
            while True:
                time.sleep(0.1)
                img = cv2.resize(self.CameraHandler.image, (0,0), fx=0.5, fy=0.5)
                frame = cv2.imencode('.jpg', img)[1].tobytes()
                frame = base64.encodebytes(frame).decode("utf-8")
                frame = frame.replace("data:image/jpeg;base64,", "")
                sio.emit('stream', data={
                    "shape": {"w": 320, "h": 320}, 
                    "frame": frame, 
                    "log": {
                        "pitch": self.SensorsHandler.pitch, 
                        "roll": self.SensorsHandler.roll, 
                        "lat": self.SensorsHandler.position["lat"], 
                        "lon": self.SensorsHandler.position["lon"], 
                        "alt": self.SensorsHandler.rel_alt, 
                        "h": self.SensorsHandler.heading
                    }
                })
                time.sleep(0)

        @sio.event
        def disconnect():
            self.connected = False
            print("DISCONNECTED")

        @sio.on("update_config")
        def update_config():
            print("update_config")

        @sio.on("ready")
        def ready(data):
            print("=============")
            print(data)
            print("=============")
            if data["test_mode"]:
                self.test_mode = data["test_mode"]
                self.home = data["home"]
                self.route = data["route"]
            self.ready = True
            print("SERVER: ready")

        connected = False
        while not connected:
            try:
                sio.connect(self.server_config["url"], transports='websocket')
                print("Socket established")
                connected = True
                sio.wait()
            except Exception as ex:
                print("Failed to establish initial connnection to server:", type(ex).__name__)
                time.sleep(2)

    
