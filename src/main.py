import argparse
import logging
import os
import time

from pymavlink import mavutil

from config import GLOBAL_POSITION_INT_INTERVAL_US, HEARTBEAT_TIMEOUT_S, TELEMETRY_TIMEOUT_S
from context import Context
from plot import LiveAltitudePlot
from config import MISSION_ALT_DESCEND_M, MISSION_ALT_REACH_UP_M, MISSION_HOLD_S
from states.arm import ArmState
from states.done import DoneState
from states.guided import SetGuidedState
from states.init import InitState
from states.land import LandState
from states.altitude import ReachAltitudeState
from state_machine import StateMachine
from states.telemetry import TelemetryReadState

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--connect", default="tcp:127.0.0.1:5760")
    parser.add_argument(
        "--log-level",
        default="INFO",
        type=str.upper,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    plotter: LiveAltitudePlot | None = None

    try:
        logger.info("Connecting to %s", args.connect)
        master = mavutil.mavlink_connection(args.connect)
        heartbeat = master.wait_heartbeat(timeout=HEARTBEAT_TIMEOUT_S)
        if heartbeat is None:
            raise RuntimeError("Heartbeat timeout: SITL is not ready")

        logger.info(
            "Heartbeat received: system=%s component=%s",
            master.target_system,
            master.target_component,
        )

        now = time.monotonic()
        ctx = Context(
            master=master,
            altitude_m=0.0,
            vel_up_mps=0.0,
            altitude_changed=False,
            setpoint_altitude_m=None,
            mode=master.flightmode or "UNKNOWN",
            armed=False,
            arm_wait_logged=False,
            guided_started=now,
            last_guided_send=0.0,
            arm_started=now,
            last_arm_send=0.0,
            next_state=None,
            done=False,
            exit_code=0,
        )

        telemetry_state = TelemetryReadState(timeout_s=TELEMETRY_TIMEOUT_S)
        phase_chain = (
            InitState(global_position_int_interval_us=GLOBAL_POSITION_INT_INTERVAL_US)
            .then(ArmState())
            .then(SetGuidedState())
            .then(ReachAltitudeState(target_altitude_rel_m=MISSION_ALT_REACH_UP_M))
            .then(ReachAltitudeState(target_altitude_rel_m=MISSION_ALT_REACH_UP_M, hold_s=MISSION_HOLD_S))
            .then(ReachAltitudeState(target_altitude_rel_m=MISSION_ALT_DESCEND_M))
            .then(ReachAltitudeState(target_altitude_rel_m=MISSION_ALT_DESCEND_M, hold_s=MISSION_HOLD_S))
            .then(LandState())
            .then(DoneState())
        )
        state_machine = StateMachine(
            telemetry_state=telemetry_state,
            initial_state=phase_chain,
        )

        try:
            plotter = LiveAltitudePlot()
            logger.info("Live altitude plot enabled")
        except Exception:
            logger.info("Live plot disabled: matplotlib backend is unavailable")
            plotter = None

        while True:
            state_machine.update(ctx)

            if plotter is not None:
                plotter.update(
                    ctx.altitude_m,
                    ctx.setpoint_altitude_m,
                    ctx.altitude_changed,
                )

            if ctx.done:
                return ctx.exit_code

    except KeyboardInterrupt:
        logger.info("Stopped by user")
        return 0

    except Exception as ex:
        logger.error("Failed to connect to SITL: %s", ex)
        return 1

    finally:
        if plotter is not None:
            plotter.close()


if __name__ == "__main__":
    raise SystemExit(main())
