import asyncio
from mavsdk.offboard import (VelocityBodyYawspeed)
import datetime

class EmergencyHandler:
    def __init__(self, server, timeout, logger, drone, sensor_limits):
        self.sensor_limits = sensor_limits
        self.sensors = False
        self.server = server
        self.drone = drone
        if timeout:
            self.timeout = 0
            asyncio.ensure_future(self.handle_timeout(timeout))
        asyncio.ensure_future(self.handle_sensor_limits())
        asyncio.ensure_future(self.handle_server_emergency())

        self.logger = logger
        self.logger.log_debug("EMERGENCY: ready")

    async def handle_sensor_limits(self):
        while self.sensors == False or self.sensors.position.alt == None:
            await asyncio.sleep(0.05)
        while self.sensors.position.alt < 1:
            await asyncio.sleep(0.05)
        #TODO DOUBLECHECK abs(...) < ...
        while \
            self.sensors.position.alt < self.sensor_limits.alt and \
            self.sensors.position.alt > self.sensor_limits.min_alt and \
            abs(self.sensors.roll) < self.sensor_limits.roll and \
            abs(self.sensors.pitch) < self.sensor_limits.pitch:
                await asyncio.sleep(0.05)

        await self.emergencyLanding(f"sensors data out of limits\
                                    \nalt: {self.sensors.position.alt}\
                                    \nroll: {self.sensors.roll}\
                                    \npitch: {self.sensors.pitch}")

    async def handle_timeout(self, timeout):
        while not self.server.ready:
            await asyncio.sleep(0.05)
        self.timeout = datetime.datetime.now() + datetime.timedelta(0,timeout) 
        self.logger.log_debug(f"EMERGENCY: {timeout} seconds timeout set")
        while self.timeout > datetime.datetime.now():
            await asyncio.sleep(0.05)
        await self.emergencyLanding("timeout force landing")

    async def handle_server_emergency(self):
        while not self.server.emergency:
            await asyncio.sleep(0.05)
        await self.emergencyLanding("triggered from server")

    async def emergencyLanding(self, data):
        self.logger.log_debug("EMERGENCY: landing")
        self.logger.log_debug(f"EMERGENCY: {data}")
        await self.drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await self.drone.offboard.start()
        await self.drone.action.land()
