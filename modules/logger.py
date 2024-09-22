import logging
import asyncio

class Logger:
    # self.debug_log = Pilot.params.debug_log
    # self.sensors = Pilot.params.sensors
    debug_log = []
    sensors = None

    def __init__(self, run):
        if run == "sim":
            logging.basicConfig(filename='main.log', filemode='w', format='%(levelname)s %(asctime)s - %(message)s', level=logging.DEBUG)
        elif run == "main":
            logging.basicConfig(filename='/home/jetson/Desktop/core/main.log', filemode='w', format='%(levelname)s %(asctime)s - %(message)s', level=logging.DEBUG)
        
        asyncio.ensure_future(self.log())
        self.log_debug("LOGGER: ready")

    async def log(self):
        while self.sensors == None:
            await asyncio.sleep(1)
        self.log_debug("LOGGER: sensors connected")
        while True:
            line = f"rel_alt:{self.sensors.position.alt}; heading:{self.sensors.heading}; lat:{self.sensors.position.lat}; lon:{self.sensors.position.lon}"
            self.log_info(line)
            await asyncio.sleep(1)

    def log_info(self, msg):
        logging.log(level=logging.INFO, msg=msg)

    def log_debug(self, msg):
        logging.log(level=logging.DEBUG, msg=msg)
        self.debug_log.append(msg)
