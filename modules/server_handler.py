import requests
import asyncio
import time

class ServerHandler:
    def __init__(self):
        self.connected = False

    def make_handshake(self, data):
        i = 0
        while not self.connected and i < 5:
            i+=1
            url = f'http://127.0.0.1:5000/handshake/UAV-1234/{data}'
            res = requests.get(url).text
            if res == 'success':
                self.connected = True
            time.sleep(1)
        if self.connected:
            print('SERVER: Vehicle connected')
        else:
            print('SERVER: Failed to connect')
    
    async def handle_log(self, SensorsHandler):
        lat = SensorsHandler.position['lat']
        lon = SensorsHandler.position['lon']
        data = f'{lat}_{lon}_{SensorsHandler.heading}_{SensorsHandler.rel_alt}'
        self.make_handshake(data)
        while self.connected:
            lat = SensorsHandler.position['lat']
            lon = SensorsHandler.position['lon']
            url = f'http://127.0.0.1:5000/log/UAV-1234/{lat}_{lon}_{SensorsHandler.heading}_{SensorsHandler.rel_alt}'
            print(url)
            res = requests.get(url).text
            print(res)
            await asyncio.sleep(0.1)
        # SOME EMERGENCY LOGIC
        return
    
