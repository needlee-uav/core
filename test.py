size = [720, 1280]
coords = [450, 690]
import math

def calculate_instructions(size, coords):
    delta_h, delta_w = calculate_delta(size, coords)
    print(size)
    print(delta_h)
    print(delta_w)
    forward_m_s = 0
    right_m_s = 0
    down_m_s = 0
    yawspeed_deg_s  = 0

    if abs(delta_h) < 0.1:
        delta_h = 0
    if abs(delta_w) < 0.1:
        delta_w = 0

    if abs(delta_h) < 0.5 and delta_w != 0:
        yawspeed_deg_s = calculate_yaw_speed(delta_w)
    elif abs(delta_w) < 0.5 and delta_h != 0:
        forward_m_s = calculate_forward_speed(delta_h)

    return forward_m_s, right_m_s, down_m_s, yawspeed_deg_s
    


    # if self.Pilot.params.sensors.position.alt > 4:
    #     if abs(delta["h"]) < size[0]/10*8 and abs(delta["w"]) < size[1]/15*10:
    #         down_m_s = 0.3
    #     if abs(delta["h"]) > size[0]/10:
    #         forward_m_s = 
    # if abs(delta["h"]) < size[0]/10 and abs(delta["w"]) < size[1]/15:
    #     if self.Pilot.params.sensors.position.alt > 4:
    #         forward_m_s = 0.4
    #         down_m_s = 0.3
    # elif abs(delta["h"]) > size[0]/10 
    # return forward_m_s, right_m_s, down_m_s, yawspeed_deg_s

def calculate_yaw_speed(delta):
    sign = math.copysign(1, delta) * -1
    if abs(delta) < 0.2: return sign * 5 
    if abs(delta) < 0.5: return round(delta * 20)
    if abs(delta) > 0.5: return sign * 10 

def calculate_forward_speed(delta):
    return round(delta * 2)

def calculate_delta(size, coords):
    h = round((size[0] / 2 - coords[0]) / (size[0] / 2), 2)
    w = round((size[1] / 2 - coords[1]) / (size[1] / 2), 2)
    return h, w

print(calculate_instructions(size, coords))