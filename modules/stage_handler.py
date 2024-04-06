import asyncio
import mission_planner
class StageHandler:
    Logger = None
    target_detected = False
    target_captured = False
    offboard_mode = False
    in_air = False
    stage = None
    stages = {
        "PREARM": -1,
        "TAKEOFF": 0,
        "ROUTE": 1,
        "CAPTURE": 2,
        "EMERGENCY": 3
    }

    async def __init__(self, Pilot):
        self.Pilot = Pilot
        # self.config = Pilot.config["mission"]
        self.RouteHandler = Pilot.RouteHandler
        self.EmergencyHandler = Pilot.EmergencyHandler
        self.ServerHandler = None
        while Pilot.SensorsHandler.position["lat"] == 0.0:
            await asyncio.sleep(1)
        self.home = Pilot.SensorsHandler.position

        # Build route
        # self.home = None
        # self.route_points = mission_planner.build_mission(self.home, config["target_area"], config["offset"])
        # self.RouteHandler.route = self.route_points
        # self.RouteHandler.target_point = self.route_points[0]
        # self.RouteHandler.home = self.home


    def rebuild_route(self, Config):
        self.home= {
            "lat": Config["home"][0],
            "lon": Config["home"][1]
        }
        self.route_points = mission_planner.build_raw_route(Config["home"], Config["route"])
        self.RouteHandler.route = self.route_points
        self.RouteHandler.target_point = self.route_points[0]
        self.RouteHandler.home = self.home

    async def handle_stages(self):
        while True:
            if self.Pilot.EmergencyHandler.emergency:
                self.switch_stage(stage="EMERGENCY")
                return
            elif self.stage == None:
                self.switch_stage(stage="PREARM")
            elif self.Pilot.ServerHandler.ready and self.stage == -1:
                self.switch_stage(stage="TAKEOFF")
            elif self.stage == 0 and self.in_air == True:
                self.switch_stage(stage="ROUTE")
            elif self.stage == -1 or self.stage == 0:
                pass
            elif not self.target_detected and self.stage != 1:
                self.switch_stage(stage="ROUTE")
            elif (self.target_detected and self.stage == 1):
               self.switch_stage(stage="CAPTURE")
            await asyncio.sleep(0.05)

    def switch_stage(self, stage):
        if stage in self.stages:
            self.stage = self.stages[stage]
            self.Pilot.Logger.log_debug(f"STAGE: {stage}")
