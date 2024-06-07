import asyncio
import numpy as np
import modules.route_handler as route_handler
import modules.sensors_handler as sensors_handler
import modules.offboard_handler as offboard_handler
import modules.stage_handler as stage_handler
import modules.logger as logger
import modules.server_handler as server_handler
import modules.takeoff_handler as takeoff_handler
import modules.emergency_handler as emergency_handler
import test_scenarios.test_scenarios_handler as test_scenarios_handler
from data_classes import Params


class Pilot:
    def __init__(self, Drone, config, camera):
        self.Drone = Drone
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
        else:
            self.SensorsHandler = sensors_handler.SensorsHandler(Pilot=self)
            self.EmergencyHandler = emergency_handler.EmergencyHandler(Pilot=self)
            self.StageHandler = stage_handler.StageHandler(Pilot=self)
            self.TakeoffHandler = takeoff_handler.TakeoffHandler(Pilot=self)
            self.OffboardHandler = offboard_handler.OffboardHandler(Pilot=self)
            self.RouteHandler = route_handler.RouteHandler(Pilot=self)
            if config.test_mode:
                self.params.stage.test.run = True
                self.TestScenariosHandler = test_scenarios_handler.TestScenariosHandler(Pilot=self)
                
    async def monitor(self, camera):
        while True:
            self.params.img = camera.img
            self.params.box = camera.box
            self.params.target.confidence = camera.confidence
            await asyncio.sleep(0.01)

    def run_vision_test(self):
        self.TestScenariosHandler = test_scenarios_handler.TestScenariosHandler(Pilot=self)
        self.params.sensors.position.lat = 41.6938
        self.params.sensors.position.lon = 44.8015
        self.params.sensors.position.alt = 0.0
        self.params.box=[0,0,0,0]
        self.params.sensors.ready = True
