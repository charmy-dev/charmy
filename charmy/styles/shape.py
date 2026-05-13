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
import inspect
from dataclasses import dataclass
import math
from ..utils import geo_math

from . import texture as cm_texture
from .. import draw as cm_draw

if typing.TYPE_CHECKING:
    from .texture import Texture, TextureLike
    from ..widgets.window import Window


# region Lines

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

    Coordinate System
    -----------------
    - 0° is at the top (positive Y direction)
    - Angles increase clockwise

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
        return geo_math.point_on_circle(self.center, self.radius, self.start_orient)

    @property
    def end_point(self) -> Point:
        return geo_math.point_on_circle(self.center, self.radius, self.end_orient)

    def fallback(self, _from: list[type[LinePath]] = []) -> typing.Sequence[LinePath]:
        """
        Simulates the circle arc using a sequence of Cubic Bezier curves.
        """
        if CubicBezier in _from:
            return LinePath.fallback(self, [*_from, self.__class__])
        beziers = geo_math.arc_to_cubic_beziers(
            self.center, self.radius, self.start_orient, self.end_orient)
        return [CubicBezier(b) for b in beziers]

    @property
    def boundary(self) -> ShapeRange:
        """Rect range of the circle arc.

        Calculation code written by Gemini, model: 3 Flash
        """
        considered_points: list[tuple[int, int]] = [self.start_point, self.end_point]
        extremes = [
            (0,   (self.center[0],               self.center[1] - self.radius)),
            (90,  (self.center[0] + self.radius, self.center[1])),
            (180, (self.center[0],               self.center[1] + self.radius)),
            (270, (self.center[0] - self.radius, self.center[1]))
        ]
        for angle, pt in extremes:
            if geo_math.is_angle_covered(angle, self.start_orient, self.end_orient):
                considered_points.append(pt)
        points_x = [p[0] for p in considered_points]
        points_y = [p[1] for p in considered_points]
        min_x, max_x = min(points_x), max(points_x)
        min_y, max_y = min(points_y), max(points_y)
        return (min_x, min_y), (max_x - min_x, max_y - min_y)

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
    type: typing.ClassVar[str] = "any_shape"

    def __init__(self, lines: typing.Sequence[LinePath]):
        """To initialize and validate a shape.

        :param lines: The lines that form the shape
        """
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

    @staticmethod
    def find_class_by_type(type_name: str) -> type[AnyShape] | None:
        """Find a shape class by shape type, return `None` if not found.

        :param type_name: Shape type in string
        """
        for cls in AnyShape.__subclasses__():
            if cls.type == type_name:
                return AnyShape
        else:
            return None

    @staticmethod
    def load_from_json(json_content: dict | str) -> AnyShape:
        """Create a shape object from json content.

        This function is a static method of AnyShape and its subclasses. It creates and returns a 
        shape object base on the JSON content given. This will be useful when loading shape config 
        from styles.

        :param json_content: The JSON content, either Python dict or raw string data

        JSON Format
        -----------
        Shapes can be represented in JSON in a structured way. The following will be the brief 
        introduction of the JSON structure, with values replaced with descriptive strings.

        .. code-block:: json
            {
            "type": "The type of the shape, in string", 
            "param 1": "Value of that parameter", 
            "param 2": "Value of that parameter", 
            }

        The detailed structure of each shape will be introduced in their classes' docstring. Here, 
        the detailed structure of defining a shape with type `any_shape`, which are shapes defined 
        by a sequence of `LinePath`s, will be introduced.

        .. code-block:: json
            {
            "type": "any_shape", 
            "lines": [
                {
                "type": "A line type", 
                "...": "See docs of `LinePath` to learn more about how to define a line with json…"
                }
            ]
            }
        """
        # TODO: Implement load shape by styles JSON
        return NotImplemented

@dataclass
class Rect(AnyShape):
    """Represents rectangles in Charmy.

    :param position: The position of the rectangle
    :param size: The size of the rectangle
    """
    type: typing.ClassVar[str] = "rect"

    position: Point
    size: Size

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

@dataclass
class RoundRect(AnyShape):
    """Represents round-corner rectangles in Charmy.

    :param position: The position of the round-corner rectangle
    :param size: The size of the round-corner rectangle
    :param radius: Radius of the round corners or of each corner, in px
    """
    type: typing.ClassVar[str] = "round_rect"

    position: Point
    size: Size
    radius: int | tuple[int, int, int, int]

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

# Type ShapeRange
ShapeRange: typing.TypeAlias = tuple[Point, Size]

# endregion