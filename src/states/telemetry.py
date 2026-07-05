import logging

from pymavlink import mavutil

from context import Context
from states.base import BaseState

logger = logging.getLogger(__name__)


class TelemetryReadState(BaseState):
    def __init__(self, timeout_s: float) -> None:
        super().__init__()
        self.timeout_s = timeout_s

    def update(self, ctx: Context) -> None:
        msg = ctx.master.recv_match(blocking=True, timeout=self.timeout_s)
        if msg is None:
            return

        msg_type = msg.get_type()
        if msg_type == "GLOBAL_POSITION_INT":
            ctx.altitude_m = msg.relative_alt / 1000.0
            ctx.vel_up_mps = -(msg.vz / 100.0)
            ctx.altitude_changed = True
        elif msg_type == "HEARTBEAT":
            ctx.armed = True if (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) else False
            ctx.mode = ctx.master.flightmode or "UNKNOWN"
        elif msg_type == "STATUSTEXT":
            text = str(getattr(msg, "text", "")).strip()
            if text:
                logger.info("STATUSTEXT: %s", text)
