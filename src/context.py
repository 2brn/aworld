from dataclasses import dataclass
from typing import TYPE_CHECKING

from pymavlink import mavutil

if TYPE_CHECKING:
    from states.base import BaseState


@dataclass
class Context:
    master: mavutil.mavfile
    altitude_m: float
    vel_up_mps: float
    altitude_changed: bool
    setpoint_altitude_m: float | None
    mode: str
    armed: bool
    arm_wait_logged: bool
    guided_started: float
    last_guided_send: float
    arm_started: float
    last_arm_send: float
    next_state: "BaseState | None"
    done: bool
    exit_code: int