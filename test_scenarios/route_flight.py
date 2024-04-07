import asyncio

class RouteFlightScenario:
    def __init__(self, Pilot):
        self.Pilot = Pilot

    async def run(self):
        self.Pilot.Logger.log_debug("TEST: Route flight scenario")
        self.Pilot.params.stage.offboard_mode = True
        self.Pilot.params.stage.name = "ROUTE"
        while not self.Pilot.params.route.route_finished:
            await asyncio.sleep(1)
        self.Pilot.Logger.log_debug("DRONE: landing")
        await self.Pilot.Drone.action.land()
        await asyncio.sleep(10)
