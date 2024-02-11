import asyncio
from mavsdk.offboard import VelocityBodyYawspeed

class TakeoffHandler:
    in_air = False
    def __init__(self):
        pass

    async def soft_takeoff(self, StageHandler, SensorsHandler, Drone):
        while StageHandler.stage != 0:
            await asyncio.sleep(0.1)
        asyncio.ensure_future(self.kill_on_takeoff_shake(StageHandler=StageHandler, SensorsHandler=SensorsHandler, Drone=Drone))
        print("TAKEOFF: arming")
        await Drone.action.arm()
        print("TAKEOFF: arm OK")
        print("TAKEOFF: starting offboard")
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await Drone.offboard.start()
        print("TAKEOFF: offboard OK")

        throttle = 0
        while SensorsHandler.velocity_down_m_s == 0:
            print(SensorsHandler.rel_alt)
            if throttle < -0.9:
                print("TAKEOFF: throttle to high! KILL")
                await Drone.action.kill()
                break
            throttle = round(throttle - 0.1, 1)
            await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, throttle, 0.0))
            print(f"throttle: {throttle}")
            await asyncio.sleep(2)
        
        await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, throttle - 0.2, 0.0))
        await asyncio.sleep(10)
        await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        StageHandler.in_air = True


    async def kill_on_takeoff_shake(self, StageHandler, SensorsHandler, Drone):
        while StageHandler.stage == 0:
            if (abs(SensorsHandler.pitch) > 5 or abs(SensorsHandler.roll) > 5):
                print("TAKEOFF: shake! KILL")
                await Drone.action.kill()
            await asyncio.sleep(0.05)