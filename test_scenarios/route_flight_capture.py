import asyncio

class RouteFlightCaptureScenario:
    def __init__(self, Pilot):
        self.Pilot = Pilot

    async def run(self):
        self.Pilot.Logger.log_debug("TEST: Capture scenario")
        # self.Pilot.params.stage.offboard_mode = True
        self.Pilot.StageHandler.switch_stage(stage="ROUTE")
        while not self.Pilot.params.route.route_finished:
            await asyncio.sleep(1)
        self.Pilot.Logger.log_debug("DRONE: landing")
        await self.Pilot.Drone.action.land()
        await asyncio.sleep(10)
