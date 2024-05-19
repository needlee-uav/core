import asyncio
from mavsdk.offboard import (VelocityBodyYawspeed)
from math import sqrt, copysign

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
            if self.Pilot.params.stage.name == "CAPTURE" and self.Pilot.params.target.target_captured != True:
                await self.Pilot.Drone.offboard.set_velocity_body(
                    VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
                await self.Pilot.Drone.offboard.start()
                self.Pilot.Logger.log_debug("CAPTURE: start")
                await asyncio.sleep(2)
                await self.center_target()
                while not self.Pilot.params.target.target_captured:
                    await asyncio.sleep(1)

            await asyncio.sleep(0.1)

    async def center_target(self):
        size = [int(self.Pilot.params.img.shape[0]), int(self.Pilot.params.img.shape[1])]
        conf = self.Pilot.params.target.confidence
        best_conf = 0.0
        target_lost_count = 0
        previous = [0.0, 0.0, 0.0, 0.0]
        while True:
            conf = self.Pilot.params.target.confidence

            if conf > best_conf:
                best_conf = conf
                print(f"best confidence: {best_conf}")

            coords = [
                (int(self.Pilot.params.box[3]) + int(self.Pilot.params.box[1])) / 2,
                (int(self.Pilot.params.box[2]) + int(self.Pilot.params.box[0])) / 2
            ]
            
            forward_m_s, right_m_s, down_m_s, yawspeed_deg_s = self.calculate_instructions(size, coords)
            print(forward_m_s, right_m_s, down_m_s, yawspeed_deg_s)
            if forward_m_s != 1.0:
                if previous != [forward_m_s, right_m_s, down_m_s, yawspeed_deg_s]:
                    print("update")
                    await self.Pilot.Drone.offboard.set_velocity_body(
                        VelocityBodyYawspeed(forward_m_s, right_m_s, down_m_s, yawspeed_deg_s))
                    previous = [forward_m_s, right_m_s, down_m_s, yawspeed_deg_s]
            elif target_lost_count < 5:
                target_lost_count += 1
                print(f"target lost: {target_lost_count}")
            else:
                await self.Pilot.Drone.offboard.set_velocity_body(
                    VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
                return

            await asyncio.sleep(1)

    
    def calculate_instructions(self, size, coords):
        print("INSTRUCTIONS")
        print(f"ALT: {self.Pilot.params.sensors.position.alt}")
        delta_h, delta_w = self.calculate_delta(size, coords)
        print(delta_h, delta_w)
        forward_m_s = 0.0
        right_m_s = 0.0
        down_m_s = 0.0
        yawspeed_deg_s  = 0.0

        if abs(delta_h) < 0.1:
            delta_h = 0.0
        if abs(delta_w) < 0.1:
            delta_w = 0.0

        if delta_w == 1.0 and delta_h == 1.0:
            return 1, 1, 1, 1
        if delta_w == 0.0 and delta_h == 0.0 and self.Pilot.params.sensors.position.alt > 4.0:
            forward_m_s = 0.3
            down_m_s = 0.1
        elif abs(delta_h) < 0.5 and delta_w != 0.0:
            yawspeed_deg_s = self.calculate_yaw_speed(delta_w)
        elif abs(delta_w) < 0.5 and delta_h != 0.0:
            forward_m_s = self.calculate_forward_speed(delta_h)
        
        return forward_m_s, right_m_s, down_m_s, yawspeed_deg_s
    
    def calculate_yaw_speed(self, delta):
        sign = copysign(1, delta) * -1
        if abs(delta) < 0.2: return round(sign * 5, 2)
        if abs(delta) < 0.5: return round(delta * 20, 2)
        if abs(delta) > 0.5: return round(sign * 10, 2)

    def calculate_forward_speed(self, delta):
        sign = copysign(1, delta)
        return round(sign * 0.3, 2)

    def calculate_delta(self, size, coords):
        h = round((size[0] / 2 - coords[0]) / (size[0] / 2), 2)
        w = round((size[1] / 2 - coords[1]) / (size[1] / 2), 2)
        return h, w