import helpers
import asyncio
import math
import helpers

class RouteHandler:
    def __init__(self, Pilot):
        self.Pilot = Pilot
        self.route = self.Pilot.params.route
        self.Drone = Pilot.Drone
        self.sensors = Pilot.params.sensors
        self.stage = Pilot.params.stage
        # TODO
        asyncio.ensure_future(self.handle_ready())

    async def handle_ready(self):
        while not self.stage.ready:
            await asyncio.sleep(1)
        if self.Pilot.params.route.points:
            asyncio.ensure_future(self.handle_route())

    async def handle_route(self):
        await self.update_target_point()
        while True:
            if self.stage.name == "ROUTE":
                await self.goto_target_point()
            await asyncio.sleep(0.05)

    async def update_target_point(self):
        print(self.route.points)
        print(self.route.point_i)
        print(self.route.points[self.route.point_i])
        self.route.target_point = self.route.points[self.route.point_i]
        if self.route.point_i < len(self.route.points) - 1:
            self.route.point_i += 1
        else: self.route.target_point = None
        self.route.point_reached = False

    async def goto_target_point(self):
        await self.Drone.action.goto_location(self.route.target_point.lat, self.route.target_point.lon, 505, 90)
        while not self.route.point_reached:
            if helpers.gps_to_meters(self.sensors.position.lat, self.sensors.position.lon, self.route.target_point.lat, self.route.target_point.lon) < 1.5:
                self.route.point_reached = True
                print("ROUTE: point reached!")
            await asyncio.sleep(1)
        await self.update_target_point()
    # async def update_target_point(self, Drone, SensorsHandler, StageHandler):
    #     while not StageHandler.in_air:
    #         await asyncio.sleep(1)
    #     while True:
    #         if not StageHandler.target_detected and StageHandler.stage == 1:
    #             await self.goto_target_point(Drone=Drone, SensorsHandler=SensorsHandler)
    #             distance = helpers.gps_to_meters(SensorsHandler.position["lat"], SensorsHandler.position["lon"], self.target_point[0], self.target_point[1])
    #             self.Logger.log_debug(f"ROUTE: {round(distance, 2)} to point")
    #             if distance < 1.5:
    #                 self.Logger.log_debug("ROUTE: point reached!")
    #                 self.next_point()
    #         await asyncio.sleep(1)

    # async def goto_target_point(self, Drone, SensorsHandler):
    #     heading = await self.calculate_gps_heading(SensorsHandler)
    #     await Drone.action.goto_location(self.target_point[0], self.target_point[1], 505, heading)

    # def next_point(self):
    #     if self.point_i < len(self.route) - 1:
    #         self.point_i += 1
    #         self.target_point = self.route[self.point_i]
    #     else:
    #         self.target_point = self.home

    async def calculate_gps_heading(self, SensorsHandler):
        position = SensorsHandler.position
        lat1 = (round(position["lat"], 5) * math.pi) / 180.0
        lon1 = (round(position["lon"], 5) * math.pi) / 180.0
        lat2 = (self.target_point[0] * math.pi) / 180.0
        lon2 = (self.target_point[1] * math.pi) / 180.0

        delta_lon = lon2 - lon1
        x = math.cos(lat2) * math.sin(delta_lon)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
        heading = math.atan2(x, y)
        heading = (heading * 180.0) / math.pi
        if (heading < 0):
            heading = 360.0 + heading

        return round(heading)
