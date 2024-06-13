import asyncio, datetime
from data_classes import OffboardComand

class OffboardCommandsScenario:
    Logger = None
    def __init__(self, Pilot):
        self.Pilot = Pilot

    async def run(self):
        self.Pilot.Logger.log_debug("TEST: Offboard commands scenario")
        commands = [
            OffboardComand(6, 0, 0, -0.3, 0),
            OffboardComand(10, 1, 0, 0, 0),
            OffboardComand(19, 0, 0, 0, -10),
            OffboardComand(3, 0, -0.5, 0, 0),
            OffboardComand(15, 0.5, 0, 0, 0),
            OffboardComand(5, 0, 0, 0.5, 0)
        ]
        
        self.Pilot.update_command(commands[0])

    
        for command in commands:
            if self.Pilot.params.stage.name == "CAPTURE": break
            self.Pilot.update_command(command)

            while self.Pilot.params.offboard.command.timeout > datetime.datetime.now():
                await asyncio.sleep(0.05)

        # TODO Capturing
        while self.Pilot.params.stage.name == "CAPTURE":
            await asyncio.sleep(1)

        # await self.Pilot.OffboardHandler.finish_offboard()
        self.Pilot.Logger.log_debug("DRONE: landing")
        await self.Pilot.Drone.action.land()
        await asyncio.sleep(10)

