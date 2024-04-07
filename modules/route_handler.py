import asyncio
import math
from mavsdk.offboard import (VelocityBodyYawspeed)
from dataclasses import dataclass

@dataclass
class Instructions:
    forward_m_s: float = 4.0
    right_m_s: float = 0.0
    down_m_s: float = 0.0
    yawspeed_deg_s: float = 0.0
    yaw_diff: float = 0.0
    yaw_correction: bool = False
    alt_correction: bool = False

class RouteHandler:
    def __init__(self, Pilot):
        self.Pilot = Pilot
        self.Drone = Pilot.Drone
        self.route = self.Pilot.params.route
        self.sensors = Pilot.params.sensors
        self.stage = Pilot.params.stage

        self.instructions = Instructions()
        asyncio.ensure_future(self.handle_ready())

    async def handle_ready(self):
        while not self.stage.ready:
            await asyncio.sleep(1)
        if self.Pilot.params.route.points:
            asyncio.ensure_future(self.handle_route())
            asyncio.ensure_future(self.handle_yaw_diff())
            asyncio.ensure_future(self.handle_alt())

    async def handle_route(self):
        await self.update_target_point()
        while True:
            if self.stage.name == "ROUTE":
                await self.goto_target_point()
            await asyncio.sleep(0.05)

    async def update_target_point(self):
        if self.route.target_point == self.route.home:
            self.route.route_finished = True
            return
        if self.route.point_i < len(self.route.points) -1:
            self.route.point_i += 1
            self.route.target_point = self.route.points[self.route.point_i]
        else:
            self.route.target_point = self.route.home
        self.route.point_reached = False


    async def handle_yaw_diff(self):
        while True:
            if self.stage.name == "ROUTE":
                target_yaw = self.calculate_gps_heading()
                self.instructions.yaw_diff = self.calculate_gps_heading_diff(current=self.sensors.heading, target=target_yaw)
                self.instructions.yawspeed_deg_s = self.instructions.yaw_diff / 10
            await asyncio.sleep(0.05)

    async def handle_alt(self):
        while True:
            if self.stage.name == "ROUTE":
                target_alt = 8
                alt_diff = self.sensors.position.alt - target_alt
                self.instructions.down_m_s = alt_diff / 5
            await asyncio.sleep(0.05)

    async def goto_target_point(self):
        while self.instructions.yaw_diff == 0.0:
            await asyncio.sleep(1)
        while abs(self.instructions.yaw_diff) > 2 or abs(self.instructions.down_m_s) > 0.4:
            yaw_speed = self.instructions.yawspeed_deg_s
            if abs(yaw_speed) < 6:
                yaw_speed = 6 if yaw_speed > 0 else -6
            vertical_speed = self.instructions.down_m_s
            if abs(vertical_speed) < 0.2:
                vertical_speed = 0.2 if vertical_speed > 0 else -0.2
            await self.Pilot.Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0, 0, vertical_speed, yaw_speed))
            await asyncio.sleep(0.1)
        print("yaw done")
        await self.Pilot.Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0, 0, 0, 0))
        await asyncio.sleep(2)
        print("fly to point")


        await self.Pilot.Drone.offboard.set_velocity_body(
                    VelocityBodyYawspeed(self.instructions.forward_m_s,0,0,0))

        while not self.route.point_reached:
            self.check_distance_to_point()
            if abs(self.instructions.yaw_diff) > 2:
                self.instructions.yaw_correction = True
                await self.Pilot.Drone.offboard.set_velocity_body(
                    VelocityBodyYawspeed(self.instructions.forward_m_s, 0, 0, self.instructions.yawspeed_deg_s))
            elif abs(self.instructions.down_m_s) > 0.4:
                self.instructions.alt_correction = True
                await self.Pilot.Drone.offboard.set_velocity_body(
                    VelocityBodyYawspeed(self.instructions.forward_m_s, 0, self.instructions.down_m_s, 0))
            elif self.instructions.yaw_correction or self.instructions.alt_correction:
                self.instructions.yaw_correction = False
                self.instructions.alt_correction = False
                await self.Pilot.Drone.offboard.set_velocity_body(
                    VelocityBodyYawspeed(self.instructions.forward_m_s, 0, 0, 0))
            await asyncio.sleep(0.1)

        await self.Pilot.Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0, 0, 0, 0))
        await self.update_target_point()

    def check_distance_to_point(self):
        if self.gps_to_meters() < 1.5:
            self.route.point_reached = True
            print("ROUTE: point reached!")

    def gps_to_meters(self):
        R = 6378.137
        dLat = self.route.target_point.lat * math.pi / 180 - self.sensors.position.lat * math.pi / 180
        dLon = self.route.target_point.lon * math.pi / 180 - self.sensors.position.lon * math.pi / 180
        a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(self.sensors.position.lat * math.pi / 180) * math.cos(self.route.target_point.lat  * math.pi / 180) * \
        math.sin(dLon/2) * math.sin(dLon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = R * c
        return d * 1000

    def calculate_gps_heading(self):
        lat1 = (round(self.sensors.position.lat, 5) * math.pi) / 180.0
        lon1 = (round(self.sensors.position.lon, 5) * math.pi) / 180.0
        lat2 = (self.route.target_point.lat * math.pi) / 180.0
        lon2 = (self.route.target_point.lon * math.pi) / 180.0

        delta_lon = lon2 - lon1
        x = math.cos(lat2) * math.sin(delta_lon)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
        heading = math.atan2(x, y)
        heading = (heading * 180.0) / math.pi
        if (heading < 0):
            heading = 360.0 + heading

        return round(heading)

    def calculate_gps_heading_diff(self, current, target):
        diff = target - current
        if abs(diff) > 180:
            diff = 360 - current - target if current - target > 0 else -360 + abs(current - target)
        return diff
