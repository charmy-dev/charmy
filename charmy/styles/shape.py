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

import typing as _typing

import warnings as _warnings
from dataclasses import dataclass as _dataclass
from abc import abstractmethod as _abstractmethod
import json as _json
import reactive_caching as _reactive_caching

from ..utils import geo_math as _geo_math


# region Lines

class LinePath(_reactive_caching.CachedClass):
    """Base class of all line paths."""

    type: _typing.ClassVar[str] = "line_path_class"

    def __init__(self):
        super().__init__()

    @property
    def start_point(self) -> Point:
        raise NotImplementedError

    @property
    def end_point(self) -> Point:
        raise NotImplementedError

    def fallback(self, _from: list[type[LinePath]] = []) -> list[LinePath]:
        """Fallback ability of the line. For final fallback, warn that the line cannot be drawn.

        :param _from: Fallback path, for internal use
        :return value: Alternative sequence of lines that represents or simulate the same line
        """
        _warnings.warn(f"Line type {self.type} could not be drawn in any alternative method.")
        return []

    @property
    def boundary(self) -> ShapeRange:
        """Rectangle boundary of the line."""
        _warnings.warn(f"Line type {self.type} does not support getting boundary.")
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
    def from_json(json_content: dict[str, _typing.Any] | str) -> LinePath:
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
            json_content = _json.loads(json_content)
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


@_dataclass
class Line(LinePath):
    """Represents lines.

    :param points: List of the 2 points that determines the line
    """
    type: _typing.ClassVar[str] = "line"
    points: list[Point]

    def __post_init__(self):
        """Init parent class and validate number of points"""
        super().__init__()
        if len(self.points) != 2:
            raise ValueError("A line must be defined with and only with 2 points.")

    def fallback(self, _from: list[type[LinePath]] = []) -> list[LinePath]:
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

    def to_polyline(self) -> PolyLine:
        """Convert line to polyline."""
        return PolyLine(self.points)

    @property
    def start_point(self) -> Point:
        return self.points[0]

    @property
    def end_point(self) -> Point:
        return self.points[-1]

    @_reactive_caching.cached_property(["points"])
    def boundary(self) -> ShapeRange:
        """Rectangle boundary of single-section line."""
        return (
            (min(self.points[0][0], self.points[1][0]), min(self.points[0][1], self.points[1][1])), 
            (abs(self.points[1][0] - self.points[0][0]), abs(self.points[1][1] - self.points[0][1]))
            )

@_dataclass
class PolyLine(LinePath):
    """Represents polylines.

    :param points: List of points that determines the line(s)
    """
    type: _typing.ClassVar[str] = "polyline"
    points: list[Point]

    def __post_init__(self):
        """Init parent class and validate number of points"""
        super().__init__()
        if len(self.points) <= 1:
            raise ValueError("At least 2 points are required to form a (poly)line.")
        # elif len(self.points) == 2:
        #     warnings.warn(
        #         "Consider using Line for exactly 2 points (although using PolyLine still works).",
        #         stacklevel=2
        #     )

    def fallback(self, _from: list[type[LinePath]] = []) -> _typing.Sequence[LinePath]:
        """Convert polyline to list of lines.

        :param _from: Fallback path, for internal use
        :return value: Alternative sequence of lines that represents or simulate the same line
        """
        # If backend not supports polyline but supports line
        # Fall back to multiple lines if backend not supported
        if Line not in _from:
            return self.to_lines()
        else:
            return LinePath.fallback(self, [*_from, self.__class__])

    def to_lines(self) -> list[Line]:
        """Convert self to lines segments."""
        lines: list[Line] = []
        for point_index in range(len(self.points)):
            if point_index == 0:
                continue
            lines.append(Line([self.points[point_index - 1], self.points[point_index]]))
        return lines

    @staticmethod
    def join(lines: list[PolyLine | Line]) -> PolyLine:
        """Join multiple lines / polylines to one single polyline."""
        if len(lines) == 0:
            raise ValueError("Cannot join nothing into a polyline!")
        result_points = [lines[0].start_point]
        for line in lines:
            for index, point in enumerate(line.points):
                if index == 0:
                    continue
                result_points.append(point)
        return PolyLine(result_points)

    @property
    def start_point(self) -> Point:
        return self.points[0]

    @property
    def end_point(self) -> Point:
        return self.points[-1]

    @_reactive_caching.cached_property(["points"])
    def boundary(self) -> ShapeRange:
        """Rectangle boundary of polyline."""
        points_x: list[int] = [point[0] for point in self.points]
        points_y: list[int] = [point[1] for point in self.points]
        min_x, max_x = min(points_x), max(points_x)
        min_y, max_y = min(points_y), max(points_y)
        width = max_x - min_x
        height = max_y - min_y
        return (min_x, min_y), (width, height)

class Curve(LinePath):
    """Class representing curves, should not be used in rendering.

    Tips
    ----
    For self-defined curves, consider using sequence of quadratic Beziers.
    """

    def __init__(self) -> None:
        super().__init__()

    def draw(self):
        raise TypeError("Curve class is only used to classification, and cannot be drawn!")

    @_abstractmethod
    def flatten(self, tolerance: int = 15) -> PolyLine: ...

@_dataclass
class CircleArc(Curve):
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
    type: _typing.ClassVar[str] = "circle_arc"
    center: Point
    radius: int
    start_orient: int
    end_orient: int

    def __post_init__(self):
        """Init parent class."""
        super().__init__()

    @property
    def start_point(self) -> Point:
        return _geo_math.point_on_circle(self.center, self.radius, self.start_orient)

    @property
    def end_point(self) -> Point:
        return _geo_math.point_on_circle(self.center, self.radius, self.end_orient)

    def fallback(self, _from: list[type[LinePath]] = []) -> list[LinePath]:
        """
        Simulates the circle arc using a sequence of Cubic Bezier curves.
        """
        if CubicBezier in _from:
            return LinePath.fallback(self, [*_from, self.__class__])
        beziers = _geo_math.arc_to_cubic_beziers(
            self.center, self.radius, self.start_orient, self.end_orient)
        return [CubicBezier(b) for b in beziers]

    def flatten(self, tolerance: float = 15.0) -> PolyLine:
        """Flatten the circle arc into a PolyLine approximation."""
        points = _geo_math.flatten_circle_arc(
            self.center, self.radius, self.start_orient, self.end_orient,
            tolerance=tolerance)
        return PolyLine(points)

    @_reactive_caching.cached_property(["center", "radius", "start_orient", "end_orient"])
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
            if _geo_math.is_angle_covered(angle, self.start_orient, self.end_orient):
                considered_points.append(pt)
        points_x = [p[0] for p in considered_points]
        points_y = [p[1] for p in considered_points]
        min_x, max_x = min(points_x), max(points_x)
        min_y, max_y = min(points_y), max(points_y)
        return (min_x, min_y), (max_x - min_x, max_y - min_y)

@_dataclass
class EllipseArc(Curve):
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
    type: _typing.ClassVar[str] = "ellipse_arc"
    v_radius: int
    h_radius: int
    rotation: int
    start_orient: int
    end_orient: int

    def __post_init__(self):
        raise NotImplementedError("Ellipse arc is not fully implemented yet.")
        super().__init__()
        if not -360 < self.rotation < 360:
            self.rotation = self.rotation % 360

@_dataclass
class QuadraticBezier(Curve):
    """Represents quadratic Bezier curves.

    :param points: List of the 3 points that determines the curve.
    """
    type: _typing.ClassVar[str] = "quadratic_bezier"
    points: list[Point]

    def __post_init__(self):
        """Init parent class and validate number of points"""
        super().__init__()
        if len(self.points) != 3:
            raise ValueError("Quadratic Bezier curves must be defined with and only with 3 points!")

    @property
    def start_point(self) -> Point:
        return self.points[0]

    @property
    def end_point(self) -> Point:
        return self.points[-1]
    
    def fallback(self, _from: list[type[LinePath]] = []) -> list[LinePath]:
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

    def flatten(self, tolerance: float = 15.0) -> PolyLine:
        """Flatten the quadratic Bezier curve into a PolyLine approximation."""
        points = _geo_math.flatten_quadratic_bezier(self.points, tolerance)
        return PolyLine(points)

    @_reactive_caching.cached_property(["points"])
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

@_dataclass
class CubicBezier(Curve):
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
    type: _typing.ClassVar[str] = "cubic_bezier"
    points: list[Point]

    def __post_init__(self):
        """Init parent class and validate number of points"""
        super().__init__()
        if len(self.points) != 4:
            raise ValueError("Cubic Bezier curves must be defined with and only with 4 points!")

    @property
    def start_point(self) -> Point:
        return self.points[0]

    @property
    def end_point(self) -> Point:
        return self.points[-1]

    def flatten(self, tolerance: float = 15.0) -> PolyLine:
        """Flatten the cubic Bezier curve into a PolyLine approximation."""
        points = _geo_math.flatten_cubic_bezier(self.points, tolerance)
        return PolyLine(points)

    @_reactive_caching.cached_property(["points"])
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

class ShapeType(_reactive_caching.CachedClass):
    """Base class of shapes"""
    type: _typing.ClassVar[str] = "shape_type"

    def __init__(self, *args, **kwargs):
        super().__init__()

    @property
    @_abstractmethod
    def boundary(self) -> ShapeRange: ...

    @_abstractmethod
    def __contains__(self, point: Point) -> bool: ...

class SingleShape(ShapeType):
    """Base class of all shapes."""
    type: _typing.ClassVar[str] = "any_shape"

    def __init__(self):
        super().__init__()

    @property
    @_abstractmethod
    def lines(self) -> list[LinePath]: ...

    @_reactive_caching.cached_property(["lines"])
    def boundary(self) -> ShapeRange:
        """Rect range of a shape."""
        if len(self.lines) == 0:
            return (0, 0), (0, 0)
        line_boundaries = [line.boundary for line in self.lines]
        xs = [
            *[pos[0] for pos, _ in line_boundaries], 
            *[pos[0] + size[0] for pos, size in line_boundaries], 
            ]
        ys = [
            *[pos[1] for pos, _ in line_boundaries], 
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

    @staticmethod
    def find_class_by_type(type_name: str) -> type[SingleShape] | None:
        """Find a shape class by shape type, return `None` if not found.

        :param type_name: Shape type in string
        """
        for cls in SingleShape.__subclasses__():
            if cls.type == type_name:
                return cls
        else:
            return None

    @staticmethod
    def from_json(json_content: dict[str, _typing.Any] | str) -> SingleShape:
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
            json_content = _json.loads(json_content)
            assert type(json_content) is dict
            # 👆 Must assert the type here, because the fucking json module did not specify the 
            # type of the return value of loads()
        if not isinstance(json_content["type"], str):
            raise TypeError("Invalid shape JSON.")
        cls = SingleShape.find_class_by_type(json_content["type"])
        if cls is None:
            raise CharmyShapeError(f"Invalid shape type {json_content["type"]}.")
        params = json_content.copy()
        params.pop("type")
        return cls(**params)

    def flatten(self, tolerance: int = 15) -> PolyLine:
        """Convert all curve edges to polyline and merge the shape into a single polyline."""
        lines: list[Line | PolyLine] = []
        for line in self.lines:
            if isinstance(line, Curve):
                lines.append(line.flatten(tolerance))
            else:
                lines.append(line) # type: ignore
        return PolyLine.join(lines)

    def __contains__(self, point: Point) -> bool:
        """Perform a hit test and test if a point is within shape."""
        if not (
            self.boundary[0][0] < point[0] < self.boundary[0][0] + self.boundary[1][0] and \
            self.boundary[0][1] < point[1] < self.boundary[0][1] + self.boundary[1][1]
            ):
            # If not even in shape's bound box, skip the winding test
            return False
        point_x, point_y = point
        winding: int = 0
        shape_lines = self.flatten(30).to_lines()
        for line in shape_lines:
            if not line.boundary[0][1] <= point[1] <= line.boundary[0][1] + line.boundary[1][1] or \
                line.boundary[0][1] + line.boundary[1][1] < point[1]:
                # If the line's bbox doesn't even lies on the ray from target point
                continue # impossible to intersect with this line, so skip
            ## Winding test, vibed with ChatGPT Web (model GPT-5.3 Mini)
            start_x, start_y = line.start_point
            end_x, end_y = line.end_point
            # explicit horizontal edge skip (robustness)
            if start_y == end_y:
                continue
            if not (min(start_y, end_y) <= point_y < max(start_y, end_y)):
                continue
            cross = (
                (end_x - start_x) * (point_y - start_y)
                - (point_x - start_x) * (end_y - start_y)
            )
            if cross > 0:
                winding += 1
            elif cross < 0:
                winding -= 1
        return winding != 0

class AnyShape(SingleShape):
    """Shapes made up with sequence of lines."""

    def __init__(self, lines: _typing.Sequence[LinePath | LineJSON]):
        """To initialize and validate a shape.

        :param lines: The lines that form the shape
        """

        super().__init__()

        self._lines: _typing.List[LinePath] = [
            # Append as-is or load from json
            line if isinstance(line, LinePath) else LinePath.from_json(line) \
                for line in lines
            ]
        if not self._validate_lines():
            _warnings.warn("Specified lines do not form a valid closed shape.")

    @property
    def lines(self) -> list[LinePath]:
        return self._lines

@_dataclass
class Rect(SingleShape):
    """Represents rectangles in Charmy.

    :param position: The position of the rectangle
    :param size: The size of the rectangle
    """
    type: _typing.ClassVar[str] = "rect"

    pos: Point
    size: Size

    def __post_init__(self):
        """Init parent class."""
        super().__init__()

    @_reactive_caching.cached_property(["pos", "size"])
    def lines(self) -> list[LinePath]:
        polyline = PolyLine([
            (self.pos[0], self.pos[1]), 
            (self.pos[0] + self.size[0], self.pos[1]), 
            (self.pos[0] + self.size[0], self.pos[1] + self.size[1]), 
            (self.pos[0], self.pos[1] + self.size[1]), 
            (self.pos[0], self.pos[1]), 
            ])
        return [polyline]

    @_reactive_caching.cached_property(["pos", "size"])
    def boundary(self) -> ShapeRange:
        return self.pos, self.size

@_dataclass
class RoundRect(SingleShape):
    """Represents round-corner rectangles in Charmy.

    :param position: The position of the round-corner rectangle
    :param size: The size of the round-corner rectangle
    :param radius: Radius of the round corners or of each corner, in px
    """
    type: _typing.ClassVar[str] = "round_rect"

    pos: Point
    size: Size
    radius: int | tuple[int, int, int, int]

    def __post_init__(self):
        """Init parent class."""
        super().__init__()

    @_reactive_caching.cached_property(["position", "size", "radius"])
    def lines(self) -> list[LinePath]:
        radii: tuple[int, int, int, int]
        if isinstance(self.radius, int):
            radii = (self.radius, self.radius, self.radius, self.radius)
        else:
            radii = self.radius
        return [
            Line([
                (self.pos[0] + radii[0], self.pos[1]), # top-left
                (self.pos[0] + self.size[0] - radii[1], self.pos[1]) # top-right
                ]), 
            CircleArc( # top-right corner
                (self.pos[0] + self.size[0] - radii[1], self.pos[1] + radii[1]), 
                radii[1], 0, 90
                ), 
            Line([
                (self.pos[0] + self.size[0], self.pos[1] + radii[1]), # right-top
                (self.pos[0] + self.size[0], 
                 self.pos[1] + self.size[1] - radii[2]) # right-bottom
                ]), 
            CircleArc( # bottom-right corner
                (self.pos[0] + self.size[0] - radii[2], 
                 self.pos[1] + self.size[1] - radii[2]), 
                 radii[2], 90, 180
                 ), 
            Line([
                (self.pos[0] + self.size[0] - radii[2], 
                 self.pos[1] + self.size[1]), # bottom-right
                (self.pos[0] + radii[3], self.pos[1] + self.size[1]) # bottom-left
                ]), 
            CircleArc( # bottom-left
                (self.pos[0] + radii[3], self.pos[1] + self.size[1] - radii[3]), 
                radii[3], 180, 270
                ), 
            Line([
                (self.pos[0], self.pos[1] + self.size[1] - radii[3]), # left-bottom
                (self.pos[0], self.pos[1] + radii[0]) # left-top
                ]), 
            CircleArc(
                (self.pos[0] + radii[0], self.pos[1] + radii[0]), 
                radii[0], 270, 360
                )
            ]

    @_reactive_caching.cached_property(["pos", "size"])
    def boundary(self) -> ShapeRange:
        return self.pos, self.size

# region ShapeGroup
class ShapeGroup(ShapeType):
    """Complicated shapes formed by a group of AnyShape."""
    type: _typing.ClassVar[str] = "shape_group"

    def __init__(self, shapes: _typing.Sequence[AnyShape | ShapeGroup]) -> None:
        """To express a composite shape."""
        super().__init__()
        self._shapes: _typing.Sequence[AnyShape] = []
        self.shapes = shapes

    @property
    def shapes(self) -> _typing.Sequence[AnyShape]:
        """Shapes that make up this shape group"""
        return self._shapes

    @shapes.setter
    def shapes(self, new: _typing.Sequence[AnyShape | ShapeGroup]) -> None:
        self._shapes = []
        for shape in new:
            if isinstance(shape, ShapeGroup):
                for subshape in shape.shapes:
                    self._shapes.append(subshape)
            else:
                self._shapes.append(shape)

    @_reactive_caching.cached_property(["shapes"])
    def boundary(self) -> ShapeRange:
        """Rect range of a group of shape."""
        if len(self.shapes) == 0:
            return (0, 0), (0, 0)
        shape_boundaries = [shape.boundary for shape in self.shapes]
        xs = [
            *[pos[0] for pos, _ in shape_boundaries], 
            *[pos[0] + size[0] for pos, size in shape_boundaries], 
            ]
        ys = [
            *[pos[1] for pos, _ in shape_boundaries], 
            *[pos[1] + size[1] for pos, size in shape_boundaries], 
            ]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return (min_x, min_y), (max_x - min_x, max_y - min_y)

    def __getitem__(self, item: int) -> AnyShape:
        return self.shapes[item]

    def __iter__(self) -> _typing.Iterator[AnyShape]:
        return iter(self.shapes)

    def __len__(self) -> int:
        return len(self.shapes)

    def __contains__(self, obj: Point | AnyShape) -> bool:
        if isinstance(obj, AnyShape):
            return obj in self.shapes
        elif isinstance(obj, tuple):
            return True in [obj in shape for shape in self.shapes]
        else:
            raise TypeError("Can only judge either a point or a shape is in a shape group")

# region Type aliases

# Type Point / Coords
Point: _typing.TypeAlias = tuple[int, int]
Size: _typing.TypeAlias = tuple[int, int]

# Type ShapeRange
ShapeRange: _typing.TypeAlias = tuple[Point, Size]

# Type LineJSON and ShapeJSON
LineJSON: _typing.TypeAlias = dict[str, _typing.Any]
ShapeJSON: _typing.TypeAlias = dict[str, _typing.Any]


# region SVG conversion

from ..utils.svg import shapes_from_svg_path as from_svg_path

# endregion