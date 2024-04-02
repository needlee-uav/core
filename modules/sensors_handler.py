class SensorsHandler:
    rel_alt = 0.0
    position = {"lat": 0.0, "lon": 0.0}
    quaternion = {}
    heading = 0.0
    pitch = 0
    roll = 0
    velocity_down_m_s = 0

    async def update_vertical_velocity(self, Drone):
        async for velocity in Drone.telemetry.velocity_ned():
            velocity_down_m_s = round(velocity.down_m_s, 1)
            if self.velocity_down_m_s != velocity_down_m_s:
                self.velocity_down_m_s = velocity_down_m_s

    async def update_pitch_roll(self, Drone):
        async for att_e in Drone.telemetry.attitude_euler():
            pitch = round(att_e.pitch_deg, 0)
            roll = round(att_e.roll_deg, 0)
            if self.pitch != pitch or self.roll != roll:
                self.pitch = pitch
                self.roll = roll

    async def update_position(self, Drone):
        async for position in Drone.telemetry.position():
            lat = round(position.latitude_deg, 5)
            lon = round(position.longitude_deg, 5)
            rel_alt = round(position.relative_altitude_m, 2)
            if self.rel_alt != rel_alt:
                self.rel_alt = rel_alt
            if lon + lat != self.position["lat"] + self.position["lon"]:
                self.position["lat"] = lat
                self.position["lon"] = lon

    async def update_heading(self, Drone):
        async for heading in Drone.telemetry.heading():
            if round(heading.heading_deg, 1) != self.heading:
                self.heading = round(heading.heading_deg, 1)
