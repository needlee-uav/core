#!/usr/bin/env python3
import cv2 as cv
import asyncio
from mavsdk import System
from multiprocessing import Process, Pipe
from test_scripts.cam import Camera

async def run():
    # CONFIGURATE
    drone = None
    camera = Camera()
    
    # CAMERA FIRST
    parent_conn, child_conn = Pipe()
    p = Process(target=camera.run, args=(child_conn, ))
    p.start()
    while not camera.ready:
        await asyncio.sleep(0.05)
    print("CAM READY")
    
    drone = System()
    print("INIT")
    await drone.connect(system_address="serial:///dev/ttyACM0")
    print("INIT: Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("INIT: Connected to drone!")
            break


# RUN ASYNCIO
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())



