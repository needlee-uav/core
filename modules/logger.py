import logging
import asyncio

class Logger:
    def __init__(self):
        logging.basicConfig(filename='main.log', filemode='w', format='%(levelname)s %(asctime)s - %(message)s', level=logging.DEBUG)
    
    async def log(self, SensorsHandler):
        while True:
            line = f"rel_alt:{SensorsHandler.rel_alt}; heading:{SensorsHandler.heading}; lat:{SensorsHandler.position['lat']}; lon:{SensorsHandler.position['lon']}"
            logging.info(line)
            await asyncio.sleep(1)

