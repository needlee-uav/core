import asyncio
from mavsdk.offboard import VelocityBodyYawspeed

class TakeoffHandler:

    def __init__(self):
        pass

    async def soft_takeoff(self, StageHandler, SensorsHandler, Drone):
        while StageHandler.stage != 0:
            await asyncio.sleep(0.1)
        print("ready")
        asyncio.ensure_future(self.kill_on_takeoff_shake(StageHandler=StageHandler, SensorsHandler=SensorsHandler, Drone=Drone))
        print("-- Arming")
        await Drone.action.arm()
        print("TAKEOFF: arm OK")
        print("TAKEOFF: starting offboard")
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await Drone.offboard.start()
        print("TAKEOFF: offboard OK")

        throttle = 0
        while SensorsHandler.velocity_down_m_s == 0:
            if throttle < -0.7:
                print("TAKEOFF: throttle to high! KILL")
                await Drone.action.kill()
                break
            throttle = round(throttle - 0.1, 1)
            await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, throttle, 0.0))
            print(f"throttle: {throttle}")
            await asyncio.sleep(2)
        
        print(f"velocity: {SensorsHandler.velocity_down_m_s}")
        await asyncio.sleep(5)
        print("slow landing")
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.1, 0.0))
        await asyncio.sleep(10)
        print("sim error")
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(1.0, 0.0, 0.0, 0.0))
        print("land")
        await Drone.action.land()
        print("kill")
        await Drone.action.kill()


    async def kill_on_takeoff_shake(self, StageHandler, SensorsHandler, Drone):
        while StageHandler.stage == 0:
            if (abs(SensorsHandler.pitch) > 5 or abs(SensorsHandler.roll) > 5):
                print("TAKEOFF: shake! KILL")
                await Drone.action.kill()
            await asyncio.sleep(0.05)