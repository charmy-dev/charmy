"""Geometry and math helpers extracted from `charmy.styles.shape`.

This module centralizes math utilities used for shapes: angle conversions,
circle-point computations, arc-to-bezier conversion, and angle coverage tests.
"""
from __future__ import annotations

import math
from typing import Tuple, List

Point = tuple[int, int]

def gui_deg_to_math_rad(gui_deg: float) -> float:
    """Convert GUI degrees (0=North, clockwise) to math radians (0=East, CCW).

    This follows the conversion used in the original shape code.
    """
    return math.radians(90 - gui_deg)

def point_on_circle(center: Point, radius: int, gui_deg: float) -> Point:
    """Return the integer point on circle at GUI orientation degrees.

    GUI coordinate system: 0 degrees is up and angles increase clockwise.
    The returned point uses integer rounding consistent with the original code.
    """
    theta = math.radians(gui_deg - 90)
    x = center[0] + int(round(radius * math.cos(theta)))
    y = center[1] + int(round(radius * math.sin(theta)))
    return (x, y)

def is_angle_covered(target: float, start: float, end: float) -> bool:
    """Check whether target angle (degrees) lies within [start, end] in GUI CW system.

    Angles are normalized to 0..360. The function handles wrap-around ranges.
    """
    start_norm = start % 360
    end_norm = end % 360
    target_norm = target % 360
    if start_norm <= end_norm:
        return start_norm <= target_norm <= end_norm
    else:
        return target_norm >= start_norm or target_norm <= end_norm

def arc_to_cubic_beziers(center: Point, radius: int, start_orient: int, end_orient: int) -> List[List[Point]]:
    """Convert a circle arc (in GUI degrees) to a list of cubic Bezier point lists.

    Returns a list where each item is [p0, p1, p2, p3] with integer points.
    This mirrors the logic from the original Shape module.
    """
    cx, cy = center
    start_rad = gui_deg_to_math_rad(start_orient)
    end_rad = gui_deg_to_math_rad(end_orient)

    total_delta = end_rad - start_rad
    if total_delta > 0:
        total_delta -= 2 * math.pi
    if total_delta < -2 * math.pi:
        total_delta = -2 * math.pi

    segments = max(1, int(math.ceil(abs(total_delta) / (math.pi / 2))))
    segment_delta = total_delta / segments
    alpha = (4/3) * math.tan(segment_delta / 4)

    beziers: List[List[Point]] = []
    for i in range(segments):
        angle0 = start_rad + i * segment_delta
        angle1 = start_rad + (i + 1) * segment_delta
        cos0, sin0 = math.cos(angle0), math.sin(angle0)
        cos1, sin1 = math.cos(angle1), math.sin(angle1)

        p0 = (int(round(cx + radius * cos0)), int(round(cy - radius * sin0)))
        p3 = (int(round(cx + radius * cos1)), int(round(cy - radius * sin1)))

        p1 = (int(round(p0[0] + (alpha * radius * -sin0))),
              int(round(p0[1] - (alpha * radius * cos0))))
        p2 = (int(round(p3[0] - (alpha * radius * -sin1))),
              int(round(p3[1] + (alpha * radius * cos1))))

        beziers.append([p0, p1, p2, p3])

    return beziers
