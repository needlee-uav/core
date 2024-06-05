#!/usr/bin/env python3
import cv2 as cv
import json
import argparse
import asyncio
from mavsdk import System
import pilot
# import pilot_test
from multiprocessing import Process, Pipe
from camera.camera import view_camera_video
from data_classes import OffboardComand, OffboardAlgorithm, Position, Camera


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

async def run():
    print("INIT")
    config = Config()
    Drone = False
    camera = None
    if config.vision:
        camera = Camera()
        parent_conn,child_conn = Pipe()
        p = Process(target=view_camera_video, args=(child_conn, config, ))
        p.start()
        
    if config.vision_test == 0:
        Drone = System()
        await Drone.connect(system_address=config.system_address)
        print("Waiting for drone to connect...")
        async for state in Drone.core.connection_state():
            if state.is_connected:
                print(f"-- Connected to drone!")
                break

        if not config.no_gps_mode:
            async for health in Drone.telemetry.health():
                if health.is_global_position_ok and health.is_home_position_ok:
                    print("-- Global position state is good enough for flying.")
                    break
                
        pilot.Pilot(Drone=Drone, config=config, camera=camera)

    else:
        while True:
            cam_data = parent_conn.recv()
            box = cam_data[:4]
            frame = cam_data[4]
            confidence = cam_data[5]
            print(confidence)
            print(box)
            cv.rectangle(frame, (box[0], box[1]), (box[2], box[3]),(0, 255, 0))
            cv.imshow("frame", frame)
            if cv.waitKey(1) >= 0:
                break
            await asyncio.sleep(0.05)
 
    if config.vision:
        while True:
            cam_data = parent_conn.recv()
            camera.box = cam_data[:4]
            camera.img = cam_data[4]
            camera.confidence = cam_data[5]
            cv.rectangle(camera.img, (camera.box[0], camera.box[1]), (camera.box[2], camera.box[3]),(0, 255, 0))
            cv.imshow("frame", camera.img)
            if cv.waitKey(1) >= 0:
                break
            await asyncio.sleep(0.05)
    else:
        while True:
            await asyncio.sleep(0.05)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
