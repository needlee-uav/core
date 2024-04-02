import asyncio
from mavsdk.offboard import (Attitude, VelocityBodyYawspeed)

class RouteFlightScenario:
    def __init__(self):
        pass

    async def run(self, Logger, StageHandler, SensorsHandler, Drone, TakeoffHandler):
        Logger.log_debug("TEST: Route flight scenario")
        asyncio.ensure_future(TakeoffHandler.soft_takeoff(StageHandler=StageHandler, SensorsHandler=SensorsHandler, Drone=Drone))
