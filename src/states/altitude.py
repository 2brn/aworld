import logging
import time

from config import ALTITUDE_TOLERANCE_M, THRUST_SEND_HZ
from context import Context
from mavlink_utils import send_thrust
from states.base import BaseState
from states.helpers import ensure_armed_or_switch_to_arm
from thrust_altitude_controller import ThrustAltitudeController

logger = logging.getLogger(__name__)


class ReachAltitudeState(BaseState):
    def __init__(
        self,
        target_altitude_rel_m: float,
        hold_s: float | None = None,
        next_state: BaseState | None = None,
    ) -> None:
        super().__init__()
        self.target_altitude_rel_m = target_altitude_rel_m
        self.hold_s = hold_s
        self.next_state = next_state
        self.started_at: float | None = None
        self.last_status_log_at = 0.0
        self.last_thrust_send_at = 0.0
        self.controller = ThrustAltitudeController()

    def update(self, ctx: Context) -> None:
        if not ensure_armed_or_switch_to_arm(ctx):
            return

        now = time.monotonic()
        if self.hold_s is not None and self.started_at is None:
            self.started_at = now
            logger.info("HoldAltitude target=%.1fm hold_s=%.1f", self.target_altitude_rel_m, self.hold_s)

        ctx.setpoint_altitude_m = self.target_altitude_rel_m

        if now - self.last_thrust_send_at >= 1.0 / THRUST_SEND_HZ:
            current_thrust = self.controller.update(
                target_altitude_m=self.target_altitude_rel_m,
                altitude_m=ctx.altitude_m,
                vel_up_mps=ctx.vel_up_mps,
            )
            send_thrust(ctx.master, current_thrust)
            self.last_thrust_send_at = now

            if now - self.last_status_log_at >= 1.0:
                if self.hold_s is None:
                    logger.info(
                        "Altitude update: current=%.2fm target=%.2fm throttle=%.3f",
                        ctx.altitude_m,
                        self.target_altitude_rel_m,
                        current_thrust,
                    )
                else:
                    logger.info(
                        "Hold update: current=%.2fm target=%.2fm throttle=%.3f",
                        ctx.altitude_m,
                        self.target_altitude_rel_m,
                        current_thrust,
                    )
                self.last_status_log_at = now

        if self.hold_s is None:
            is_complete = abs(self.target_altitude_rel_m - ctx.altitude_m) <= ALTITUDE_TOLERANCE_M
            if is_complete:
                logger.info("Reached altitude %.1fm", self.target_altitude_rel_m)
        else:
            is_complete = self.started_at is not None and (now - self.started_at) >= self.hold_s
            if is_complete:
                logger.info("Hold complete %.1fm for %.1fs", self.target_altitude_rel_m, self.hold_s)

        if is_complete:
            self.go_next(ctx)
