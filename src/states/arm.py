import logging
import time

from config import ARM_RETRY_S, ARM_TIMEOUT_S
from context import Context
from mavlink_utils import arm_vehicle
from states.base import BaseState

logger = logging.getLogger(__name__)


class ArmState(BaseState):
    def update(self, ctx: Context) -> None:
        if ctx.armed:
            logger.info("Vehicle armed")
            ctx.guided_started = time.monotonic()
            ctx.last_guided_send = 0.0
            self.go_next(ctx)
            return

        now = time.monotonic()
        if now - ctx.arm_started > ARM_TIMEOUT_S:
            raise RuntimeError("Vehicle did not arm in time")

        if not ctx.arm_wait_logged:
            logger.info("Waiting for arm")
            ctx.arm_wait_logged = True

        if now - ctx.last_arm_send >= ARM_RETRY_S:
            arm_vehicle(ctx.master)
            logger.info("ARM command sent")
            ctx.last_arm_send = now