import requests
import asyncio
import time

class ServerHandler:
    def __init__(self, server_config):
        self.url = server_config['url']
        self.drone_id = server_config['drone_id']
        self.connected = False
        self.ready = False

    def make_handshake(self, data):
        i = 0
        while not self.connected and i < 5:
            i+=1
            url = f'{self.url}/handshake/{self.drone_id}/{data}'
            res = requests.get(url).text
            if res == 'success':
                self.connected = True
            time.sleep(1)
        if self.connected:
            print('SERVER: Vehicle connected')
        else:
            print('SERVER: Failed to connect')
    
    async def handle_ready(self, SensorsHandler):
        lat = SensorsHandler.position['lat']
        lon = SensorsHandler.position['lon']
        data = f'{lat}_{lon}_{SensorsHandler.heading}_{SensorsHandler.rel_alt}'
        self.make_handshake(data)
        while not self.ready:
            lat = SensorsHandler.position['lat']
            lon = SensorsHandler.position['lon']
            url = f'{self.url}/log/{self.drone_id}/{lat}_{lon}_{SensorsHandler.heading}_{SensorsHandler.rel_alt}'
            res = requests.get(url).text
            if res == "ready: 1":
                print("SERVER: ready")
                self.ready = True
                return
            await asyncio.sleep(0.1)

    async def handle_log(self, SensorsHandler):
        while self.connected:
            lat = SensorsHandler.position['lat']
            lon = SensorsHandler.position['lon']
            url = f'{self.url}/log/{self.drone_id}/{lat}_{lon}_{SensorsHandler.heading}_{SensorsHandler.rel_alt}'
            res = requests.get(url).text
            await asyncio.sleep(0.1)
        # SOME EMERGENCY LOGIC
        return
    
