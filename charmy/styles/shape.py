"""Charmy lines and shapes APIs.

This module implements Charmy's ability to express and draw lines and shapes.

Lines
-----
Lines are divided into following types: lines for straight lines, polylines, circle arcs, ellipse
arcs (not implemented), quadratic Bezier curves and cubic Bezier curves.

Each `LinePath` object can either be used to express a path, to be used to express a part of a 
shape, or to be drawn on a window directly. Paths expressed by lines may be used in animations in 
the future; shapes expressed by a list of lines can be drawn (see Shape section below); lines that 
are drawn directly are called `DrawnLine`, which can have their texture and line width be specified 
and adjusted.

Shapes
------
In Charmy, all shapes can be expressed by a sequence of lines. Shapes are divided into following
types: (...TO BE WRITTEN...). Backends that does not support drawing `any_shape` (line-sequence-
expressed shapes) will be able to draw some of the other shape types directly using its drawing 
module's API.

Each `Shape` object can either be used to express a shape of a widget or be drawn on a window. 
Shapes that are drawn on windows are called `DrawnShape`, which can have their inside texture, 
border width, and border texture be specified and adjusted.
"""

from __future__ import annotations as _

import typing

import warnings
from dataclasses import dataclass
import math

from . import texture as cm_texture
from .. import draw as cm_draw

if typing.TYPE_CHECKING:
    from .texture import Texture, TextureLike
    from ..widgets.window import Window


# region Lines

@dataclass
class LinePath():
    """Base class of all line paths."""

    type: typing.ClassVar[str] = "line_path_class"

    @property
    def start_point(self) -> Point:
        raise NotImplementedError

    @property
    def end_point(self) -> Point:
        raise NotImplementedError

    def draw(self, window: Window, texture: Texture | TextureLike, width: int = 5, 
             _fallback_from: list[type[LinePath]] = []) -> typing.Self:
        """Create DrawnLine object and draw the line.

        :param window: The window to draw line to
        :param texture: The texture of the line
        :param width: Line width in pixels
        :param _fallback_from: Fallback path, for internal use
        :return self: The LinePath object itself
        """
        # window.backend_base.drawing_list.append(DrawnLine(self, texture, width))
        warnings.warn("Directly drawing lines is not suggested, and may be removed in future.", 
                      DeprecationWarning, stacklevel=2)
        cm_draw.DrawnLine(self, texture, width).draw(window, _fallback_from)
        return self

    def fallback(self, _from: list[type[LinePath]] = []) -> typing.Sequence[LinePath]:
        """Fallback ability of the line. For final fallback, warn that the line cannot be drawn.

        :param _from: Fallback path, for internal use
        :return value: Alternative sequence of lines that represents or simulate the same line
        """
        warnings.warn(f"Line type {self.type} could not be drawn in any alternative method.")
        return []

    @property
    def boundary(self) -> ShapeRange:
        """Rectangle boundary of the line."""
        warnings.warn(f"Line type {self.type} does not support getting boundary.")
        return (0, 0), (0, 0)


@dataclass
class Line(LinePath):
    """Represents lines.

    :param points: List of the 2 points that determines the line
    """
    type: typing.ClassVar[str] = "line"
    points: list[Point]

    def __post_init__(self):
        if len(self.points) != 2:
            raise ValueError("A line must be defined with and only with 2 points.")

    def fallback(self, _from: list[type[LinePath]] = []) -> typing.Sequence[LinePath]:
        """Convert line to single polyline.

        :param _from: Fallback path, for internal use
        :return value: Alternative sequence of lines that represents or simulate the same line
        """
        # If backend not supports line but supports polyline
        # Fall back to polyline if backend not supported
        if PolyLine not in _from:
            return [PolyLine(self.points)]
        else:
            return LinePath.fallback(self, [*_from, self.__class__])

    @property
    def start_point(self) -> Point:
        return self.points[0]

    @property
    def end_point(self) -> Point:
        return self.points[-1]

    @property
    def boundary(self) -> ShapeRange:
        """Rectangle boundary of single-section line."""
        return (
            (min(self.points[0][0], self.points[1][0]), min(self.points[0][1], self.points[1][1])), 
            (self.points[1][0] - self.points[0][0], self.points[1][1] - self.points[0][1])
            )

@dataclass
class PolyLine(LinePath):
    """Represents polylines.

    :param points: List of points that determines the line(s)
    """
    type: typing.ClassVar[str] = "polyline"
    points: list[Point]

    def __post_init__(self):
        if len(self.points) <= 1:
            raise ValueError("At least 2 points are required to form a (poly)line.")
        # elif len(self.points) == 2:
        #     warnings.warn(
        #         "Consider using Line for exactly 2 points (although using PolyLine still works).",
        #         stacklevel=2
        #     )

    def fallback(self, _from: list[type[LinePath]] = []) -> typing.Sequence[LinePath]:
        """Convert polyline to list of lines.

        :param _from: Fallback path, for internal use
        :return value: Alternative sequence of lines that represents or simulate the same line
        """
        # If backend not supports polyline but supports line
        # Fall back to multiple lines if backend not supported
        if Line not in _from:
            lines: list[Line] = []
            for point_index in range(len(self.points)):
                if point_index == 0:
                    continue
                lines.append(Line([self.points[point_index - 1], self.points[point_index]]))
            return lines
        else:
            return LinePath.fallback(self, [*_from, self.__class__])

    @property
    def start_point(self) -> Point:
        return self.points[0]

    @property
    def end_point(self) -> Point:
        return self.points[-1]

    @property
    def boundary(self) -> ShapeRange:
        """Rectangle boundary of polyline."""
        points_x: list[int] = [point[0] for point in self.points]
        points_y: list[int] = [point[1] for point in self.points]
        min_x, max_x = min(points_x), max(points_x)
        min_y, max_y = min(points_y), max(points_y)
        width = max_x - min_x
        height = max_y - min_y
        return (min_x, min_y), (width, height)


@dataclass
class CircleArc(LinePath):
    """Represents circle arcs.

    :param center: Coordinates of the center of the circle
    :param radius: Radius of the circle, in integer
    :param start_orient: Starting orientation in integer degrees
    :param end_orient: Ending orientation in integer degrees
    """
    center: Point
    type: typing.ClassVar[str] = "circle_arc"
    radius: int
    start_orient: int
    end_orient: int

    @property
    def start_point(self) -> Point:
        # Vibed with GitHub Copilot, model GPT-5 mini
        # Compute start point from center, radius and start_orient (degrees).
        theta = math.radians(self.start_orient)
        x = self.center[0] + int(round(self.radius * math.cos(theta)))
        y = self.center[1] + int(round(self.radius * math.sin(theta)))
        return (x, y)

    @property
    def end_point(self) -> Point:
        # Vibed with GitHub Copilot, model GPT-5 mini
        # Compute end point from center, radius and end_orient (degrees).
        theta = math.radians(self.end_orient)
        x = self.center[0] + int(round(self.radius * math.cos(theta)))
        y = self.center[1] + int(round(self.radius * math.sin(theta)))
        return (x, y)

    def fallback(self, _from: list[type[LinePath]] = []) -> typing.Sequence[LinePath]:
        """Convert circle arc to Bezier curves.

        This function is vibed with ChatGPT.

        Coordinate system assumptions:
        - 0° is at the top (positive Y direction)
        - Angles increase clockwise

        :param _from: Fallback path, for internal use
        :return value: Alternative sequence of lines that represents or simulate the same line
        """
        if CubicBezier in _from:
            return LinePath.fallback(self, [*_from, self.__class__])

        # If fallback required, use cubic bezier to simulate
        cx, cy = self.center
        # --- Convert custom angle system to standard math radians ---
        # Math system: 0 rad at +X axis, CCW positive
        def to_math_rad(deg: float) -> float:
            return math.radians(90 - deg)
        start = to_math_rad(self.start_orient)
        end = to_math_rad(self.end_orient)
        # --- Ensure clockwise traversal ---
        # In math coordinates, clockwise means decreasing angle
        delta = end - start
        if delta > 0:
            delta -= 2 * math.pi
        # Clamp to at most one full circle
        if delta < -2 * math.pi:
            delta = -2 * math.pi
        # # Handle full circles
        # if self.start_orient == self.end_orient:
        #     delta = -2 * math.pi
        # --- Split into segments (max 90° each) ---
        max_step = math.pi / 2
        segments = max(1, int(math.ceil(abs(delta) / max_step)))
        step = delta / segments
        beziers: list[CubicBezier] = []
        for i in range(segments):
            t0 = start + i * step
            t1 = start + (i + 1) * step
            dt = t1 - t0
            # Cubic Bézier approximation factor
            alpha = 4 / 3 * math.tan(dt / 4)
            cos0, sin0 = math.cos(t0), math.sin(t0)
            cos1, sin1 = math.cos(t1), math.sin(t1)
            # For y coords, must use negative operations, because y-axis is reversed on a window
            # Endpoints
            x0: int = int(round(cx + self.radius * cos0, 0))
            y0: int = int(round(cy - self.radius * sin0, 0))
            x3: int = int(round(cx + self.radius * cos1, 0))
            y3: int = int(round(cy - self.radius * sin1, 0))
            # Tangent directions
            dx0, dy0 = -sin0, cos0
            dx1, dy1 = -sin1, cos1
            # Control points
            x1: int = int(round(x0 + alpha * self.radius * dx0, 0))
            y1: int = int(round(y0 - alpha * self.radius * dy0, 0))
            x2: int = int(round(x3 - alpha * self.radius * dx1))
            y2: int = int(round(y3 + alpha * self.radius * dy1))
            beziers.append(
                CubicBezier([(x0, y0), (x1, y1), (x2, y2), (x3, y3)])
                )
        return beziers

    @property
    def boundary(self) -> ShapeRange:
        """Rectangle boundary of polyline."""
        min_x = min(self.start_point[0], self.end_point[0])
        max_x = max(self.start_point[0], self.end_point[0])
        min_y = min(self.start_point[1], self.end_point[1])
        max_y = max(self.start_point[1], self.end_point[1])
        return (0, 0), (0, 0)

@dataclass
class EllipseArc(LinePath):
    """Represents arcs trimmed from ellipses.

    Note that this is NOT IMPLEMENTED and NOT PLANNED currently. 
    You may see this as avandoned codes.

    :param center: Coordinates of the center of the oval
    :param v_radius: Vertical radius in integer
    :param h_radius: Horizontal radius in integer
    :param rotation: Rotation in integer degrees
    :param start_orient: Starting orientation in integer degrees
    :param end_orient: Ending orientation in integer degrees
    """
    center: Point
    type: typing.ClassVar[str] = "ellipse_arc"
    v_radius: int
    h_radius: int
    rotation: int
    start_orient: int
    end_orient: int

    def __post_init__(self):
        raise NotImplementedError("Ellipse arc is not fully implemented yet.")
        if not -360 < self.rotation < 360:
            self.rotation = self.rotation % 360

@dataclass
class QuadraticBezier(LinePath):
    """Represents quadratic Bezier curves.

    :param points: List of the 3 points that determines the curve.
    """
    type: typing.ClassVar[str] = "quadratic_bezier"
    points: list[Point]

    def __post_init__(self):
        if len(self.points) != 3:
            raise ValueError("Quadratic Bezier curves must be defined with and only with 3 points!")

    @property
    def start_point(self) -> Point:
        return self.points[0]

    @property
    def end_point(self) -> Point:
        return self.points[-1]
    
    def fallback(self, _from: list[type[LinePath]] = []) -> typing.Sequence[LinePath]:
        """Convert quadratic Bezier curves to cubic.

        :param _from: Fallback path, for internal use
        :return value: Alternative sequence of lines that represents or simulate the same line
        """
        if CubicBezier not in _from:
            # Use cubic Beziers to express, vibed with ChatGPT
            p0, p1, p2 = self.points
            k = 2/3
            return [CubicBezier([
                p0,
                (int(round(p0[0] + k*(p1[0] - p0[0]), 0)), 
                    int(round(p0[1] + k*(p1[1] - p0[1]), 0))),
                (int(round(p2[0] + k*(p1[0] - p2[0]), 0)), 
                    int(round(p2[1] + k*(p1[1] - p2[1]), 0))),
                p2
            ])]
        else:
            return LinePath.fallback(self, [*_from, self.__class__])

@dataclass
class CubicBezier(LinePath):
    """Represents cubic Bezier curves.

    :param points: List of the 3 points that determines the curve.
    """
    type: typing.ClassVar[str] = "cubic_bezier"
    points: list[Point]

    def __post_init__(self):
        if len(self.points) != 4:
            raise ValueError("Cubic Bezier curves must be defined with and only with 4 points!")

    @property
    def start_point(self) -> Point:
        return self.points[0]

    @property
    def end_point(self) -> Point:
        return self.points[-1]


# region Shapes

class CharmyShapeError(Exception): ...

class AnyShape():
    """Base class of all shapes."""
    type: str = "any_shape"

    def __init__(self, lines: typing.Sequence[LinePath]):
        """To represent a shape.

        :param lines: List of lines forming the shape.
        """
        super().__init__()

        self.lines: typing.Sequence[LinePath] = lines

        if not self._validate_lines():
            raise CharmyShapeError("Specified lines do not form a valid closed shape.")

    def _validate_lines(self):
        """Validate if lines form a valid closed shape."""
        last_line_end: Point = self.lines[-1].end_point
        # 👆 Set last_line_end to end point of the last line, a valid shape must be closed.
        for line in self.lines:
            if line.start_point != last_line_end:
                return False
            last_line_end = line.end_point
            # 👆 Set last_line_end to end point of current line, lines must be connected.
        return True

    def draw(self, window: Window, texture: Texture | TextureLike, 
             border_width: int = 0, border_texture: Texture | TextureLike = None) -> typing.Self:
        """Draw the shape using backend.

        :param window: The window to draw shape to
        :param texture: Texture within the shape
        :param border_width: Width of borderline in px, positive for outer and negative for inner
        :param border_texture: Texture used on border
        """
        warnings.warn("Directly drawing shapes is not suggested, and may be removed in future.", 
                      DeprecationWarning, stacklevel=2)
        cm_draw.DrawnShape(self, texture, border_width, border_texture).draw(window)
        return self

class Rect(AnyShape):
    """Represents rectangles in Charmy."""
    type: str = "rect"

    def __init__(self, position: Point, size: Size):
        """To initialize a rectangle.
        
        :param position: The position of the rectangle
        :param size: The size of the rectangle
        """
        self.position: Point = position
        self.size: Size = size

    @property
    def lines(self) -> typing.Sequence[LinePath]:
        polyline = PolyLine([
            (self.position[0], self.position[1]), 
            (self.position[0] + self.size[0], self.position[1]), 
            (self.position[0] + self.size[0], self.position[1] + self.size[1]), 
            (self.position[0], self.position[1] + self.size[1]), 
            (self.position[0], self.position[1]), 
            ])
        return [polyline]

class RoundRect(AnyShape):
    """Represents round-corner rectangles in Charmy."""
    type: str = "round_rect"

    def __init__(self, position: Point, size: Size, radius: int | tuple[int, int, int, int]):
        """To initialize a round-corner rectangle.
        
        :param position: The position of the round-corner rectangle
        :param size: The size of the round-corner rectangle
        :param radius: Radius of the round corners or of each corner, in px
        """
        self.position: Point = position
        self.size: Size = size
        self.radius: int | tuple[int, int, int, int] = radius

    @property
    def lines(self) -> typing.Sequence[LinePath]:
        radii: tuple[int, int, int, int]
        if isinstance(self.radius, int):
            radii = (self.radius, self.radius, self.radius, self.radius)
        else:
            radii = self.radius
        return [
            Line([
                (self.position[0] + radii[0], self.position[1]), # top-left
                (self.position[0] + self.size[0] - radii[1], self.position[1]) # top-right
                ]), 
            CircleArc( # top-right corner
                (self.position[0] + self.size[0] - radii[1], self.position[1] + radii[1]), 
                radii[1], 0, 90
                ), 
            Line([
                (self.position[0] + self.size[0], self.position[1] + radii[1]), # right-top
                (self.position[0] + self.size[0], 
                 self.position[1] + self.size[1] - radii[2]) # right-bottom
                ]), 
            CircleArc( # bottom-right corner
                (self.position[0] + self.size[0] - radii[2], 
                 self.position[1] + self.size[1] - radii[2]), 
                 radii[2], 90, 180
                 ), 
            Line([
                (self.position[0] + self.size[0] - radii[2], 
                 self.position[1] + self.size[1]), # bottom-right
                (self.position[0] + radii[3], self.position[1] + self.size[1]) # bottom-left
                ]), 
            CircleArc( # bottom-left
                (self.position[0] + radii[3], self.position[1] + self.size[1] - radii[3]), 
                radii[3], 180, 270
                ), 
            Line([
                (self.position[0], self.position[1] + self.size[1] - radii[3]), # left-bottom
                (self.position[0], self.position[1] + radii[0]) # left-top
                ]), 
            CircleArc(
                (self.position[0] + radii[0], self.position[1] + radii[0]), 
                radii[0], 270, 360
                )
            ]


# region Type aliases

# Type Point / Coords
Point: typing.TypeAlias = tuple[int, int]
Size: typing.TypeAlias = tuple[int, int]

# Type Range
ShapeRange: typing.TypeAlias = tuple[Point, Size]

# endregion