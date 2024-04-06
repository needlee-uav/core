import asyncio
import helpers as helpers
from dataclasses import dataclass, field
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

@dataclass
class Position:
    lat: float
    lon: float
    alt: float
    def __init__(self, lat, lon, alt):
        self.lat = lat
        self.lon = lon
        self.alt = alt if alt else None

@dataclass
class Test():
    run: bool = False
    name: str = ""

@dataclass
class Stage:
    test: Test = Test()
    ready: bool = False
    in_air: bool = False
    emergency: bool = False
    emergency_data: dict = field(default_factory=dict)
    name: str = "PREARM"
    offboard_mode: bool = False

@dataclass
class Sensors:
    ready: bool = False
    position: Position = Position(0.0, 0.0, 0.0)
    heading: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0
    velocity_down_m_s: float = 0.0

@dataclass
class Server:
    connected: bool = False
    enable_camera: bool = False

@dataclass
class Route:
    point_i: int = 0
    route: list = field(default_factory=list)
    target_point: Position = None
    checkpoint: Position = None
    home: Position = None

@dataclass
class Offboard:
    grid_yaw: bool = False
    target_coords: Position = None
    yaw_diff: float = 0.0
    distance: float = 0.0

@dataclass
class Target:
    target_coords: Position = None
    target_distance: float = 0.0
    confidence: float = 0.0
    target_detected: bool = False
    target_captured: bool = False


@dataclass
class Params:
    img: list = field(default_factory=list)
    debug_log: list = field(default_factory=list)
    stage: Stage = Stage()
    sensors: Sensors = Sensors()
    server: Server = Server()
    route: Route = Route()
    offboard: Offboard = Offboard()
    target: Target = Target()

class Pilot:
    def __init__(self, Drone, config):
        self.Drone = Drone
        self.params = Params()
        self.config = config

        # Essential
        self.Logger = logger.Logger(Pilot=self)
        self.SensorsHandler = sensors_handler.SensorsHandler(Pilot=self)
        self.EmergencyHandler = emergency_handler.EmergencyHandler(Pilot=self)
        self.CameraHandler = camera_handler.CameraHandler(Pilot=self)
        if not config.serverless: self.ServerHandler = server_handler.ServerHandler(Pilot=self)
        self.StageHandler = stage_handler.StageHandler(Pilot=self)
        self.TakeoffHandler = takeoff_handler.TakeoffHandler(Pilot=self)
        # self.RouteHandler = route_handler.RouteHandler(self=Pilot)
        # self.OffboardHandler = offboard_handler.OffboardHandler(Pilot=self)
        # self.YoloHandler = vision_handler.YoloHandler(CameraHandler=self.CameraHandler)
        asyncio.ensure_future(self.monitor())

        return



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
    async def monitor(self):
        while True:
            # print(self.params.stage)
            await asyncio.sleep(1)
