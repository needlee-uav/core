import asyncio


class SoftTakeoffScenario:
    def __init__(self, Pilot):
        self.Pilot = Pilot

    async def run(self):
        self.Pilot.Logger.log_debug("TEST: Soft takeoff scenario")
        await asyncio.sleep(5)
        self.Pilot.Logger.log_debug("DRONE: landing")
        await self.Pilot.Drone.action.land()
        await asyncio.sleep(10)
