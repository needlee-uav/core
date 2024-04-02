import asyncio
import helpers as helpers
import json
import modules.route_handler as route_handler
import modules.sensors_handler as sensors_handler
import modules.camera_handler as camera_handler
import modules.offboard_handler as offboard_handler
import modules.stage_handler as stage_handler
import modules.logger as logger
import modules.server_handler as server_handler
import modules.takeoff_handler as takeoff_handler
import modules.emergency_handler as emergency_handler
import test_scenarios.test_scenarios_handler as test_scenarios_handler

#import modules.vision_handler as vision_handler

class Pilot:

    def __init__(self, Drone):
        self.Drone = Drone
        config_file = open('config.json')
        self.Config = json.load(config_file)
        config_file.close()
        self.ready = False
        self.enable_camera = False

        self.EmergencyHandler = emergency_handler.EmergencyHandler(Pilot=self)
        self.CameraHandler = camera_handler.CameraHandler(Config=self.Config, Pilot=self)
        self.SensorsHandler = sensors_handler.SensorsHandler()
        self.RouteHandler = route_handler.RouteHandler()
        self.StageHandler = stage_handler.StageHandler(Config=self.Config, RouteHandler=self.RouteHandler, EmergencyHandler=self.EmergencyHandler)
        self.ServerHandler = server_handler.ServerHandler(server_config=self.Config["server"], CameraHandler=self.CameraHandler, SensorsHandler=self.SensorsHandler, StageHandler=self.StageHandler, EmergencyHandler=self.EmergencyHandler, Pilot=self)
        self.StageHandler.ServerHandler = self.ServerHandler
        self.Logger = logger.Logger(self.ServerHandler)
        self.OffboardHandler = offboard_handler.OffboardHandler()
        self.TakeoffHandler = takeoff_handler.TakeoffHandler()
        #self.YoloHandler = vision_handler.YoloHandler(CameraHandler=self.CameraHandler)
        self.plug_logger()
        self.Logger.log_debug("LOGGER: log OK")
        self.Logger.log_debug("PILOT: modules OK")
        self.Logger.log_debug(f'MODE: {self.Config["mode"]}')
        # Async
        asyncio.ensure_future(self.CameraHandler.view_camera_video())
        asyncio.ensure_future(self.Logger.log(SensorsHandler=self.SensorsHandler))
        self.Logger.log_debug("PILOT: log info OK")
        asyncio.ensure_future(self.SensorsHandler.update_position(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_heading(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_pitch_roll(Drone=self.Drone))
        asyncio.ensure_future(self.SensorsHandler.update_vertical_velocity(Drone=self.Drone))
        self.Logger.log_debug("PILOT: sensors OK")
        self.ServerHandler.start_websocket()
        self.Logger.log_debug("PILOT: websocket start")
        asyncio.ensure_future(self.StageHandler.handle_stages())
        self.Logger.log_debug("PILOT: stage OK")
        asyncio.ensure_future(self.RouteHandler.update_target_point(Drone=self.Drone, SensorsHandler=self.SensorsHandler, StageHandler=self.StageHandler))
        self.Logger.log_debug("PILOT: route OK")

        if self.Config["mode"] == "main":
            pass
        elif self.Config["mode"] == "test":
            self.TestScenariosHandler = test_scenarios_handler.TestScenariosHandler()
            self.TestScenariosHandler.Logger = self.Logger
            asyncio.ensure_future(self.TestScenariosHandler.handle_scenarios(ServerHandler=self.ServerHandler, StageHandler=self.StageHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone, TakeoffHandler=self.TakeoffHandler))
            self.Logger.log_debug("PILOT: test OK")
        elif self.Config["mode"] == "sim":
            asyncio.ensure_future(self.TakeoffHandler.soft_takeoff(StageHandler=self.StageHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
            self.Logger.log_debug("PILOT: takeoff OK")

    def plug_logger(self):
        self.OffboardHandler.Logger = self.Logger
        self.RouteHandler.Logger = self.Logger
        self.ServerHandler.Logger = self.Logger
        self.StageHandler.Logger = self.Logger
        self.EmergencyHandler.Logger = self.Logger
    # def run_async_sim(self):
    #     asyncio.ensure_future(self.CameraHandler.view_camera_video())
    #     #asyncio.ensure_future(self.YoloHandler.detect(CameraHandler=self.SimCameraHandler, StageHandler=self.StageHandler))
    #     #print("YOLO: detect OK")
    #     asyncio.ensure_future(self.Logger.log(SensorsHandler=self.SensorsHandler))
    #     print("PILOT: log OK")
    #     asyncio.ensure_future(self.SensorsHandler.update_position(Drone=self.Drone))
    #     asyncio.ensure_future(self.SensorsHandler.update_heading(Drone=self.Drone))
    #     asyncio.ensure_future(self.SensorsHandler.update_pitch_roll(Drone=self.Drone))
    #     asyncio.ensure_future(self.SensorsHandler.update_vertical_velocity(Drone=self.Drone))
    #     print("PILOT: sensors OK")
    #     self.WebSocketHandler.start_websocket()
    #     print("PILOT: websocket start")
    #     asyncio.ensure_future(self.StageHandler.handle_stages())
    #     print("PILOT: stage OK")
    #     asyncio.ensure_future(self.RouteHandler.update_target_point(Drone=self.Drone, SensorsHandler=self.SensorsHandler, StageHandler=self.StageHandler))
    #     print("PILOT: route OK")

    #     #asyncio.ensure_future(self.VisionHandler.process_image(CameraHandler=self.CameraHandler, StageHandler=self.StageHandler))
    #     #print("PILOT: vision OK")
    #     #asyncio.ensure_future(self.OffboardHandler.handle_offboard(StageHandler=self.StageHandler, VisionHandler=self.VisionHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
    #     #print("PILOT: offboard OK")
    #     asyncio.ensure_future(self.TakeoffHandler.soft_takeoff(StageHandler=self.StageHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
    #     print("PILOT: takeoff OK")

    # def run_async_test(self):
    #     asyncio.ensure_future(self.Logger.log(SensorsHandler=self.SensorsHandler))
    #     print("PILOT: log OK")
    #     asyncio.ensure_future(self.SensorsHandler.update_position(Drone=self.Drone))
    #     asyncio.ensure_future(self.SensorsHandler.update_heading(Drone=self.Drone))
    #     asyncio.ensure_future(self.SensorsHandler.update_pitch_roll(Drone=self.Drone))
    #     asyncio.ensure_future(self.SensorsHandler.update_vertical_velocity(Drone=self.Drone))
    #     print("PILOT: sensors OK")
    #     asyncio.ensure_future(self.StageHandler.handle_stages())
    #     print("PILOT: stage OK")
    #     asyncio.ensure_future(self.TestScenariosHandler.handle_scenarios(ServerHandler=self.ServerHandler, StageHandler=self.StageHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))

    #     #asyncio.ensure_future(self.TakeoffHandler.soft_takeoff(StageHandler=self.StageHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
    #     #print("PILOT: takeoff waiting OK")

    #     #asyncio.ensure_future(self.CameraTestScreen.show_frame(CameraHandler=self.CameraHandler))

    #     #print("PILOT: camera OK")
    #     #asyncio.ensure_future(self.VisionHandler.process_image(CameraHandler=self.CameraHandler, StageHandler=self.StageHandler))
    #     #print("PILOT: vision OK")
    #     #asyncio.ensure_future(self.OffboardHandler.handle_offboard(StageHandler=self.StageHandler, VisionHandler=self.VisionHandler, SensorsHandler=self.SensorsHandler, Drone=self.Drone))
    #     #print("PILOT: offboard OK")

    # def run_async_main(self):
    #     asyncio.ensure_future(self.YoloHandler.detect(CameraHandler=self.CameraHandler))
    #     print("YOLO: detect OK")
    #     pass
