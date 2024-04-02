import asyncio, datetime
from mavsdk.offboard import (Attitude, VelocityBodyYawspeed)

class OffboardCommandsScenario:
    Logger = None
    def __init__(self):
        pass

    async def run(self, Logger, StageHandler, SensorsHandler, Drone, TakeoffHandler):
        self.Logger = Logger
        self.Logger.log_debug("TEST: Soft takeoff scenario")
        while StageHandler.stage != 0:
            await asyncio.sleep(0.1)
        self.Logger.log_debug("TEST: ready")
        asyncio.ensure_future(self.kill_on_takeoff_shake(StageHandler=StageHandler, SensorsHandler=SensorsHandler, Drone=Drone))

        self.Logger.log_debug("TAKEOFF: starting offboard")
        await Drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.0))
        await Drone.offboard.start()
        await asyncio.sleep(2)
        self.Logger.log_debug("TAKEOFF: offboard OK")
        self.Logger.log_debug("-- Arming")
        await Drone.action.arm()
        self.Logger.log_debug("TAKEOFF: arm OK")

        throttle = 0
        while SensorsHandler.velocity_down_m_s == 0:
            if throttle < -0.7:
                self.Logger.log_debug("TAKEOFF: throttle to high! KILL")
                await Drone.action.kill()
                break
            throttle = round(throttle - 0.1, 1)
            await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, throttle, 0.0))

            self.Logger.log_debug(f"throttle: {throttle}")
            await asyncio.sleep(2)
        start_time = datetime.datetime.now()
        while SensorsHandler.rel_alt < 4:
            diff = int(str(datetime.datetime.now() - start_time).split('.')[0].split(":")[2])
            if diff > 20: break
            self.Logger.log_debug(f"seconds: {diff}")
            self.Logger.log_debug(f"velocity: {SensorsHandler.velocity_down_m_s}")
            self.Logger.log_debug(f"altitude: {SensorsHandler.rel_alt}")
            await asyncio.sleep(1)

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
