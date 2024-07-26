import json, argparse
import sys

class ConfigCamera:
    def __init__(self, camera_address, model, camera_w, camera_h):
        self.camera_address = camera_address
        self.width = camera_w
        self.height = camera_h
        self.model = model

class SensorLimits:
    def __init__(self, alt, min_alt, roll, pitch):
        self.alt = alt
        self.min_alt = min_alt
        self.roll = roll
        self.pitch = pitch

class Config:
    def __init__(self):
        config_json = self.load_config()

        # Set arguments
        args = self.parse_args()
        self.run = args.run
        self.mode = args.mode
        self.server = args.server
        self.cameramode = args.cameramode
        self.visiontest = args.visiontest
        self.capturing = args.capturing
        self.timeout = args.timeout
        self.nogps = args.nogps
        self.args_autoswitch()
        
        # Set sensor limits
        self.sensor_limits = SensorLimits(
            config_json["sensor_limits"]["alt"],
            config_json["sensor_limits"]["min_alt"],
            config_json["sensor_limits"]["roll"],
            config_json["sensor_limits"]["pitch"]
        )

        print(self.sensor_limits)
        # Set camera and vision
        if self.cameramode != "none":
            camera_address = config_json["camera_address"][self.run] 
            camera_dims = config_json["camera_dims"][self.run]
            if self.mode == "visiontest":
                camera_dims = config_json["camera_dims"]["vision_test"]
            
            camera_w = camera_dims["w"]
            camera_h = camera_dims["h"]
            model = False
            if self.cameramode != "stream":
                model = config_json["vision_model"][self.run]

            self.camera = ConfigCamera(camera_address, model, camera_w, camera_h)
        else:
            self.visiontest = 0

        # Set drone system address
        self.system_address = config_json["system_address"][self.run] 
        
        # Set server address
        if self.server == "local":
            self.server_url = config_json["server"]["local_url"]
        elif self.server == "web":
            self.server_url = config_json["server"]["url"]
        else:
            self.server_url = False

        # Set drone ID
        self.drone_id = config_json["server"]["drone_id"]

        self.print_config()

    def args_autoswitch(self):
        if self.timeout == 0:
            self.timeout = False
        if self.mode == "visiontest":
            if self.visiontest == 0:
                sys.exit("Vision test number is required for running visiontest, set --visiontest n")
            self.server = "serverless"
            self.cameramode = "vision"
        elif self.server == "serverless":
            sys.exit(f"Can't run serverless with mode={self.mode}.")

    def load_config(self):
        path = '/home/jetson/Desktop/core/config.json'
        # path = 'config.json'
        config_file = open(path)
        config_json = json.load(config_file)
        config_file.close()
        return config_json

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--run",
            help="Can't be empty: (sim, main)",
            choices=["sim", "main"],
            type=str,
            required=True)

        parser.add_argument(
            "--mode",
            help="Can't be empty: (test, mission, visiontest)",
            choices=["test", "mission", "visiontest"],
            type=str, 
            required=True)
        
        parser.add_argument(
            "--server",
            help="Can't be empty: (serverless, local, web)",
            choices=["serverless", "local", "web"],
            type=str,
            required=True)
        
        parser.add_argument(
            "--cameramode",
            help="Can't be empty: (none, stream, vision)",
            choices=["none", "stream", "vision"],
            type=str,
            required=True)
        
        parser.add_argument(
            "--visiontest",
            help="Visiontest number, required for mode=visiontest", 
            type=int, 
            default=0)
        
        parser.add_argument(
            "--timeout",
            help="Timeout before force landing in seconds", 
            type=int, 
            default=0)
        
        parser.add_argument(
            "--capturing",
            help="Fly without capturing stage if this argument is not set", 
            action="store_true")
        
        parser.add_argument(
            "--nogps",
            help="Run home tests if nogps set", 
            action="store_true")
        return parser.parse_args()

    def print_config(self):
        nogps = ""
        if self.nogps:
            nogps = f"\nnogps mode"
        camera_config_print = ""
        if self.cameramode != "none":
            camera_config_print = \
                f"\ncamera.camera_address: {self.camera.camera_address}\
                \ncamera.width: {self.camera.width}\
                \ncamera.height: {self.camera.height}\
                \ncamera.model: {self.camera.model}"
            
        server_config_print = ""
        if self.server != "none":
            server_config_print = \
                f"\nserver_url: {self.server_url}"
        
        sensor_limits = f"\
            \nsensor_limits.alt: {self.sensor_limits.alt}\
            \nsensor_limits.roll: {self.sensor_limits.roll}\
            \nsensor_limits.pitch: {self.sensor_limits.pitch}"
        self.config_print = \
            f"\
            \n==== NEEDLEE INIT ====\
            {nogps}\
            \nrun: {self.run}\
            \nmode: {self.mode}\
            \nserver: {self.server}\
            \ncameramode: {self.cameramode}\
            \nvisiontest: {self.visiontest}\
            \ncapturing: {self.capturing}\
            \ntimeout: {self.timeout}\
            {sensor_limits}\
            {camera_config_print}\
            {server_config_print}\
            \nsystem_address: {self.system_address}\
            \ndrone_id: {self.drone_id}\
            \n======================"
        