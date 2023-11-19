class SensorsHandler:
    rel_alt = 0.0
    position = {"lat": 0.0, "lon": 0.0}
    quaternion = {}
    heading = 0.0

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