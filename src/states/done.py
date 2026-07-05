import logging

from config import LAND_COMPLETE_ALT_M
from context import Context
from states.base import BaseState

logger = logging.getLogger(__name__)


class DoneState(BaseState):
    def update(self, ctx: Context) -> None:
        if ctx.mode == "LAND" and (not ctx.armed) and ctx.altitude_m <= LAND_COMPLETE_ALT_M:
            logger.info("Landing complete")
            ctx.done = True
            ctx.exit_code = 0