import asyncio
import numpy as np
import modules.logger as logger
import modules.server_handler as server_handler
from main import Position

#TODO fake params
class Test():
    run: bool = False
    id: int = 0

class Stage:
    test: Test = Test()
    ready: bool = False
    in_air: bool = False
    emergency: bool = False
    emergency_data: dict = None
    name = "PREARM"
    offboard_mode = False

class Sensors:
    ready = False
    position = Position(0.0, 0.0, 0.0)
    heading = 1
    pitch = 1
    roll = 1
    velocity_down_m_s = 1

class Server:
    connected = False
    enable_camera: bool = False

class Params:
    box = []
    img = []
    debug_log = []
    stage: Stage = Stage()
    sensors: Sensors = Sensors()
    server: Server = Server()
    
class Pilot:
    def __init__(self, config, camera):
        self.params = Params()
        self.config = config
        
        if config.vision == False: 
            self.params.img = np.zeros([320, 320, 3],dtype=np.uint8)
            self.params.img.fill(255)
        else:
            asyncio.ensure_future(self.monitor(camera=camera))
            
        self.Logger = logger.Logger(Pilot=self)
        if not config.serverless: self.ServerHandler = server_handler.ServerHandler(Pilot=self)

        if config.vision_test:
            self.run_vision_test()
        
                
    async def monitor(self, camera):
        while True:
            self.params.img = camera.img
            self.params.box = camera.box
            self.params.target.confidence = camera.confidence
            await asyncio.sleep(0.01)

    def run_vision_test(self):
        self.params.sensors.position.lat = 41.6938
        self.params.sensors.position.lon = 44.8015
        self.params.sensors.position.alt = 0.0
        self.params.box=[0,0,0,0]
        self.params.sensors.ready = True
