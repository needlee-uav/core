import asyncio
from mavsdk.offboard import VelocityBodyYawspeed

class TakeoffHandler:
    def __init__(self, Pilot):
        self.Pilot = Pilot
        self.takeoff_task = asyncio.ensure_future(self.soft_takeoff())
        asyncio.ensure_future(self.kill_on_takeoff_shake())
        asyncio.ensure_future(self.hold_takeoff_at_alt())

    async def arm_on_takeoff(self):
        self.Pilot.Logger.log_debug("TAKEOFF: start offboard")
        await self.Pilot.Drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await self.Pilot.Drone.offboard.start()
        await asyncio.sleep(2)
        self.Pilot.Logger.log_debug("TAKEOFF: offboard OK")
        self.Pilot.Logger.log_debug("TAKEOFF: arm")
        await self.Pilot.Drone.action.arm()
        self.Pilot.Logger.log_debug("TAKEOFF: arm OK")

    async def soft_takeoff(self):
        while self.Pilot.params.stage.name != "TAKEOFF":
            await asyncio.sleep(0.1)
        await self.arm_on_takeoff()
        down_m_s = 0
        while down_m_s > -0.6 and not self.Pilot.params.stage.in_air:
            down_m_s = round(down_m_s - 0.1, 1)
            if down_m_s <= -0.6:
                self.Pilot.Logger.log_debug("TAKEOFF: velocity to high! Land")
                await self.Pilot.Drone.action.land()
                break
            await self.Pilot.Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, down_m_s, 0.0))
            self.Pilot.Logger.log_debug(f"TAKEOFF: velocity {abs(down_m_s)}")
            await asyncio.sleep(10 * abs(down_m_s))

    async def hold_takeoff_at_alt(self):
        while self.Pilot.params.stage.name != "TAKEOFF":
            await asyncio.sleep(0.1)
        while self.Pilot.params.sensors.position.alt < 1.0:
            await asyncio.sleep(0.2)
        self.Pilot.params.stage.in_air = True
        self.Pilot.Logger.log_debug(f"TAKEOFF: 1 meter reached at velocity {self.Pilot.params.sensors.velocity_down_m_s}")
        await asyncio.sleep(0.2)
        await self.Pilot.Drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))


    async def kill_on_takeoff_shake(self):
        while self.Pilot.params.stage.name != "TAKEOFF":
            await asyncio.sleep(0.1)
        while self.Pilot.params.stage.name == "TAKEOFF":
            if (abs(self.Pilot.params.sensors.pitch) > 5 or abs(self.Pilot.params.sensors.roll) > 5):
                print("TAKEOFF: shake! KILL")
                await self.Pilot.Drone.action.kill()
            await asyncio.sleep(0.05)
