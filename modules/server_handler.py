import requests
import asyncio
import socketio, time, datetime
import threading
import cv2
import base64

class WebSocketHandler:
    def __init__(self, server_config, CameraHandler, SensorsHandler):
        self.CameraHandler = CameraHandler
        self.SensorsHandler = SensorsHandler
        self.server_config = server_config

    def start_websocket(self):
        t = threading.Thread(target=self._handler)
        t.start()

    def _handler(self):
        sio = socketio.Client(engineio_logger=True)
        
        @sio.event
        def connect():
            print("CONNECTED!")
            sio.emit('move_map_to_vehicle', data={"lat": self.SensorsHandler.position["lat"], "lon": self.SensorsHandler.position["lon"], "alt": self.SensorsHandler.rel_alt, "h": self.SensorsHandler.heading})
        
            while True:
                time.sleep(0.1)
                img = cv2.resize(self.CameraHandler.image, (0,0), fx=0.5, fy=0.5)
                frame = cv2.imencode('.jpg', img)[1].tobytes()
                frame = base64.encodebytes(frame).decode("utf-8")
                frame = frame.replace("data:image/jpeg;base64,", "")
                sio.emit('stream', data={"frame": frame, "log": {"lat": self.SensorsHandler.position["lat"], "lon": self.SensorsHandler.position["lon"], "alt": self.SensorsHandler.rel_alt, "h": self.SensorsHandler.heading}})
                time.sleep(0)

        @sio.event
        def disconnect():
            print("DISCONNECTED")

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


class ServerHandler:
    def __init__(self, server_config):
        self.url = server_config['url']
        self.drone_id = server_config['drone_id']
        self.connected = False
        self.ready = False
        self.test_mode = None

    def make_handshake(self, data):
        i = 0
        while not self.connected and i < 5:
            i+=1
            url = f'{self.url}/handshake/{self.drone_id}/{data}'
            res = requests.get(url).text
            if res == 'success':
                self.connected = True
            time.sleep(1)
        if self.connected:
            print('SERVER: Vehicle connected')
        else:
            print('SERVER: Failed to connect')
    
    async def handle_ready(self, SensorsHandler):
        lat = SensorsHandler.position['lat']
        lon = SensorsHandler.position['lon']
        data = f'{lat}_{lon}_{SensorsHandler.heading}_{SensorsHandler.rel_alt}'
        self.make_handshake(data)
        while not self.ready:
            lat = SensorsHandler.position['lat']
            lon = SensorsHandler.position['lon']
            url = f'{self.url}/log/{self.drone_id}/{lat}_{lon}_{SensorsHandler.heading}_{SensorsHandler.rel_alt}'
            res = requests.get(url).text
            if "ready: 1" in res:
                self.parse_ready_res(res)
                print("SERVER: ready")
                self.ready = True
                return
            await asyncio.sleep(1)

    def parse_ready_res(self, res):
        self.test_mode = res.split('; ')[1].split(': ')[1]
        print(f'Test mode: {self.test_mode}')

    async def handle_log(self, SensorsHandler):
        while self.connected:
            lat = SensorsHandler.position['lat']
            lon = SensorsHandler.position['lon']
            url = f'{self.url}/log/{self.drone_id}/{lat}_{lon}_{SensorsHandler.heading}_{SensorsHandler.rel_alt}'
            res = requests.get(url).text
            await asyncio.sleep(1)
        # SOME EMERGENCY LOGIC
        return
    
