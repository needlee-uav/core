import asyncio

# 1: Soft takeoff and land no GPS
# 2: Test offboard commands
# 3: Test GPS route navigation
# 4: Test emergency
# 5: Test camera streaming
# 6: Test capturing
# 7: Test following

class TestScenariosHandler:
    scenario = None
    def __init__(self):
        pass

    async def handle_scenarios(self, ServerHandler, StageHandler, SensorsHandler, Drone):
        pass