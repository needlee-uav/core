import asyncio
from mavsdk.offboard import VelocityBodyYawspeed

class TakeoffHandler:
    def __init__(self, Pilot):
        self.Pilot = Pilot
        asyncio.ensure_future(self.soft_takeoff())

    async def soft_takeoff(self):
        while self.Pilot.params.stage.name != "TAKEOFF":
            await asyncio.sleep(0.1)
        print("ready")
        asyncio.ensure_future(self.kill_on_takeoff_shake())

        print("TAKEOFF: starting offboard")
        await self.Pilot.Drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await self.Pilot.Drone.offboard.start()
        await asyncio.sleep(2)
        print("TAKEOFF: offboard OK")
        print("-- Arming")
        await self.Pilot.Drone.action.arm()
        print("TAKEOFF: arm OK")

        min_down_m_s = 0
        while self.Pilot.params.sensors.velocity_down_m_s == 0:
            if min_down_m_s < -0.7:
                print("TAKEOFF: down_m_s to high! KILL")
                await self.Pilot.Drone.action.kill()
                break
            min_down_m_s = round(min_down_m_s - 0.1, 1)
            await self.Pilot.Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, min_down_m_s, 0.0))
            print(f"min down_m_s: {min_down_m_s}")
            await asyncio.sleep(2)

        down_m_s = min_down_m_s
        while self.Pilot.params.sensors.position.alt < 2.0:
            if down_m_s < -0.7: break
            down_m_s = round(down_m_s - 0.01, 2)
            await self.Pilot.Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, down_m_s, 0.0))
            print(f"down_m_s: {down_m_s}")
            await asyncio.sleep(0.4)

        print(f"down_m_s: {self.Pilot.params.sensors.velocity_down_m_s}")
        await self.Pilot.Drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        self.Pilot.params.stage.in_air = True


    async def kill_on_takeoff_shake(self):
        while self.Pilot.params.stage.name == "TAKEOFF":
            if (abs(self.Pilot.params.sensors.pitch) > 5 or abs(self.Pilot.params.sensors.roll) > 5):
                print("TAKEOFF: shake! KILL")
                await self.Pilot.Drone.action.kill()
            await asyncio.sleep(0.05)
