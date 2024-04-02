import requests
import asyncio
import socketio, time, datetime
import threading
import cv2
import base64

class ServerHandler:
    Logger = None
    def __init__(self, server_config, CameraHandler, SensorsHandler, StageHandler, EmergencyHandler, Pilot):
        self.Pilot = Pilot
        self.EmergencyHandler = EmergencyHandler
        self.CameraHandler = CameraHandler
        self.SensorsHandler = SensorsHandler
        self.StageHandler = StageHandler
        self.debug = []
        self.server_config = server_config
        self.connected = False
        self.ready = False
        self.test_mode = None
        self.home = None
        self.route = None
        self.enable_camera = None

    def process_debug(self):
        if len(self.debug) > 0:
            msg = self.debug[0]
            self.debug.pop(0)
            return msg
        return ""

    def start_websocket(self):
        t = threading.Thread(target=self._handler)
        t.start()

    def _handler(self):
        sio = socketio.Client(engineio_logger=False)

        @sio.event
        def connect():
            self.Logger.log_debug("SERVER: connected")
            self.connected = True
            while self.SensorsHandler.position["lat"] == 0.0:
                time.sleep(1)
            sio.emit('vehicle_sign_in', data={
                "id": self.server_config["drone_id"],
                "lat": self.SensorsHandler.position["lat"],
                "lon": self.SensorsHandler.position["lon"],
                "alt": self.SensorsHandler.rel_alt,
                "h": self.SensorsHandler.heading,
                "v_m_s": self.SensorsHandler.velocity_down_m_s
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
                    "debug": self.process_debug(),
                    "log": {
                        "pitch": self.SensorsHandler.pitch,
                        "roll": self.SensorsHandler.roll,
                        "lat": self.SensorsHandler.position["lat"],
                        "lon": self.SensorsHandler.position["lon"],
                        "alt": self.SensorsHandler.rel_alt,
                        "h": self.SensorsHandler.heading,
                        "v_m_s": self.SensorsHandler.velocity_down_m_s
                    }
                })
                time.sleep(0)

        @sio.event
        def disconnect():
            self.connected = False
            self.Logger.log_debug("Server: disconnected")

        @sio.on("emergency")
        def emergency(data):
            self.EmergencyHandler.pass_emergency_data(data)

        @sio.on("update_config")
        def update_config():
            self.Logger.log_debug("Server: update config")

        @sio.on("ready")
        def ready(data):
            self.Logger.log_debug("SERVER: ready")
            self.Logger.log_debug("=============")
            self.Logger.log_debug(data)
            self.Logger.log_debug("=============")
            if data["test_mode"]:
                self.test_mode = data["test_mode"]
                self.home = data["home"]
                self.route = data["route"]
                self.enable_camera = data["enable_camera"]
                self.Pilot.enable_camera = self.enable_camera
            self.ready = True

        connected = False
        while not connected:
            try:
                sio.connect(self.server_config["url"], transports='websocket')
                self.Logger.log_debug("SERVER: socket established")
                connected = True
                sio.wait()
            except Exception as ex:
                self.Logger.log_debug("SERVER: failed to establish initial connnection to server:", type(ex).__name__)
                time.sleep(2)
