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
from main import OffboardAlgorithm, Position

@dataclass
class Test():
    run: bool = False
    id: int = 0

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
    point_reached: bool = False
    point_i: int = 0
    points: list[Position] = None
    target_point: Position = None
    checkpoint: Position = None
    home: Position = None

@dataclass
class Offboard:
    algo: OffboardAlgorithm = None
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
        self.OffboardHandler = offboard_handler.OffboardHandler(Pilot=self)
        self.RouteHandler = route_handler.RouteHandler(Pilot=self)
        # self.YoloHandler = vision_handler.YoloHandler(CameraHandler=self.CameraHandler)
        if config.test_mode:
            self.params.stage.test.run = True
            self.TestScenariosHandler = test_scenarios_handler.TestScenariosHandler(Pilot=self)

        asyncio.ensure_future(self.monitor())


    async def monitor(self):
        while True:
            # print(self.params.stage)
            await asyncio.sleep(1)
