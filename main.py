#!/usr/bin/env python3
import cv2 as cv
import asyncio
from mavsdk import System
import pilot
from multiprocessing import Process, Pipe

from config import Config
from modules.logger import Logger
from modules.server_handler import ServerHandler
from modules.emergency_handler import EmergencyHandler

async def run():
    # CONFIGURATE
    drone = None
    camera = None
    server = None
    config = Config()
    logger = Logger()
    logger.log_debug(config.config_print)
    print(config.config_print)

    # CAMERA BEFORE ANYTHING ELSE
    if config.cameramode != "none":
        camera = None
        if config.run == "main":
            import camera.camera_jetson as j
            camera = j.Camera(config=config)
        else:
            import camera.camera_sim as s
            camera = s.Camera(config=config)

        parent_conn, child_conn = Pipe()
        p = Process(target=camera.run, args=(child_conn, ))
        p.start()
    
        # CONTINUE ON CAMERA READY ONLY
        while not parent_conn.recv()[0] == "READY":
            await asyncio.sleep(0.05)
        logger.log_debug("CAM READY")

    # INIT SERVER
    if config.server != "serverless":
        server = ServerHandler(logger, config)

    # INIT MAVSDK & PILOT
    if config.mode != "visiontest":
        drone = System()
        logger.log_debug("INIT")
        await drone.connect(system_address=config.system_address)
        logger.log_debug("INIT: Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                logger.log_debug("INIT: Connected to drone!")
                break
        if not config.nogps:
            async for health in drone.telemetry.health():
                if health.is_global_position_ok and health.is_home_position_ok:
                    logger.log_debug("INIT: Global position state is good enough for flying.")
                    break
        emergency = EmergencyHandler(server, config.timeout, logger, drone, config.sensor_limits)
        pilot.Pilot(drone=drone, config=config, camera=camera, logger=logger, server=server, emergency=emergency)

    # RUN LOOP
    if config.mode == "visiontest":
        font = cv.FONT_HERSHEY_SIMPLEX
        while True:
            cam_data = parent_conn.recv()
            detections = cam_data[1]
            camera.box = [detections[1], detections[2], detections[3], detections[4]]
            print(camera.box)
            camera.frame = cam_data[0]
            cv.putText(camera.frame, f"Conf: {detections[5]}", 
                (40,40),
                font,
                1,
                (255,255,255),
                2,
                2)
            cv.rectangle(camera.frame, (detections[1], detections[2]), (detections[3], detections[4]),(0, 255, 0))
            cv.imshow("frame", cam_data[0])
            if cv.waitKey(1) >= 0:
                break
            await asyncio.sleep(0.05)
            
    elif camera == None:
        while True: 
            await asyncio.sleep(0.05)

    elif config.cameramode == "stream":
        while True:
            cam_data = parent_conn.recv()
            camera.frame = cam_data[0]
            await asyncio.sleep(0.05)

    elif config.cameramode == "vision":
        while True:
            cam_data = parent_conn.recv()
            camera.frame = cam_data[0]
            detections = cam_data[1]
            camera.box = [detections[1], detections[2], detections[3], detections[4]]
            camera.confidence = detections[5]
            cv.rectangle(camera.frame, (detections[1], detections[2]), (detections[3], detections[4]),(0, 255, 0))
            await asyncio.sleep(0.05)

# RUN ASYNCIO
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())



