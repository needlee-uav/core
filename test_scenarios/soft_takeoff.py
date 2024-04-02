import asyncio
from mavsdk.offboard import (VelocityBodyYawspeed)

class SoftTakeoffScenario:
    Logger = None
    def __init__(self):
        pass

    async def run(self, Logger, StageHandler, SensorsHandler, Drone, TakeoffHandler):
        self.Logger = Logger
        self.Logger.log_debug("TEST: Soft takeoff scenario")
        while StageHandler.stage != 0:
            await asyncio.sleep(0.1)
        self.Logger.log_debug("Ready")
        asyncio.ensure_future(self.kill_on_takeoff_shake(StageHandler=StageHandler, SensorsHandler=SensorsHandler, Drone=Drone))

        self.Logger.log_debug("TAKEOFF: starting offboard")
        await Drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await Drone.offboard.start()
        await asyncio.sleep(2)
        self.Logger.log_debug("TAKEOFF: offboard OK")
        self.Logger.log_debug("-- Arming")
        await Drone.action.arm()
        self.Logger.log_debug("TAKEOFF: arm OK")

        min_down_m_s = 0
        while SensorsHandler.velocity_down_m_s == 0:
            if min_down_m_s < -0.7:
                self.Logger.log_debug("TAKEOFF: down_m_s to high! KILL")
                await Drone.action.kill()
                break
            min_down_m_s = round(min_down_m_s - 0.1, 1)
            await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, min_down_m_s, 0.0))
            self.Logger.log_debug(f"min down_m_s: {min_down_m_s}")
            await asyncio.sleep(2)

        down_m_s = min_down_m_s
        while SensorsHandler.rel_alt < 2.0:
            if down_m_s < -0.7: break
            down_m_s = round(down_m_s - 0.01, 2)
            await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, down_m_s, 0.0))
            self.Logger.log_debug(f"down_m_s: {down_m_s}")
            await asyncio.sleep(0.4)

        self.Logger.log_debug(f"down_m_s: {SensorsHandler.velocity_down_m_s}")
        await Drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await asyncio.sleep(5)
        self.Logger.log_debug("slow landing")
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.1, 0.0))
        await asyncio.sleep(10)
        self.Logger.log_debug("land")
        await Drone.action.land()
        await asyncio.sleep(10)
        self.Logger.log_debug("kill")
        await Drone.action.kill()

    async def kill_on_takeoff_shake(self, StageHandler, SensorsHandler, Drone):
        while StageHandler.stage == 0:
            if (abs(SensorsHandler.pitch) > 5 or abs(SensorsHandler.roll) > 5):
                self.Logger.log_debug("TAKEOFF: shake! KILL")
                await Drone.action.kill()
            await asyncio.sleep(0.05)
