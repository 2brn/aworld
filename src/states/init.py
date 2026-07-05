import logging

from pymavlink import mavutil

from context import Context
from mavlink_utils import set_message_interval
from states.base import BaseState

logger = logging.getLogger(__name__)


class InitState(BaseState):
    def __init__(self, global_position_int_interval_us: int) -> None:
        super().__init__()
        self.global_position_int_interval_us = global_position_int_interval_us

    def update(self, ctx: Context) -> None:
        set_message_interval(
            ctx.master,
            mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
            self.global_position_int_interval_us,
        )
        logger.info("GLOBAL_POSITION_INT rate set to 1s")
        self.go_next(ctx)