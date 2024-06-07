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


class Test():
    run: bool = False
    id: int = 0

class Stage:
    test: Test = Test()
    ready: bool = False
    in_air: bool = False
    emergency: bool = False
    emergency_data: dict = None
    name = "PREARM"
    offboard_mode = False

class Sensors:
    ready = False
    position = Position(0.0, 0.0, 0.0)
    heading = 0.0
    pitch = 0.0
    roll = 0.0
    velocity_down_m_s = 0.0

class Server:
    connected = False
    enable_camera: bool = False


class Route:
    route_finished = False
    point_reached = False
    point_i = -1
    points = []
    target_point = None
    checkpoint = None
    home = None

class Offboard:
    algo: OffboardAlgorithm = None
    grid_yaw: bool = False
    target_coords: Position = None
    yaw_diff: float = 0.0
    distance: float = 0.0

class Target:
    target_coords: Position = None
    target_distance: float = 0.0
    confidence: float = 0.0
    target_detected: bool = False
    target_captured: bool = False

class Params:
    box = []
    img = []
    debug_log = []
    stage: Stage = Stage()
    sensors: Sensors = Sensors()
    server: Server = Server()
    route: Route = Route()
    offboard: Offboard = Offboard()
    target: Target = Target()