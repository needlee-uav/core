import asyncio
from mavsdk.offboard import (Attitude, VelocityBodyYawspeed)

class RouteFlightScenario:
    def __init__(self):
        pass
    
    async def run(self, StageHandler, SensorsHandler, Drone, TakeoffHandler):
        print("TEST: Route flight scenario")
        asyncio.ensure_future(TakeoffHandler.soft_takeoff(StageHandler=StageHandler, SensorsHandler=SensorsHandler, Drone=Drone))