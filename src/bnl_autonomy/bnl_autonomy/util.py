from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class XY:
    x: float
    y: float


def yaw_to_quaternion(yaw_rad: float):
    """Return (x,y,z,w) quaternion for planar yaw."""
    half = 0.5 * float(yaw_rad)
    return (0.0, 0.0, math.sin(half), math.cos(half))


def normalize_angle(angle_rad: float) -> float:
    a = float(angle_rad)
    while a > math.pi:
        a -= 2.0 * math.pi
    while a < -math.pi:
        a += 2.0 * math.pi
    return a


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))
