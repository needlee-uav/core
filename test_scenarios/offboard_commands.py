import asyncio
from main import OffboardAlgorithm, OffboardComand

class OffboardCommandsScenario:
    Logger = None
    def __init__(self, Pilot):
        self.Pilot = Pilot

    async def run(self):
        self.Pilot.Logger.log_debug("TEST: Offboard commands scenario")
        self.Pilot.params.offboard.algo = OffboardAlgorithm()
        self.Pilot.params.offboard.algo.commands = [
            OffboardComand(6, 0, 0, -0.3, 0),
            OffboardComand(10, 1, 0, 0, 0),
            OffboardComand(21, 0, 0, 0, -10),
            OffboardComand(10, 0, 0.5, 0, 0),
            OffboardComand(5, 0, 0, 0.5, 0)
        ]
        self.Pilot.params.stage.offboard_mode = True
        while self.Pilot.params.stage.offboard_mode:
            await asyncio.sleep(1)
        self.Pilot.Logger.log_debug("DRONE: landing")
        await self.Pilot.Drone.action.land()
        await asyncio.sleep(10)
