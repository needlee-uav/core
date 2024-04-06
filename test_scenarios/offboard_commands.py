import asyncio, datetime
from mavsdk.offboard import (Attitude, VelocityBodyYawspeed)

class OffboardCommandsScenario:
    Logger = None
    def __init__(self):
        pass

    async def run(self, Logger, StageHandler, SensorsHandler, Drone, TakeoffHandler):


        self.Logger.log_debug("test offboard")
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.3, 0.0, 0.0))
        await asyncio.sleep(10)
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, -0.3, 0.0, 0.0))
        await asyncio.sleep(10)
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.3, 0.0, 0.0, 0.0))
        await asyncio.sleep(20)
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(-0.3, 0.0, 0.0, 0.0))
        await asyncio.sleep(10)
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 7))
        await asyncio.sleep(10)
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, -7))
        await asyncio.sleep(10)
        self.Logger.log_debug("slow landing")
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.1, 0.0))
        await asyncio.sleep(10)
        self.Logger.log_debug("land")
        await Drone.action.land()
        await asyncio.sleep(20)
        self.Logger.log_debug("kill")
        await Drone.action.kill()

    async def kill_on_takeoff_shake(self, StageHandler, SensorsHandler, Drone):
        while StageHandler.stage == 0:
            if (abs(SensorsHandler.pitch) > 8 or abs(SensorsHandler.roll) > 8):
                self.Logger.log_debug("TAKEOFF: shake! KILL")
                await Drone.action.kill()
            await asyncio.sleep(0.05)
