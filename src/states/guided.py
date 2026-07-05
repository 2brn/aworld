import logging
import time

from config import GUIDED_MODE, GUIDED_RETRY_S, GUIDED_TIMEOUT_S
from context import Context
from mavlink_utils import set_mode
from states.base import BaseState
from states.helpers import ensure_armed_or_switch_to_arm

logger = logging.getLogger(__name__)


class SetGuidedState(BaseState):
    def update(self, ctx: Context) -> None:
        if not ensure_armed_or_switch_to_arm(ctx):
            return

        if ctx.mode == GUIDED_MODE:
            logger.info("GUIDED mode confirmed")
            self.go_next(ctx)
            return

        now = time.monotonic()
        if now - ctx.guided_started > GUIDED_TIMEOUT_S:
            raise RuntimeError("Failed to switch to GUIDED mode in time")

        if now - ctx.last_guided_send >= GUIDED_RETRY_S:
            set_mode(ctx.master, GUIDED_MODE)
            logger.info("GUIDED mode command sent")
            ctx.last_guided_send = now
