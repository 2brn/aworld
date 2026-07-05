import logging
import time

from config import LAND_RETRY_S, LAND_TIMEOUT_S
from context import Context
from mavlink_utils import set_mode
from states.base import BaseState

logger = logging.getLogger(__name__)


class LandState(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.started_at: float | None = None
        self.last_send_at = 0.0

    def update(self, ctx: Context) -> None:
        now = time.monotonic()
        if self.started_at is None:
            self.started_at = now
            logger.info("Landing...")

        if ctx.mode == "LAND":
            logger.info("LAND mode confirmed")
            self.go_next(ctx)
            return

        if now - self.started_at > LAND_TIMEOUT_S:
            raise RuntimeError("Failed to switch to LAND mode in time")

        if now - self.last_send_at >= LAND_RETRY_S:
            set_mode(ctx.master, "LAND")
            self.last_send_at = now