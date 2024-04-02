import asyncio
from mavsdk.offboard import (VelocityBodyYawspeed)
class EmergencyHandler:
    emergency = False
    Logger = None
    def __init__(self, Pilot):
        self.Pilot = Pilot
        asyncio.ensure_future(self.handle_emergency())

    def pass_emergency_data(self, data):
        self.data = data
        self.emergency = True

    async def handle_emergency(self):
        while not self.emergency:
            await asyncio.sleep(0.05)
        await self.emergencyLanding()

    async def emergencyLanding(self):
        self.Logger.log_debug("EMERGENCY: landing")
        await self.Pilot.Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await self.Pilot.Drone.offboard.start()
        await self.Pilot.Drone.action.land()


    # async def log(self, SensorsHandler):
    #     while True:
    #         line = f"rel_alt:{SensorsHandler.rel_alt}; heading:{SensorsHandler.heading}; lat:{SensorsHandler.position['lat']}; lon:{SensorsHandler.position['lon']}"
    #         self.log_info(line)
    #         await asyncio.sleep(1)
