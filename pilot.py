import asyncio
import helpers as helpers
import json
import modules.route_handler as route_handler
import modules.sensors_handler as sensors_handler
import modules.camera_handler as camera_handler
import modules.vision_handler as vision_handler
import modules.offboard_handler as offboard_handler
import modules.stage_handler as stage_handler
import modules.logger as logger
import modules.server_handler as server_handler
import modules.takeoff_handler as takeoff_handler
from mavsdk.offboard import (VelocityBodyYawspeed, VelocityNedYaw)

class Pilot:
    
    def __init__(self, Drone):
        self.Drone = Drone
        config_file = open('config.json')
        self.Config = json.load(config_file)
        config_file.close()
        self.ready = False

        # Modules
        self.TakeoffHandler = takeoff_handler.TakeoffHandler()
        self.ServerHandler = server_handler.ServerHandler(server_config=self.Config["server"])
        self.Logger = logger.Logger()
        self.RouteHandler = route_handler.RouteHandler()
        self.SensorsHandler = sensors_handler.SensorsHandler()
        self.CameraHandler = camera_handler.CameraHandler(Config=self.Config)
        self.VisionHandler = vision_handler.VisionHandler(Config=self.Config)
        self.OffboardHandler = offboard_handler.OffboardHandler()
        self.StageHandler = stage_handler.StageHandler(Config=self.Config, RouteHandler=self.RouteHandler)
        
        self.ensure_features()
        
    def ensure_features(self):
        asyncio.ensure_future(self.Logger.log(SensorsHandler=self.SensorsHandler))
        print("PILOT: log OK")
        asyncio.ensure_future(self.SensorsHandler.update_position(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_heading(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_pitch_roll(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_vertical_velocity(Drone=self.Drone))
        print("PILOT: sensors OK")
        asyncio.ensure_future(self.StageHandler.handle_stages(ServerHandler=self.ServerHandler))
        print("PILOT: stage OK")
        asyncio.ensure_future(self.ServerHandler.handle_ready(SensorsHandler=self.SensorsHandler))
        print("PILOT: prearm OK")  
        asyncio.ensure_future(self.TakeoffHandler.soft_takeoff(StageHandler=self.StageHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
        print("PILOT: takeoff waiting OK")
        
        #asyncio.ensure_future(self.CameraHandler.read_sim_image())
        #print("PILOT: camera OK")
        #asyncio.ensure_future(self.VisionHandler.process_image(CameraHandler=self.CameraHandler, StageHandler=self.StageHandler))
        #print("PILOT: vision OK")
        #asyncio.ensure_future(self.OffboardHandler.handle_offboard(StageHandler=self.StageHandler, VisionHandler=self.VisionHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
        #print("PILOT: offboard OK")

    