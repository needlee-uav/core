import asyncio
import mission_planner
class StageHandler:
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
        "FAILSAFE": 3
    }

    def __init__(self, Config, RouteHandler):
        config = Config["mission"]
        self.RouteHandler = RouteHandler
        self.home = config["home"]
        self.route_points = mission_planner.build_mission(self.home, config["target_area"], config["offset"])
        RouteHandler.route = self.route_points
        RouteHandler.target_point = self.route_points[0]
        RouteHandler.home = self.home
        self.ServerHandler = None

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
            if self.stage == None:
                self.switch_stage(stage="PREARM")
            elif self.ServerHandler.ready and self.stage == -1:
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
            print(f"STAGE: {stage}")
    
                   
