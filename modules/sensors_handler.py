import asyncio
import time

class SensorsHandler:
    def __init__(self, Pilot):
        self.Drone = Pilot.Drone
        self.Logger = Pilot.Logger
        self.params = Pilot.params.sensors
        asyncio.ensure_future(self.ready())
        asyncio.ensure_future(self.update_position())
        asyncio.ensure_future(self.update_heading())
        asyncio.ensure_future(self.update_pitch_roll())
        asyncio.ensure_future(self.update_vertical_velocity())

    async def ready(self):
        while self.params.position.lat == 0.0:
            await asyncio.sleep(1)
        self.params.ready = True
        self.Logger.log_debug("SENSORS: ready")

    async def update_vertical_velocity(self):
        async for velocity in self.Drone.telemetry.velocity_ned():
            velocity_down_m_s = round(velocity.down_m_s, 1)
            if self.params.velocity_down_m_s != velocity_down_m_s:
                self.params.velocity_down_m_s = velocity_down_m_s

    async def update_pitch_roll(self):
        async for att_e in self.Drone.telemetry.attitude_euler():
            pitch = round(att_e.pitch_deg, 1)
            roll = round(att_e.roll_deg, 1)
            if self.params.pitch != pitch or self.params.roll != roll:
                self.params.pitch = pitch
                self.params.roll = roll

    async def update_position(self):
        async for position in self.Drone.telemetry.position():
            lat = round(position.latitude_deg, 5)
            lon = round(position.longitude_deg, 5)
            rel_alt = round(position.relative_altitude_m, 2)
            if self.params.position.alt != rel_alt:
                self.params.position.alt = rel_alt
            if lon + lat != self.params.position.lat + self.params.position.lon:
                self.params.position.lat = lat
                self.params.position.lon = lon

    async def update_heading(self):
        async for heading in self.Drone.telemetry.heading():
            if round(heading.heading_deg, 1) != self.params.heading:
                self.params.heading = round(heading.heading_deg, 1)
