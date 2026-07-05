from context import Context
from states.base import BaseState


class StateMachine:
    def __init__(self, telemetry_state: BaseState, initial_state: BaseState) -> None:
        self.telemetry_state = telemetry_state
        self.phase_state = initial_state

    def update(self, ctx: Context) -> None:
        ctx.altitude_changed = False
        ctx.setpoint_altitude_m = None
        self.telemetry_state.update(ctx)
        self.phase_state.update(ctx)
        next_state = ctx.next_state
        if next_state is not None:
            self.phase_state = next_state
            ctx.next_state = None