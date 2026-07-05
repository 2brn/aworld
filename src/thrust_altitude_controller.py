import logging

from config import (
    ALT_KP,
    HOVER_THRUST,
    MAX_DOWN_ACCEL_MPS2,
    MAX_DOWN_SPEED_MPS,
    MAX_UP_ACCEL_MPS2,
    MAX_UP_SPEED_MPS,
    THRUST_SEND_HZ,
    VEL_INTEGRAL_MAX,
    VEL_INTEGRAL_MIN,
    VEL_KI,
    VEL_KP,
)
from utils import clamp

GRAVITY_MPS2 = 9.80665
logger = logging.getLogger(__name__)


class ThrustAltitudeController:
    def __init__(self) -> None:
        self.vel_integral = 0.0

    def update(self, target_altitude_m: float, altitude_m: float, vel_up_mps: float) -> float:
        altitude_error_m = target_altitude_m - altitude_m
        target_vel_up_mps = clamp(ALT_KP * altitude_error_m, -MAX_DOWN_SPEED_MPS, MAX_UP_SPEED_MPS)

        control_dt = 1.0 / THRUST_SEND_HZ

        vel_error_mps = target_vel_up_mps - vel_up_mps
        self.vel_integral = clamp(
            self.vel_integral + vel_error_mps * control_dt,
            VEL_INTEGRAL_MIN,
            VEL_INTEGRAL_MAX,
        )

        accel_up_cmd = VEL_KP * vel_error_mps + VEL_KI * self.vel_integral
        accel_up_cmd = clamp(accel_up_cmd, -MAX_DOWN_ACCEL_MPS2, MAX_UP_ACCEL_MPS2)

        thrust = HOVER_THRUST * (1.0 + accel_up_cmd / GRAVITY_MPS2)

        return thrust