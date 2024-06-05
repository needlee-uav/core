class OffboardComand:
    duration: float
    forward_m_s: float
    right_m_s: float
    down_m_s: float
    yawspeed_deg_s: float
    def __init__(self, duration, forward_m_s, right_m_s, down_m_s, yawspeed_deg_s):
        self.duration = duration
        self.forward_m_s = forward_m_s
        self.right_m_s = right_m_s
        self.down_m_s = down_m_s
        self.yawspeed_deg_s = yawspeed_deg_s

class OffboardAlgorithm:
    commands = []

class Position:
    lat: float
    lon: float
    alt: float
    def __init__(self, lat, lon, alt):
        self.lat = lat
        self.lon = lon
        self.alt = alt if alt else None

class Camera:
    box = []
    img = []
    confidence = 0