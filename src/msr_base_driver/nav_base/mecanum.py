import math
from typing import List


def clamp(value: float, limit: float) -> float:
    if value > limit:
        return limit
    if value < -limit:
        return -limit
    return value


def twist_to_rpm(
    vx: float,
    vy: float,
    wz: float,
    wheel_radius_m: float,
    half_length_m: float,
    half_width_m: float,
    max_rpm: float,
    motor_signs: List[float],
) -> List[int]:
    # Standard mecanum inverse kinematics.
    # Wheel order here is A, B, C, D.
    k = half_length_m + half_width_m

    wheel_rad_s = [
        (vx - vy - k * wz) / wheel_radius_m,
        (vx + vy + k * wz) / wheel_radius_m,
        (vx + vy - k * wz) / wheel_radius_m,
        (vx - vy + k * wz) / wheel_radius_m,
    ]

    rpm = [w * 60.0 / (2.0 * math.pi) for w in wheel_rad_s]

    signed = []
    for i, value in enumerate(rpm):
        sign = motor_signs[i] if i < len(motor_signs) else 1.0
        signed.append(int(round(clamp(value * sign, max_rpm))))

    return signed
