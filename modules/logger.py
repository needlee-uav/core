import logging
import asyncio

class Logger:
    def __init__(self, WebSocketHandler):
        self.WebSocketHandler = WebSocketHandler
        self.debug = []
        logging.basicConfig(filename='main.log', filemode='w', format='%(levelname)s %(asctime)s - %(message)s', level=logging.DEBUG)

    async def log(self, SensorsHandler):
        while True:
            line = f"rel_alt:{SensorsHandler.rel_alt}; heading:{SensorsHandler.heading}; lat:{SensorsHandler.position['lat']}; lon:{SensorsHandler.position['lon']}"
            self.log_info(line)
            await asyncio.sleep(1)

    def log_info(self, msg):
        logging.log(level=logging.INFO, msg=msg)

    def log_debug(self, msg):
        logging.log(level=logging.DEBUG, msg=msg)
        self.WebSocketHandler.debug.append(msg)
