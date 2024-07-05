#!/usr/bin/env python3
import cv2 as cv
import asyncio
from mavsdk import System
from multiprocessing import Process, Pipe
from cam_rec import Camera

async def run():
    print("INIT")
    drone = None
    camera = Camera()
    
    # CAMERA FIRST
    parent_conn, child_conn = Pipe()
    p = Process(target=camera.run, args=(child_conn, ))
    p.start()
    while not parent_conn.recv()[0] == "READY":
        await asyncio.sleep(0.05)
    print("CAM READY")
    
    drone = System()
    print("INIT DRONE")
    await drone.connect(system_address="serial:///dev/ttyACM0")
    print("INIT: Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("INIT: Connected to drone!")
            break
    while not parent_conn.recv()[0] == "DONE":
        await asyncio.sleep(0.05)
        print("CAM DONE")
    await drone.action.arm()
    await drone.action.kill()

# RUN ASYNCIO
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


