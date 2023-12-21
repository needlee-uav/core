import asyncio
import mission_planner
class StageHandler:
    target_detected = False
    target_captured = False
    offboard_mode = False
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
        self.grid_yaw = config["grid_yaw"]
        self.grid_step = config["grid_step"]
        self.min_relative_altitude = config["min_relative_altitude"]
        self.home = config["home"]
        self.route_points = mission_planner.build_mission(self.home, config["target_area"], config["offset"])
        RouteHandler.route = self.route_points
        RouteHandler.target_point = self.route_points[0]
        RouteHandler.home = self.home

    
    async def handle_stages(self, ServerHandler):
        while True:
            if self.stage == None:
                self.switch_stage(stage="PREARM")
            elif ServerHandler.ready and self.stage == -1:
                self.switch_stage(stage="TAKEOFF")
            elif self.stage == -1:
                pass
            #elif not self.target_detected and self.stage != 1:
            #    self.switch_stage(stage="ROUTE")
            #elif (self.target_detected and self.stage == 1):
            #    self.switch_stage(stage="CAPTURE")
            await asyncio.sleep(0.05)
    
    def switch_stage(self, stage):
        if stage in self.stages:
            self.stage = self.stages[stage]
            print(f"STAGE: {stage}")
    
                   
