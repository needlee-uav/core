import asyncio
from mavsdk.offboard import VelocityBodyYawspeed

class TakeoffHandler:
    in_air = False
    def __init__(self):
        pass

    async def soft_takeoff(self, StageHandler, SensorsHandler, Drone):
        while StageHandler.stage != 0:
            await asyncio.sleep(0.1)
        print("ready")
        asyncio.ensure_future(self.kill_on_takeoff_shake(StageHandler=StageHandler, SensorsHandler=SensorsHandler, Drone=Drone))

        print("TAKEOFF: starting offboard")
        await Drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await Drone.offboard.start()
        await asyncio.sleep(2)
        print("TAKEOFF: offboard OK")
        print("-- Arming")
        await Drone.action.arm()
        print("TAKEOFF: arm OK")

        min_down_m_s = 0
        while SensorsHandler.velocity_down_m_s == 0:
            if min_down_m_s < -0.7:
                print("TAKEOFF: down_m_s to high! KILL")
                await Drone.action.kill()
                break
            min_down_m_s = round(min_down_m_s - 0.1, 1)
            await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, min_down_m_s, 0.0))
            print(f"min down_m_s: {min_down_m_s}")
            await asyncio.sleep(2)

        down_m_s = min_down_m_s
        while SensorsHandler.rel_alt < 2.0:
            if down_m_s < -0.7: break
            down_m_s = round(down_m_s - 0.01, 2)
            await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, down_m_s, 0.0))
            print(f"down_m_s: {down_m_s}")
            await asyncio.sleep(0.4)

        print(f"down_m_s: {SensorsHandler.velocity_down_m_s}")
        await Drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        StageHandler.in_air = True


    async def kill_on_takeoff_shake(self, StageHandler, SensorsHandler, Drone):
        while StageHandler.stage == 0:
            if (abs(SensorsHandler.pitch) > 5 or abs(SensorsHandler.roll) > 5):
                print("TAKEOFF: shake! KILL")
                await Drone.action.kill()
            await asyncio.sleep(0.05)
