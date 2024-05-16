import asyncio
from mavsdk.offboard import (VelocityBodyYawspeed)
from math import sqrt

class OffboardHandler:
    def __init__(self, Pilot):
        self.Pilot = Pilot
        asyncio.ensure_future(self.handle_offboard())
        if not Pilot.config.nocapturing:
            asyncio.ensure_future(self.handle_capture())
            
    async def handle_offboard(self):
        while True:
            if self.Pilot.params.stage.offboard_mode:
                await self.Pilot.Drone.offboard.set_velocity_body(
                    VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
                await self.Pilot.Drone.offboard.start()
                self.Pilot.Logger.log_debug("OFFBOARD: start")
                await self.offboard_algorithm()
                self.Pilot.params.stage.offboard_mode = False
            await asyncio.sleep(1)

    async def offboard_algorithm(self):
        self.Pilot.Logger.log_debug("OFFBOARD: run flight algorithm")
        for command in self.Pilot.params.offboard.algo.commands:
            await self.Pilot.Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(command.forward_m_s, command.right_m_s, command.down_m_s, command.yawspeed_deg_s))
            await asyncio.sleep(command.duration)
        self.Pilot.Logger.log_debug("OFFBOARD: flight algorithm finished")
        await self.Pilot.Drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        
    async def handle_capture(self):
        self.Pilot.Logger.log_debug("OFFBOARD: enable capturing")
        while True:
            if self.Pilot.params.stage.name == "CAPTURE":
                await self.Pilot.Drone.offboard.set_velocity_body(
                    VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
                await self.Pilot.Drone.offboard.start()
                self.Pilot.Logger.log_debug("CAPTURE: start")
                while True:
                    print("CAPTURE!")
                    await asyncio.sleep(1)
            await asyncio.sleep(0.1)

    


    # async def goto_target(self, Drone, VisionHandler, SensorsHandler):
    #     self.Logger.log_debug("OFFBOARD: observe target")
    #     while (VisionHandler.target_coords[1] > 10 or VisionHandler.target_coords[1] < -10) or (VisionHandler.target_yaw_angle > 2 or VisionHandler.target_yaw_angle < -2):
    #         if SensorsHandler.rel_alt < 8.0 or VisionHandler.detection_threshold > 0.80:
    #             break
    #         yaw_v = sqrt(abs(VisionHandler.target_yaw_angle))
    #         if VisionHandler.target_yaw_angle < 0: yaw_v *= -1
    #         await Drone.offboard.set_velocity_body(
    #             VelocityBodyYawspeed(1, 0.0, 0.5, yaw_v)
    #             )
    #         await asyncio.sleep(1)

    #     self.Logger.log_debug("OFFBOARD: target reached")
    #     await Drone.offboard.set_velocity_body(
    #         VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    #     await asyncio.sleep(1)



    # async def change_velocity(self, Drone, curr_v, new_v, sec):
    #     step = (new_v - curr_v) / 4
    #     for n in range(4):
    #         await Drone.offboard.set_velocity_body(
    #             VelocityBodyYawspeed(curr_v + step * n, 0.0, 0.0, 0.0))
    #         await asyncio.sleep(sec / 4)

    # async def goto_target(self, Drone, VisionHandler, SensorsHandler):
    #     self.Logger.log_debug("OFFBOARD: observe target")
    #     while (VisionHandler.target_coords[1] > 10 or VisionHandler.target_coords[1] < -10) or (VisionHandler.target_yaw_angle > 2 or VisionHandler.target_yaw_angle < -2):
    #         if SensorsHandler.rel_alt < 8.0 or VisionHandler.detection_threshold > 0.80:
    #             break
    #         yaw_v = sqrt(abs(VisionHandler.target_yaw_angle))
    #         if VisionHandler.target_yaw_angle < 0: yaw_v *= -1
    #         await Drone.offboard.set_velocity_body(
    #             VelocityBodyYawspeed(1, 0.0, 0.5, yaw_v)
    #             )
    #         await asyncio.sleep(1)

    #     self.Logger.log_debug("OFFBOARD: target reached")
    #     await Drone.offboard.set_velocity_body(
    #         VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    #     await asyncio.sleep(1)
