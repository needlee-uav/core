import asyncio
from test_scenarios.soft_takeoff import SoftTakeoffScenario
from test_scenarios.offboard_commands import OffboardCommandsScenario
from test_scenarios.route_flight import RouteFlightScenario
from test_scenarios.vision_camera import VisionScenario
# 1: Soft takeoff and land
# 2: Test offboard commands
# 3: Test GPS route navigation
# 4: Test emergency
# 5: Test camera streaming
# 6: Test capturing
# 7: Test following
# 8: Test validating


class TestScenariosHandler:
    scenario = None
    def __init__(self, Pilot):
        self.Pilot = Pilot
        self.scenarios = [
            None,
            SoftTakeoffScenario(Pilot),
            OffboardCommandsScenario(Pilot),
            RouteFlightScenario(Pilot),
            None,
            VisionScenario(Pilot)
        ]
        asyncio.ensure_future(self.handle_scenarios())
        self.Pilot.Logger.log_debug("TEST: ready")

    async def handle_scenarios(self):
        while not self.Pilot.params.stage.name == "TEST":
            await asyncio.sleep(0.5)
        self.scenario = self.scenarios[int(self.Pilot.params.stage.test.id)]
        await self.scenario.run()
