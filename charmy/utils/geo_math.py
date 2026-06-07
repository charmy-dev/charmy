"""Geometry and math helpers extracted from `charmy.styles.shape`.

This module centralizes math utilities used for shapes: angle conversions,
circle-point computations, arc-to-bezier conversion, and angle coverage tests.

!! THIS IS A VIBED MODULE !!
----------------------------
This module was mostly vibed by GitHub Copilot, ChatGPT, and Google Gemini.
It includes geometric knowledge that the core devs (in 2026) have not learned
yet.

This module is impossible to be completed by three secondary school students
without the help from third-party, and here, in this era, we chose AI. We
provide no guarantee for codes this file.
"""

from __future__ import annotations

import math
from typing import List, Sequence, Tuple

Point = tuple[int, int]


def evaluate_quadratic_bezier(points: Sequence[Point], t: float) -> tuple[float, float]:
    """Evaluate a quadratic Bezier at parameter t (0..1).

    Returns (x, y) as floats.
    """
    start_point, control_point, end_point = points
    one_minus_t = 1.0 - t
    x = (
        one_minus_t * one_minus_t * start_point[0]
        + 2 * one_minus_t * t * control_point[0]
        + t * t * end_point[0]
    )
    y = (
        one_minus_t * one_minus_t * start_point[1]
        + 2 * one_minus_t * t * control_point[1]
        + t * t * end_point[1]
    )
    return x, y


def _unique_t_values(values: List[float], abs_tolerance: float = 1e-9) -> List[float]:
    """Return unique t values within abs_tolerance preserving order."""
    unique: List[float] = []
    for value in values:
        if not any(math.isclose(value, existing, abs_tol=abs_tolerance) for existing in unique):
            unique.append(value)
    return unique


def quadratic_bezier_internal_t_roots(points: Sequence[Point], eps: float = 1e-12) -> List[float]:
    """Return the list of unique t roots (0<t<1) where derivative in x or y is zero.

    This mirrors solving (p0 - 2*p1 + p2) * t = (p0 - p1) for each coordinate.
    """
    start_point, control_point, end_point = points
    candidate_ts: List[float] = []
    for coord_index in (0, 1):
        denom_coord = (
            start_point[coord_index] - 2 * control_point[coord_index] + end_point[coord_index]
        )
        if math.isclose(denom_coord, 0.0, abs_tol=eps):
            continue
        t_candidate = (start_point[coord_index] - control_point[coord_index]) / denom_coord
        if 0.0 < t_candidate < 1.0:
            candidate_ts.append(t_candidate)

    return _unique_t_values(candidate_ts, abs_tolerance=1e-9)


def evaluate_cubic_bezier(points: Sequence[Point], t: float) -> tuple[float, float]:
    """Evaluate a cubic Bezier at parameter t (0..1). Returns (x, y) floats."""
    start_point, control_point_first, control_point_second, end_point = points
    one_minus_t = 1.0 - t
    x = (
        (one_minus_t**3) * start_point[0]
        + 3 * (one_minus_t**2) * t * control_point_first[0]
        + 3 * one_minus_t * (t**2) * control_point_second[0]
        + (t**3) * end_point[0]
    )
    y = (
        (one_minus_t**3) * start_point[1]
        + 3 * (one_minus_t**2) * t * control_point_first[1]
        + 3 * one_minus_t * (t**2) * control_point_second[1]
        + (t**3) * end_point[1]
    )
    return x, y


def cubic_bezier_derivative_roots(points: Sequence[Point], eps: float = 1e-12) -> List[float]:
    """Return t roots (0<t<1) where derivative in x or y is zero.

    Solves quadratic 3*a t^2 + 2*b t + c = 0 for each coordinate, where
    a = -p0 + 3*p1 - 3*p2 + p3
    b = 3*(p0 - 2*p1 + p2)
    c = 3*(p1 - p0)
    """
    start_point, control_point_first, control_point_second, end_point = points
    candidate_ts: List[float] = []

    def compute_polynomial_coefficients(
        coord_start_value,
        coord_control_first,
        coord_control_second,
        coord_end_value,
    ):
        coeff_a = (
            -coord_start_value
            + 3 * coord_control_first
            - 3 * coord_control_second
            + coord_end_value
        )
        coeff_b = 3 * (coord_start_value - 2 * coord_control_first + coord_control_second)
        coeff_c = 3 * (coord_control_first - coord_start_value)
        return coeff_a, coeff_b, coeff_c

    for coord_index in (0, 1):
        coeff_a, coeff_b, coeff_c = compute_polynomial_coefficients(
            start_point[coord_index],
            control_point_first[coord_index],
            control_point_second[coord_index],
            end_point[coord_index],
        )
        deriv_coeff_A = 3 * coeff_a
        deriv_coeff_B = 2 * coeff_b
        deriv_coeff_C = coeff_c
        if math.isclose(deriv_coeff_A, 0.0, abs_tol=eps):
            # linear case: deriv_coeff_B * t + deriv_coeff_C = 0
            if not math.isclose(deriv_coeff_B, 0.0, abs_tol=eps):
                t_candidate = -deriv_coeff_C / deriv_coeff_B
                if 0.0 < t_candidate < 1.0:
                    candidate_ts.append(t_candidate)
            continue
        discriminant_val = deriv_coeff_B * deriv_coeff_B - 4 * deriv_coeff_A * deriv_coeff_C
        if discriminant_val < 0:
            continue
        sqrt_discriminant = math.sqrt(discriminant_val)
        root_candidate_plus = (-deriv_coeff_B + sqrt_discriminant) / (2 * deriv_coeff_A)
        root_candidate_minus = (-deriv_coeff_B - sqrt_discriminant) / (2 * deriv_coeff_A)
        for t_candidate in (root_candidate_plus, root_candidate_minus):
            if 0.0 < t_candidate < 1.0:
                candidate_ts.append(t_candidate)

    # unique with tolerance
    return _unique_t_values(candidate_ts, abs_tolerance=1e-9)


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


def arc_to_cubic_beziers(
    center: Point, radius: int, start_orient: int, end_orient: int
) -> List[List[Point]]:
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
    alpha = (4 / 3) * math.tan(segment_delta / 4)

    beziers: List[List[Point]] = []
    for i in range(segments):
        angle0 = start_rad + i * segment_delta
        angle1 = start_rad + (i + 1) * segment_delta
        cos0, sin0 = math.cos(angle0), math.sin(angle0)
        cos1, sin1 = math.cos(angle1), math.sin(angle1)

        p0 = (int(round(cx + radius * cos0)), int(round(cy - radius * sin0)))
        p3 = (int(round(cx + radius * cos1)), int(round(cy - radius * sin1)))

        p1 = (
            int(round(p0[0] + (alpha * radius * -sin0))),
            int(round(p0[1] - (alpha * radius * cos0))),
        )
        p2 = (
            int(round(p3[0] - (alpha * radius * -sin1))),
            int(round(p3[1] + (alpha * radius * cos1))),
        )

        beziers.append([p0, p1, p2, p3])

    return beziers


def flatten_circle_arc(
    center: Point,
    radius: int,
    start_orient: int,
    end_orient: int,
    tolerance: float = 15.0,
) -> List[Point]:
    """Flatten a circle arc into a polyline approximation.

    The returned list includes the start and end points of the arc.
    :param tolerance: Maximum allowed angle step between consecutive points, in degrees.
    """
    start_rad = gui_deg_to_math_rad(start_orient)
    end_rad = gui_deg_to_math_rad(end_orient)

    total_delta = end_rad - start_rad
    if total_delta > 0:
        total_delta -= 2 * math.pi
    if total_delta < -2 * math.pi:
        total_delta = -2 * math.pi

    if math.isclose(total_delta, 0.0, abs_tol=1e-12):
        return [
            point_on_circle(center, radius, start_orient),
            point_on_circle(center, radius, end_orient),
        ]

    segment_count = max(1, int(math.ceil(abs(total_delta) / math.radians(tolerance))))
    points: List[Point] = []
    for segment_index in range(segment_count + 1):
        angle = start_rad + segment_index * (total_delta / segment_count)
        gui_degree = 90 - math.degrees(angle)
        points.append(point_on_circle(center, radius, gui_degree))
    return points


def flatten_quadratic_bezier(
    points: Sequence[Point],
    tolerance: float = 15.0,
) -> List[Point]:
    """Flatten a quadratic Bezier curve into a polyline.

    :param tolerance: Approximate maximum angle between adjacent polyline segments, in degrees.
    """
    if tolerance <= 0:
        segments = 1
    else:
        segments = max(1, int(math.ceil(180.0 / tolerance)))
    result: List[Point] = []
    for i in range(segments + 1):
        t = i / segments
        x_f, y_f = evaluate_quadratic_bezier(points, t)
        result.append((int(round(x_f)), int(round(y_f))))
    return result


def flatten_cubic_bezier(
    points: Sequence[Point],
    tolerance: float = 15.0,
) -> List[Point]:
    """Flatten a cubic Bezier curve into a polyline.

    :param tolerance: Approximate maximum angle between adjacent polyline segments, in degrees.
    """
    if tolerance <= 0:
        segments = 1
    else:
        segments = max(1, int(math.ceil(180.0 / tolerance)))
    result: List[Point] = []
    for i in range(segments + 1):
        t = i / segments
        x_f, y_f = evaluate_cubic_bezier(points, t)
        result.append((int(round(x_f)), int(round(y_f))))
    return result
