import time

from context import Context
from states.base import BaseState


def ensure_armed_or_switch_to_arm(ctx: Context) -> bool:
    if ctx.armed:
        return True

    ctx.arm_started = time.monotonic()
    ctx.last_arm_send = 0.0

    from states.arm import ArmState

    BaseState.transition(ctx, ArmState())
    return False