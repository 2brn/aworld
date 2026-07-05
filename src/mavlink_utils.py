from pymavlink import mavutil


def arm_vehicle(master: mavutil.mavfile) -> None:
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
    )


def set_mode(master: mavutil.mavfile, mode_name: str) -> None:
    mode_map = master.mode_mapping()
    if not mode_map or mode_name not in mode_map:
        raise RuntimeError(f"Mode {mode_name} is not available")

    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_map[mode_name],
    )


def set_message_interval(master: mavutil.mavfile, message_id: int, interval_us: int) -> None:
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        0,
        message_id,
        interval_us,
        0,
        0,
        0,
        0,
        0,
    )


def send_thrust(master: mavutil.mavfile, thrust: float) -> None:
    type_mask = (
        mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_BODY_ROLL_RATE_IGNORE
        | mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_BODY_PITCH_RATE_IGNORE
        | mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_BODY_YAW_RATE_IGNORE
    )
    master.mav.set_attitude_target_send(
        0,
        1,
        1,
        type_mask,
        [1.0, 0.0, 0.0, 0.0],
        0.0,
        0.0,
        0.0,
        thrust,
    )