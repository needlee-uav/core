import asyncio
import datetime
from mavsdk.offboard import (VelocityBodyYawspeed)
from math import copysign
from data_classes import OffboardComand

class OffboardHandler:
    busy = False
    def __init__(self, Pilot):
        self.Pilot = Pilot
        asyncio.ensure_future(self.commander())
        if Pilot.config.capturing:
            asyncio.ensure_future(self.handle_capture())
    
    # A single source of truth for commands
    async def commander(self):
        while not self.Pilot.params.stage.in_air:
            await asyncio.sleep(0.05)

        while True:
            if not self.Pilot.params.offboard.busy:
                self.Pilot.params.offboard.busy = True
                self.Pilot.Logger.log_debug("OFFBOARD: run command")
                command = self.Pilot.params.offboard.command
                await self.Pilot.Drone.offboard.set_velocity_body(
                    VelocityBodyYawspeed(command.forward_m_s, command.right_m_s, command.down_m_s, command.yawspeed_deg_s))
            await asyncio.sleep(0.05)

    
    def update_command(self, command, stage):
        if self.Pilot.params.stage.name == stage:
            self.Pilot.Logger.log_debug("OFFBOARD: update command")
            command.timeout = datetime.datetime.now() + datetime.timedelta(0, command.duration)
            self.Pilot.params.offboard.command = command
            self.Pilot.params.offboard.busy = False
        
    async def handle_capture(self):
        self.Pilot.Logger.log_debug("OFFBOARD: enable capturing")
        while True:
            if self.Pilot.params.stage.name == "CAPTURE" and self.Pilot.params.target.target_captured != True:
                self.Pilot.Logger.log_debug("CAPTURE: start")
                self.update_command(OffboardComand(0,0,0,0,0), "CAPTURE")
                await self.center_target()
                while not self.Pilot.params.target.target_captured and self.Pilot.params.target.target_detected:
                    print(self.Pilot.params.target.target_captured)
                    print(self.Pilot.params.target.target_detected)
                    await asyncio.sleep(0.1)
                self.update_command(OffboardComand(0,0,0,0,0), "CAPTURE")
                self.Pilot.Logger.log_debug("CAPTURE: end")
            await asyncio.sleep(0.1)

    async def center_target(self):
        size = [int(self.Pilot.params.img.shape[0]), int(self.Pilot.params.img.shape[1])]
        conf = self.Pilot.params.target.confidence
        best_conf = 0.0
        target_lost_count = 0
        previous = [0.0, 0.0, 0.0, 0.0]
        while True:
            if best_conf > 0.7 and previous == [0,0,0,0]:
                self.Pilot.params.target.target_captured = True
                self.Pilot.params.target.target_detected = False
                return
            
            conf = self.Pilot.params.target.confidence
            if conf > best_conf:
                best_conf = conf
            print(f"confidence: {conf}")
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
                    self.update_command(OffboardComand(0,forward_m_s, right_m_s, down_m_s, yawspeed_deg_s), "CAPTURE")
                    previous = [forward_m_s, right_m_s, down_m_s, yawspeed_deg_s]
            elif target_lost_count < 5:
                target_lost_count += 1
                print(f"target lost: {target_lost_count}")
            else:
                self.Pilot.params.target.target_detected = False
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
        sign = copysign(1, delta)
        if abs(delta) < 0.2: return round(sign * 5, 2)
        if abs(delta) < 0.5: return round(sign * 7, 2)
        if abs(delta) > 0.5: return round(sign * 10, 2)

    def calculate_forward_speed(self, delta):
        sign = copysign(1, delta)
        return round(sign * 0.3, 2)

    def calculate_delta(self, size, coords):
        h = round((size[0] / 2 - coords[0]) / (size[0] / 2), 2)
        w = -round((size[1] / 2 - coords[1]) / (size[1] / 2), 2)
        return h, w