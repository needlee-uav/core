import socketio, time
import threading
import cv2
import base64
from data_classes import Position

class ServerHandler:
    Pilot = None
    def __init__(self, logger, config):
        self.config = config
        self.logger = logger
        self.emergency = False
        self.start_websocket()

    def process_debug(self):
        if len(self.logger.debug_log) > 0:
            msg = self.logger.debug_log[0]
            self.logger.debug_log.pop(0)
            return msg
        return ""

    def start_websocket(self):
        t = threading.Thread(target=self._handler)
        t.start()

    def _handler(self):
        while self.Pilot == None:
            time.sleep(1)
        print("SERVER: Pilot connected")

        self.logger.log_debug("SERVER: open connection")
        sio = socketio.Client(engineio_logger=False)
        @sio.event
        def connect():
            self.logger.log_debug("SERVER: connected")
            self.Pilot.params.server.connected = True
            while not self.Pilot.params.sensors.ready:
                time.sleep(1)
            sio.emit('vehicle_sign_in', data={
                "id": self.Pilot.config.drone_id,
                "lat": self.Pilot.params.sensors.position.lat,
                "lon": self.Pilot.params.sensors.position.lon,
                "alt": self.Pilot.params.sensors.position.alt,
                "h": self.Pilot.params.sensors.heading,
                "v_m_s": self.Pilot.params.sensors.velocity_down_m_s,
            })
            self.logger.log_debug("SERVER: vehicle sign in")
            while True:
                time.sleep(0.1)
                img = cv2.resize(self.Pilot.params.img, (0,0), fx=0.5, fy=0.5)
                frame = cv2.imencode('.jpg', img)[1].tobytes()
                frame = base64.encodebytes(frame).decode("utf-8")
                frame = frame.replace("data:image/jpeg;base64,", "")
                sio.emit('stream', data={
                    "shape": {"w": 320, "h": 320},
                    "frame": frame,
                    "debug": self.process_debug(),
                    "log": {
                        "pitch": self.Pilot.params.sensors.pitch,
                        "roll": self.Pilot.params.sensors.roll,
                        "lat": self.Pilot.params.sensors.position.lat,
                        "lon": self.Pilot.params.sensors.position.lon,
                        "alt": self.Pilot.params.sensors.position.alt,
                        "h": self.Pilot.params.sensors.heading,
                        "v_m_s": self.Pilot.params.sensors.velocity_down_m_s
                    }
                })
                time.sleep(0)

        @sio.event
        def disconnect():
            self.Pilot.params.server.connected = False
            self.logger.log_debug("SERVER: disconnected")

        @sio.on("emergency")
        def emergency(data):
            self.emergency = True
            self.Pilot.params.stage.emergency_data = data
            self.Pilot.params.stage.emergency = True
            self.logger.log_debug("SERVER: emergency")

        @sio.on("update_config")
        def update_config():
            self.Pilot.logger.log_debug("SERVER: update config")

        @sio.on("ready")
        def ready(data):
            self.logger.log_debug("SERVER: ready")
            self.Pilot.params.route.home = Position(self.Pilot.params.sensors.position.lat, self.Pilot.params.sensors.position.lon, 2)
            self.Pilot.params.route.points = self.push_route_points(data["route"])
            self.Pilot.params.server.enable_camera = True
            if data["test_mode"]:
                if self.config.mode == "test":
                    self.Pilot.params.stage.test.id = data["test_mode"]
                    self.Pilot.params.server.enable_camera = data["enable_camera"]
                    self.Pilot.params.stage.ready = True
                else:
                    self.logger.log_debug("SERVER: can't perform a test, test mode is not enabled")
                    
            
            if False:
                # TODO non-test logic
                self.Pilot.params.stage.ready = True

        while not self.Pilot.params.server.connected:
            try:
                sio.connect(self.Pilot.config.server_url, transports="websocket")
                self.logger.log_debug("SERVER: socket established")
                self.Pilot.params.server.connected = True
                sio.wait()
            except Exception as e:
                self.Pilot.logger.log_debug("SERVER: failed to establish initial connnection to server")
                time.sleep(2)

    def push_route_points(self, route_points):
        if not route_points: return None
        points = []
        for point in route_points:
            alt = point[2] if len(point) == 3 else None
            points.append(Position(lat=point[0], lon=point[1], alt=alt))
        return points
