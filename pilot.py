import asyncio
import cv2 as cv
import numpy as np
from data_classes import Params
import modules.route_handler as route_handler
import modules.sensors_handler as sensors_handler
import modules.offboard_handler as offboard_handler
import modules.stage_handler as stage_handler
import modules.takeoff_handler as takeoff_handler
import test_scenarios.test_scenarios_handler as test_scenarios_handler


class Pilot:
    def __init__(self, drone, config, camera, logger, server, emergency):
        self.Drone = drone
        self.config = config
        self.camera = camera
        self.params = Params()
        self.Logger = logger
        self.Logger.sensors = self.params.sensors
        self.SensorsHandler = sensors_handler.SensorsHandler(Pilot=self)
        self.ServerHandler = server
        self.ServerHandler.Pilot = self
        self.EmergencyHandler = emergency
        self.EmergencyHandler.sensors = self.params.sensors

        if config.cameramode == "none": 
            self.params.img = np.zeros([320, 320, 3],dtype=np.uint8)
            self.params.img.fill(255)
        else:
            asyncio.ensure_future(self.monitor(camera=camera))

        self.StageHandler = stage_handler.StageHandler(Pilot=self)
        self.TakeoffHandler = takeoff_handler.TakeoffHandler(Pilot=self)
        self.OffboardHandler = offboard_handler.OffboardHandler(Pilot=self)
        # TODO
        # self.RouteHandler = route_handler.RouteHandler(Pilot=self)
        if config.mode == "test":
            self.params.stage.test.run = True
            self.TestScenariosHandler = test_scenarios_handler.TestScenariosHandler(Pilot=self)

    async def monitor(self, camera):
        while True:
            self.params.img = camera.frame
            self.params.box = camera.box
            self.params.target.confidence = camera.confidence
            await asyncio.sleep(0.01)#

    

    

