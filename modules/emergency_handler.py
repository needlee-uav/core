import asyncio
from mavsdk.offboard import (VelocityBodyYawspeed)
class EmergencyHandler:
    def __init__(self, Pilot):
        self.Pilot = Pilot
        asyncio.ensure_future(self.handle_emergency())
        Pilot.Logger.log_debug("EMERGENCY: ready")


    async def handle_emergency(self):
        while not self.Pilot.params.stage.emergency:
            await asyncio.sleep(0.05)
        self.Pilot.Logger.log_debug("EMERGENCY: triggered")
        await self.emergencyLanding(self.Pilot.params.stage.emergency_data)

    async def emergencyLanding(self, data):
        self.Pilot.Logger.log_debug("EMERGENCY: landing")
        self.Pilot.Logger.log_debug(f"EMERGENCY: {data}")
        await self.Pilot.Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await self.Pilot.Drone.offboard.start()
        await self.Pilot.Drone.action.land()
