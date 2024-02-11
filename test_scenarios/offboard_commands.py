import asyncio, datetime
from mavsdk.offboard import (Attitude, VelocityBodyYawspeed)

class OffboardCommandsScenario:

    def __init__(self):
        pass

    async def run(self, StageHandler, SensorsHandler, Drone):
        print("TEST: Soft takeoff scenario")
        while StageHandler.stage != 0:
            await asyncio.sleep(0.1)
        print("ready")
        asyncio.ensure_future(self.kill_on_takeoff_shake(StageHandler=StageHandler, SensorsHandler=SensorsHandler, Drone=Drone))
        
        print("TAKEOFF: starting offboard")
        await Drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.0))
        await Drone.offboard.start()
        await asyncio.sleep(2)
        print("TAKEOFF: offboard OK")
        print("-- Arming")
        await Drone.action.arm()
        print("TAKEOFF: arm OK")

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
        start_time = datetime.datetime.now()
        while SensorsHandler.rel_alt < 4:
            diff = int(str(datetime.datetime.now() - start_time).split('.')[0].split(":")[2])
            if diff > 20: break
            print(f"seconds: {diff}")
            print(f"velocity: {SensorsHandler.velocity_down_m_s}")
            print(f"altitude: {SensorsHandler.rel_alt}")
            await asyncio.sleep(1)
        
        print("test offboard")
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
        print("slow landing")
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.1, 0.0))
        await asyncio.sleep(10)
        print("land")
        await Drone.action.land()
        await asyncio.sleep(20)
        print("kill")
        await Drone.action.kill()

    async def kill_on_takeoff_shake(self, StageHandler, SensorsHandler, Drone):
        while StageHandler.stage == 0:
            if (abs(SensorsHandler.pitch) > 8 or abs(SensorsHandler.roll) > 8):
                print("TAKEOFF: shake! KILL")
                await Drone.action.kill()
            await asyncio.sleep(0.05)