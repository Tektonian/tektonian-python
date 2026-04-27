from __future__ import annotations

import math


def euler_to_quat(
    roll: float, pitch: float, yaw: float
) -> tuple[float, float, float, float]:
    """
    Args:
        roll (int): ψ: rotation about the X-axis
        pitch (int): θ: rotation about the new Y-axis
        yaw (int): ϕ: rotation about the new Z-axis
    Returns:
        tuple[float, float, float, float]: (x, y, z, w)

    References:
        https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Angles_(in_ZYX_sequence)_to_quaternion_conversion
    """

    zc = math.cos(roll * 0.5)
    zs = math.sin(roll * 0.5)
    yc = math.cos(pitch * 0.5)
    ys = math.sin(pitch * 0.5)
    xc = math.cos(yaw * 0.5)
    xs = math.sin(yaw * 0.5)

    w = zc * yc * xc + zs * ys * xs
    x = zs * yc * xc - zc * ys * xs
    y = zc * ys * xc + zs * yc * xs
    z = zc * yc * xs - zs * ys * xc

    return (x, y, z, w)
