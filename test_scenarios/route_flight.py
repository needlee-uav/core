import asyncio
from main import OffboardAlgorithm, OffboardComand

class RouteFlightScenario:
    def __init__(self, Pilot):
        self.Pilot = Pilot


    async def run(self):
        self.Pilot.Logger.log_debug("TEST: Route flight scenario")
        self.Pilot.params.offboard.algo = OffboardAlgorithm()
        self.Pilot.params.offboard.algo.commands = [
            OffboardComand(10, 0, 0, -0.5, 0)
        ]
        self.Pilot.params.stage.offboard_mode = True
        while self.Pilot.params.stage.offboard_mode:
            await asyncio.sleep(1)

        self.Pilot.params.stage.name = "ROUTE"
