import asyncio
from mavsdk.offboard import (VelocityBodyYawspeed, VelocityNedYaw)
from math import sqrt

class OffboardHandler:
    grid_yaw = False
    target_coords = (0,0)
    yaw_diff = 0.0
    distance = 0.0

    async def handle_offboard(self, StageHandler, VisionHandler, SensorsHandler, Drone):
        while True:
            # "CAPTURE": 2
            if StageHandler.stage == 2 and StageHandler.offboard_mode == False:
                await self.start_offboard(Drone=Drone, StageHandler=StageHandler)
                await asyncio.sleep(2)
                await self.goto_target(Drone=Drone, VisionHandler=VisionHandler, SensorsHandler=SensorsHandler)
                StageHandler.offboard_mode = False
                await Drone.offboard.stop()
                print("OFFBOARD: stoped")
                StageHandler.target_detected = False
                StageHandler.target_captured = False
                VisionHandler.detection_threshold = 1
                await asyncio.sleep(10)
                VisionHandler.detection_threshold = 0.3
            await asyncio.sleep(0.1)
    
    async def start_offboard(self, Drone, StageHandler):
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await Drone.offboard.start()
        StageHandler.offboard_mode = True
        print("OFFBOARD: started")

    async def turn_to_grid_yaw(self, Drone, SensorsHandler, yaw):
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await Drone.offboard.start()

        print("OFFBOARD: to grid yaw")
        while SensorsHandler.heading > yaw + 0.2 or SensorsHandler.heading < yaw - 0.2:
            await Drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw))
            await asyncio.sleep(2)

    async def fly_grid_route(self, Drone, StageHandler):
        while (StageHandler.target_detected == False):
            await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(2.0, 0.0, 0.0, 0.0))
            await asyncio.sleep(1)

        await self.change_velocity(Drone, 2.0, 0.5, 0.4)

        while (StageHandler.target_captured == False):
            await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.5, 0.0, 0.0, 0.0))
            await asyncio.sleep(1)
        await self.change_velocity(Drone, 0.5, 0.0, 0.2)
        print("OFFBOARD: stop on captured target")
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await asyncio.sleep(2)

    async def change_velocity(self, Drone, curr_v, new_v, sec):
        step = (new_v - curr_v) / 4
        for n in range(4):
            print(f"vel: {curr_v + step * n}")
            await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(curr_v + step * n, 0.0, 0.0, 0.0))
            await asyncio.sleep(sec / 4)
        
    async def goto_target(self, Drone, VisionHandler, SensorsHandler):
        print("OFFBOARD: observe target")
        while (VisionHandler.target_coords[1] > 10 or VisionHandler.target_coords[1] < -10) or (VisionHandler.target_yaw_angle > 2 or VisionHandler.target_yaw_angle < -2):
            if SensorsHandler.rel_alt < 8.0:
                break
            yaw_v = sqrt(abs(VisionHandler.target_yaw_angle))
            if VisionHandler.target_yaw_angle < 0: yaw_v *= -1
            await Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.5, 0.0, 0.3, yaw_v)
                )
            await asyncio.sleep(1)
        
        print("OFFBOARD: target reached")
        await Drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await asyncio.sleep(1)

    