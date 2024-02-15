import asyncio
import helpers as helpers
import json
import time
import modules.route_handler as route_handler
import modules.sensors_handler as sensors_handler
import modules.camera_handler as camera_handler
#import modules.vision_handler as vision_handler
import modules.offboard_handler as offboard_handler
import modules.stage_handler as stage_handler
import modules.logger as logger
import modules.server_handler as server_handler
import modules.takeoff_handler as takeoff_handler
import test_scenarios.test_scenarios_handler as test_scenarios_handler

class Pilot:
    
    def __init__(self, Drone):
        self.Drone = Drone
        config_file = open('config.json')
        self.Config = json.load(config_file)
        config_file.close()
        self.ready = False

        print(f'MODE: {self.Config["mode"]}')
        # Modules
        self.SimCameraHandler = camera_handler.SimCameraHandler(Config=self.Config)
        self.SensorsHandler = sensors_handler.SensorsHandler()
        self.RouteHandler = route_handler.RouteHandler()
        self.StageHandler = stage_handler.StageHandler(Config=self.Config, RouteHandler=self.RouteHandler)
        self.WebSocketHandler = server_handler.WebSocketHandler(server_config=self.Config["server"], CameraHandler=self.SimCameraHandler, SensorsHandler=self.SensorsHandler, StageHandler=self.StageHandler)
        self.StageHandler.ServerHandler = self.WebSocketHandler
        self.Logger = logger.Logger()
        self.OffboardHandler = offboard_handler.OffboardHandler()
        #self.YoloHandler = vision_handler.YoloHandler(CameraHandler=self.CameraHandler)
        print("PILOT: modules OK")
        
        # Async
        asyncio.ensure_future(self.SimCameraHandler.view_camera_video())
        asyncio.ensure_future(self.Logger.log(SensorsHandler=self.SensorsHandler))
        print("PILOT: log OK")
        asyncio.ensure_future(self.SensorsHandler.update_position(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_heading(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_pitch_roll(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_vertical_velocity(Drone=self.Drone))
        print("PILOT: sensors OK")
        self.WebSocketHandler.start_websocket()
        print("PILOT: websocket start")
        asyncio.ensure_future(self.StageHandler.handle_stages())
        print("PILOT: stage OK")
        asyncio.ensure_future(self.RouteHandler.update_target_point(Drone=self.Drone, SensorsHandler=self.SensorsHandler, StageHandler=self.StageHandler))
        print("PILOT: route OK")

        if self.Config["mode"] == "main":
            pass
        elif self.Config["mode"] == "test":
            self.TestScenariosHandler = test_scenarios_handler.TestScenariosHandler()
            asyncio.ensure_future(self.TestScenariosHandler.handle_scenarios(ServerHandler=self.WebSocketHandler, StageHandler=self.StageHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
            print("PILOT: test OK")
        elif self.Config["mode"] == "sim":
            self.TakeoffHandler = takeoff_handler.TakeoffHandler()
            asyncio.ensure_future(self.TakeoffHandler.soft_takeoff(StageHandler=self.StageHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
            print("PILOT: takeoff OK")
    
    def run_async_sim(self):
        asyncio.ensure_future(self.SimCameraHandler.view_camera_video())
        #asyncio.ensure_future(self.YoloHandler.detect(CameraHandler=self.SimCameraHandler, StageHandler=self.StageHandler))
        #print("YOLO: detect OK")
        asyncio.ensure_future(self.Logger.log(SensorsHandler=self.SensorsHandler))
        print("PILOT: log OK")
        asyncio.ensure_future(self.SensorsHandler.update_position(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_heading(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_pitch_roll(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_vertical_velocity(Drone=self.Drone))
        print("PILOT: sensors OK")
        self.WebSocketHandler.start_websocket()
        print("PILOT: websocket start")
        asyncio.ensure_future(self.StageHandler.handle_stages())
        print("PILOT: stage OK")
        asyncio.ensure_future(self.RouteHandler.update_target_point(Drone=self.Drone, SensorsHandler=self.SensorsHandler, StageHandler=self.StageHandler))
        print("PILOT: route OK")
        
        #asyncio.ensure_future(self.VisionHandler.process_image(CameraHandler=self.CameraHandler, StageHandler=self.StageHandler))
        #print("PILOT: vision OK")
        #asyncio.ensure_future(self.OffboardHandler.handle_offboard(StageHandler=self.StageHandler, VisionHandler=self.VisionHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
        #print("PILOT: offboard OK")
        asyncio.ensure_future(self.TakeoffHandler.soft_takeoff(StageHandler=self.StageHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
        print("PILOT: takeoff OK")

    def run_async_test(self):
        asyncio.ensure_future(self.Logger.log(SensorsHandler=self.SensorsHandler))
        print("PILOT: log OK")
        asyncio.ensure_future(self.SensorsHandler.update_position(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_heading(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_pitch_roll(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_vertical_velocity(Drone=self.Drone))
        print("PILOT: sensors OK")
        asyncio.ensure_future(self.StageHandler.handle_stages())
        print("PILOT: stage OK")
        asyncio.ensure_future(self.TestScenariosHandler.handle_scenarios(ServerHandler=self.ServerHandler, StageHandler=self.StageHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))

        #asyncio.ensure_future(self.TakeoffHandler.soft_takeoff(StageHandler=self.StageHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
        #print("PILOT: takeoff waiting OK")
        
        #asyncio.ensure_future(self.CameraTestScreen.show_frame(CameraHandler=self.CameraHandler))

        #print("PILOT: camera OK")
        #asyncio.ensure_future(self.VisionHandler.process_image(CameraHandler=self.CameraHandler, StageHandler=self.StageHandler))
        #print("PILOT: vision OK")
        #asyncio.ensure_future(self.OffboardHandler.handle_offboard(StageHandler=self.StageHandler, VisionHandler=self.VisionHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
        #print("PILOT: offboard OK")

    def run_async_main(self):
        asyncio.ensure_future(self.YoloHandler.detect(CameraHandler=self.CameraHandler))
        print("YOLO: detect OK")
        pass