import asyncio
from test_scenarios.soft_takeoff import SoftTakeoffScenario
from test_scenarios.offboard_commands import OffboardCommandsScenario
# 1: Soft takeoff and land no GPS
# 2: Test offboard commands
# 3: Test GPS route navigation
# 4: Test emergency
# 5: Test camera streaming
# 6: Test capturing
# 7: Test following
# 8: Test validating


class TestScenariosHandler:
    scenario = None
    def __init__(self):
        self.scenarios = [
            None,
            SoftTakeoffScenario(),
            OffboardCommandsScenario()
        ]

    async def handle_scenarios(self, ServerHandler, StageHandler, SensorsHandler, Drone):
        while ServerHandler.test_mode == None:
            await asyncio.sleep(0.3)
        self.scenario = self.scenarios[int(ServerHandler.test_mode)]
        await self.scenario.run(StageHandler=StageHandler, SensorsHandler=SensorsHandler, Drone=Drone)