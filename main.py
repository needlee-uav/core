#!/usr/bin/env python3
import cv2 as cv
import asyncio
from mavsdk import System
import pilot
from multiprocessing import Process, Pipe
from camera.camera import view_camera_video
from data_classes import Camera
from config import Config

async def run():
    print("====== NEEDLEE INIT ======")
    config = Config()
    Drone = False
    camera = None
    if config.vision:
        camera = Camera()
        parent_conn, child_conn = Pipe()
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
            print(box)
            print(f"confidence: {cam_data[5]}")
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
            print(camera.box)
            print(f"confidence: {camera.confidence}")
            await asyncio.sleep(0.05)
    else:
        while True:
            await asyncio.sleep(0.05)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
