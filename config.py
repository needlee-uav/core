import json, argparse

class Config:
    def __init__(self):
        config_json = load_config()
        args = parse_args()
        self.nocapturing = args.nocapturing
        self.vision_test = args.visiontest
        self.drone_id = config_json["server"]["drone_id"]
        self.sim = args.sim
        self.system_address = config_json["system_address"]["sim"] if args.sim else config_json["system_address"]["main"]
        self.server_url = config_json["server"]["local_url"] if args.local else config_json["server"]["url"]
        self.serverless = args.serverless
        self.test_mode = args.test
        self.no_gps_mode = args.nogps
        self.vision = False
        if not args.nocamera:
            vision_config = config_json["vision"] if args.sim else config_json["jetson_vision"]
            self.vision = ConfigVision(vision_config, args.novision)

class ConfigVision:
    def __init__(self, config_vision, no_vision):
        self.camera_address = config_vision["camera_address"]
        self.width = config_vision["width"]
        self.height = config_vision["height"]
        self.model = False if no_vision else config_vision["model"]

def load_config():
    config_file = open('config.json')
    config_json = json.load(config_file)
    config_file.close()
    return config_json

def parse_args():
    parser = argparse.ArgumentParser()
    args = [
        ["--visiontest", "Run vision tests"], # done
        ["--sim", "Run simulation"], # done
        ["--local", "Run on local server"],
        ["--serverless", "Run preset mission without server connection"],
        ["--test", "Run flight tests"], # done
        ["--nocamera", "Run without camera"], # done
        ["--nocapturing", "Run vision without offboard target capturing"], # done
        ["--novision", "Run without computer vision"], # done
        ["--nogps", "Run without gps (dangerous)"]
    ]
    for arg in args:
        if arg[0] == "--visiontest":
            parser.add_argument(arg[0], help=arg[1], type=int, default=0)
        else:
            parser.add_argument(arg[0], help=arg[1], action="store_true")
    return parser.parse_args()
