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
import json
import re

from ..utils import geo_math
from .. import graphics as cm_draw

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

    @staticmethod
    def find_class_by_type(type_name: str) -> type[LinePath] | None:
        """Find a line class by line type, return `None` if not found.

        :param type_name: Line type in string
        """
        for cls in LinePath.__subclasses__():
            if cls.type == type_name:
                return cls
        else:
            return None

    @staticmethod
    def from_json(json_content: dict[str, typing.Any] | str) -> LinePath:
        """Create a shape object from json content.

        This function is a static method of LinePath and its subclasses. It creates and returns a 
        line object base on the JSON content given. This will be useful when loading line config 
        from styles.

        :param json_content: The JSON content, either Python dict or raw string data

        JSON Format
        -----------
        Lines can be represented in JSON in a structured way. Each JSON data must has a `type` key 
        that defines the type of the line, and also other keys and values that specify the params 
        for that line. The following is an example for polylines.

        .. code-block:: python
            {
            "type": "polyline", 
            "points": [
                (10, 10), (100, 50), (50, 100)
            ],
            }
        """
        # Convert raw content to JSON
        if isinstance(json_content, str):
            json_content = json.loads(json_content)
            assert type(json_content) is dict
            # 👆 Must assert the type here, because the fucking json module did not specify the 
            # type of the return value of loads()
        if not isinstance(json_content["type"], str):
            raise TypeError("Invalid line JSON.")
        cls = LinePath.find_class_by_type(json_content["type"])
        if cls is None:
            raise CharmyShapeError(f"Invalid line type {json_content["type"]}.")
        params = json_content.copy()
        params.pop("type")
        return cls(**params)


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
            (abs(self.points[1][0] - self.points[0][0]), abs(self.points[1][1] - self.points[0][1]))
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

    @property
    def boundary(self) -> ShapeRange:
        """Rectangle boundary of quadratic Bezier.

        This function was vibed with GitHub Copilot, model GPT-5 mini. 
        **No white box tests carried out so far.**

        Compute extrema by solving derivative = 0 for x and y separately, include
        t in (0,1) and endpoints.
        """
        p0, p1, p2 = self.points
        from ..utils.geo_math import evaluate_quadratic_bezier, quadratic_bezier_internal_t_roots

        candidate_points: list[tuple[int, int]] = [p0, p2]
        ts = quadratic_bezier_internal_t_roots((p0, p1, p2))
        for t in ts:
            x_f, y_f = evaluate_quadratic_bezier((p0, p1, p2), t)
            candidate_points.append((int(round(x_f)), int(round(y_f))))

        xs = [pt[0] for pt in candidate_points]
        ys = [pt[1] for pt in candidate_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return (min_x, min_y), (max_x - min_x, max_y - min_y)

@dataclass
class CubicBezier(LinePath):
    """Represents cubic Bezier curves.

    The Points
    ----------
    Almost ame as SVG path, you should give the points in order of:
        1. Starting point
        2. 1st control point
        3. 2nd control point
        4. Ending point

    :param points: List of the 3 points that determines the curve
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

    @property
    def boundary(self) -> ShapeRange:
        """Rectangle boundary of cubic Bezier using helpers in geo_math.
        
        This function was vibed by GitHub Copilot, model GPT-5 mini. 
        **No white box tests carried out so far.**
        """
        p0, p1, p2, p3 = self.points
        from ..utils.geo_math import (
            evaluate_cubic_bezier,
            cubic_bezier_derivative_roots,
        )

        candidate_points: list[tuple[int, int]] = [p0, p3]
        ts = cubic_bezier_derivative_roots((p0, p1, p2, p3))
        for t in ts:
            x_f, y_f = evaluate_cubic_bezier((p0, p1, p2, p3), t)
            candidate_points.append((int(round(x_f)), int(round(y_f))))

        xs = [pt[0] for pt in candidate_points]
        ys = [pt[1] for pt in candidate_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return (min_x, min_y), (max_x - min_x, max_y - min_y)


# region Shapes

class CharmyShapeError(Exception): ...
class CharmySVGIntepreterError(Exception): ...

class AnyShape():
    """Base class of all shapes."""
    type: typing.ClassVar[str] = "any_shape"

    def __init__(self, lines: typing.Sequence[LinePath | LineJSON]):
        """To initialize and validate a shape.

        :param lines: The lines that form the shape
        """
        
        self.lines: typing.Sequence[LinePath] = [
            # Append as-is or load from json
            line if isinstance(line, LinePath) else LinePath.from_json(line) \
                for line in lines
            ]
        if not self._validate_lines():
            warnings.warn("Specified lines do not form a valid closed shape.")

    @property
    def boundary(self) -> ShapeRange:
        """Rect range of a shape."""
        if len(self.lines) == 0:
            return (0, 0), (0, 0)
        line_boundaries = [line.boundary for line in self.lines]
        xs = [
            *[pos[0] for pos, size in line_boundaries], 
            *[pos[0] + size[0] for pos, size in line_boundaries], 
            ]
        ys = [
            *[pos[1] for pos, size in line_boundaries], 
            *[pos[1] + size[1] for pos, size in line_boundaries], 
            ]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return (min_x, min_y), (max_x - min_x, max_y - min_y)

    def _validate_lines(self):
        """Validate if lines form a valid closed shape."""
        if len(self.lines) == 0:
            return True
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
                return cls
        else:
            return None

    @staticmethod
    def from_json(json_content: dict[str, typing.Any] | str) -> AnyShape:
        """Create a shape object from json content.

        This function is a static method of AnyShape and its subclasses. It creates and returns a 
        shape object base on the JSON content given. This will be useful when loading shape config 
        from styles.

        :param json_content: The JSON content, either Python dict or raw string data

        JSON Format
        -----------
        Shapes can be represented in JSON in a structured way. Each JSON data must has a `type` key 
        that defines the type of the shape, and also other keys and values that specify the params 
        for that shape. The following is an example for rectangles.

        .. code-block:: python
            {
            "type": "rect", 
            "pos": (50, 50), 
            "size": (100, 100), 
            }
        """
        # Convert raw content to JSON
        if isinstance(json_content, str):
            json_content = json.loads(json_content)
            assert type(json_content) is dict
            # 👆 Must assert the type here, because the fucking json module did not specify the 
            # type of the return value of loads()
        if not isinstance(json_content["type"], str):
            raise TypeError("Invalid shape JSON.")
        cls = AnyShape.find_class_by_type(json_content["type"])
        if cls is None:
            raise CharmyShapeError(f"Invalid shape type {json_content["type"]}.")
        params = json_content.copy()
        params.pop("type")
        return cls(**params)

@dataclass
class Rect(AnyShape):
    """Represents rectangles in Charmy.

    :param position: The position of the rectangle
    :param size: The size of the rectangle
    """
    type: typing.ClassVar[str] = "rect"

    pos: Point
    size: Size

    @property
    def lines(self) -> typing.Sequence[LinePath]:
        polyline = PolyLine([
            (self.pos[0], self.pos[1]), 
            (self.pos[0] + self.size[0], self.pos[1]), 
            (self.pos[0] + self.size[0], self.pos[1] + self.size[1]), 
            (self.pos[0], self.pos[1] + self.size[1]), 
            (self.pos[0], self.pos[1]), 
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

# Type LineJSON and ShapeJSON
LineJSON: typing.TypeAlias = dict
ShapeJSON: typing.TypeAlias = dict


# region SVG conversion

@staticmethod
def shapes_from_svg_path(svg_path: str, scale: float = 1) -> list[AnyShape]:
    """This converts SVG path into sequence of Charmy lines.

    I made a fucking complete SVG path intepreter man!!!   —— rgzz666 @ 26/05/16

    We assume that the SVG path that you give is valid, otherwise we will throw an error.

    :param svg_path: The SVG path in string 
    """

    def tokenize_svg_path(path_string):
        # This regex matches:
        # 1. Any SVG command letter: [a-zA-Z]
        # 2. Any integer/floating point number (including negatives): -?\d*\.?\d+
        token_pattern = re.compile(r'([a-zA-Z]|-?\d*\.?\d+)')
        # Find all matching tokens in the string
        tokens = token_pattern.findall(path_string)
        return tokens

    def calc_point(sections: list[str], curr: int, offset: int, relative: bool):
        point_x = float(sections[curr + offset])
        point_y = float(sections[curr + offset + 1])
        if relative:
            return pen_pos[0] + point_x, pen_pos[1] + point_y
        else:
            return point_x, point_y

    def scale_point(point: tuple[int | float, int | float], scale: float = scale) -> Point:
        return (
            int(round(point[0] * scale, 0)), int(round(point[1] * scale, 0))
            )

    def calc_s_curve(
            prev_curve: CubicBezier, 
            s_data: list[tuple[int, int]], 
            ) -> CubicBezier:
        """
        Calculates and returns a new CubicBezier object for an S/s command.
        
        :param prev_curve: The preceding CubicBezier object (in absolute coordinates).
        :param s_data: A list of 2 tuples representing the points provided to the S/s command:
                    [(cp2_x, cp2_y), (end_x, end_y)]
                    These can be absolute or relative depending on the `relative` flag.
        :param relative: True if the current command is lowercase 's', False if uppercase 'S'.
        """
        # 1. Extract the crucial points from the previous absolute curve
        # The end of the previous curve is the start (junction) of the new curve
        junc_x, junc_y = prev_curve.points[3]  
        old_cp2_x, old_cp2_y = prev_curve.points[2]
        # 2. Calculate the mirrored first control point (always absolute)
        # Formula: 2 * Junction - Old_Control_Point
        new_cp1_x = 2 * junc_x - old_cp2_x
        new_cp1_y = 2 * junc_y - old_cp2_y
        new_cp1 = (new_cp1_x, new_cp1_y)
        # 3. Unpack the incoming S/s command data
        s_cp2, s_end = s_data
        # 4. Resolve the S/s points to absolute coordinates if they are relative
        # if relative:
        #     abs_cp2 = (junc_x + s_cp2[0], junc_y + s_cp2[1])
        #     abs_end = (junc_x + s_end[0], junc_y + s_end[1])
        # else:
        abs_cp2 = s_cp2
        abs_end = s_end
        # 5. Construct and return the new absolute CubicBezier object
        # Order: [start, control_1, control_2, end]
        return CubicBezier([
            (junc_x, junc_y), 
            new_cp1, 
            abs_cp2, 
            abs_end
        ])

    sections: list[str] = tokenize_svg_path(svg_path)
    command_index: int = 0
    pen_pos: Point = (0, 0)
    lines: list[LinePath] = []
    shapes: list[AnyShape] = []
    while command_index < len(sections):
        command = sections[command_index]
        match command.upper():
            case "M": # MoveTo
                # End current shape
                if len(lines) > 0:
                    shapes.append(AnyShape(lines))
                    lines = []
                # Then set pos
                pen_pos = scale_point(calc_point(sections, command_index, 1, command.islower()))
                command_index += 3
            case "L" | "V" | "H": # LineTo
                dest: Point
                match command.upper():
                    case "L": # Any line
                        dest = scale_point(calc_point(
                            sections, command_index, 1, command.islower()))
                    case "V": # Vertical
                        dest = scale_point((
                            pen_pos[0], 
                            float(sections[command_index + 1]) + \
                                (pen_pos[1] if command.isupper() else 0)
                            ))
                    case "H": # Horizontal
                        dest = scale_point((
                            float(sections[command_index + 1]) + \
                                (pen_pos[0] if command.isupper() else 0), 
                            pen_pos[1]
                            ))
                lines.append(Line([pen_pos, dest]))
                pen_pos = dest
                command_index += 3
            case "C" | "S": # Cubic Bezier
                if command.upper() == "S":
                    # Chained cubic Beziers (chained smooth curves)
                    if not isinstance(lines[-1], CubicBezier):
                        raise CharmySVGIntepreterError(
                            "An S command must follow a C command in SVG path."
                            )
                    lines.append(calc_s_curve(
                        lines[-1], 
                        [
                            scale_point(calc_point(sections, command_index, 1, command.islower())), 
                            scale_point(calc_point(sections, command_index, 3, command.islower()))
                        ], 
                        ))
                    command_index += 5
                else:
                    # Normal cubic Beziers
                    lines.append(CubicBezier([
                        pen_pos, 
                        scale_point(calc_point(sections, command_index, 1, command.islower())), 
                        scale_point(calc_point(sections, command_index, 3, command.islower())), 
                        scale_point(calc_point(sections, command_index, 5, command.islower())), 
                        ]))
                    command_index += 7
                pen_pos = lines[-1].end_point
            case "Z": # Close path
                # Close path
                lines.append(Line([pen_pos, lines[0].start_point]))
                # End current shape
                if len(lines) > 0:
                    shapes.append(AnyShape(lines))
                    lines = []
                # Then to next command
                command_index += 1
            case _:
                raise CharmySVGIntepreterError(f"Invalid or unsupported command: {command}.")
    return shapes


# endregion