import asyncio

class StageHandler:
    def __init__(self, Pilot):
        # TODO, add timeout at switch stage
        self.capture_timeout = 0
        self.Pilot = Pilot
        self.stage = Pilot.params.stage
        self.target = Pilot.params.target
        asyncio.ensure_future(self.handle_stages())

    async def handle_stages(self):
        while True:
            if self.stage.emergency:
                self.switch_stage(stage="EMERGENCY")
                break
            elif self.stage.ready and self.stage.name == "PREARM":
                self.switch_stage(stage="TAKEOFF")
            elif self.stage.name == "TAKEOFF" and self.stage.in_air == True:
                self.switch_stage(stage="TEST" if self.Pilot.params.stage.test.run else "ROUTE")
            elif self.stage.name == "PREARM" or self.stage.name == "TAKEOFF":
                pass
            elif self.Pilot.params.box[0] != 0  and self.Pilot.config.capturing and (self.stage.name == "ROUTE" or self.stage.name == "TEST"):
                self.target.target_detected = True
                self.switch_stage(stage="CAPTURE")
            elif not self.target.target_detected and self.stage.name == "CAPTURE":
               self.switch_stage(stage="ROUTE")
            await asyncio.sleep(0.05)

    def switch_stage(self, stage):
        self.stage.name = stage
        self.Pilot.Logger.log_debug(f"STAGE: {stage}")
