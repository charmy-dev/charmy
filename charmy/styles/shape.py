import typing

import warnings
from dataclasses import dataclass

from ..object import CharmyObject

if typing.TYPE_CHECKING:
    from ..backend.template import Backend
    from ..widgets.window import Window


# region Lines

@dataclass
class LinePath():
    """Base class of all line paths"""

    type: typing.ClassVar[str] = "line_path_class"

    def draw(self, window: Window):
        """Draw the line."""
        backend = window.backend_base.backend
        # 👆 Alias to avoid path to backend properties getting too long. 😅
        if self.type == "line_path_class":
            raise TypeError("LinePath class is a template, cannot be drawn.")
        else:
            if self.type in backend.LineBase.supports:
                # If supported by the windows' backend.
                backend.draw_line(self, window)
                NotImplemented
            else:
                warnings.warn(f"Line type {self.type} is not supported by "
                              f"backend {backend.friendly_name}")

    @property
    def start_point(self) -> tuple[int, int]:
        raise NotImplementedError

    @property
    def end_point(self) -> tuple[int, int]:
        raise NotImplementedError


@dataclass
class Line(LinePath):
    """Represents lines.

    Args:
        points: List of the 2 points that determines the line
    """
    type: typing.ClassVar[str] = "line"
    points: list[tuple[int, int]]

    def __post_init__(self):
        if len(self.points) != 2:
            raise ValueError("A line must be defined with and only with 2 points.")

    @property
    def start_point(self) -> tuple[int, int]:
        return self.points[0]

    @property
    def end_point(self) -> tuple[int, int]:
        return self.points[-1]

@dataclass
class PolyLine(LinePath):
    """Represents polylines.

    Args:
        points: List of points that determines the line(s)
    """
    type: typing.ClassVar[str] = "polyline"
    points: list[tuple[int, int]]

    def __post_init__(self):
        if len(self.points) <= 1:
            raise ValueError("At least 2 points are required to form a (poly)line.")
        elif len(self.points) == 2:
            warnings.warn(
                "Consider using Line for exactly 2 points (although using PolyLine still works).",
                stacklevel=2
            )

    @property
    def start_point(self) -> tuple[int, int]:
        return self.points[0]

    @property
    def end_point(self) -> tuple[int, int]:
        return self.points[-1]

@dataclass
class CircleArc(LinePath):
    """Represents circle arcs.

    Args:
        center: Coordinates of the center of the circle
        radius: Radius of the circle, in integer
        start_orient: Starting orientation in integer degrees
        end_orient: Ending orientation in integer degrees
    """
    center: tuple[int, int]
    type: typing.ClassVar[str] = "circle_arc"
    radius: int
    start_orient: int
    end_orient: int

@dataclass
class EllipseArc(LinePath):
    """Represents arcs trimmed from ellipses.

    Args:
        center: Coordinates of the center of the oval
        v_radius: Vertical radius in integer
        h_radius: Horizontal radius in integer
        rotation: Rotation in integer degrees
        start_orient: Starting orientation in integer degrees
        end_orient: Ending orientation in integer degrees
    """
    center: tuple[int, int]
    type: typing.ClassVar[str] = "ellipse_arc"
    v_radius: int
    h_radius: int
    rotation: int
    start_orient: int
    end_orient: int

    def __post_init__(self):
        if not -360 < self.rotation < 360:
            self.rotation = self.rotation % 360

@dataclass
class QuadraticBezier(LinePath):
    """Represents quadratic Bezier curves."""
    type: typing.ClassVar[str] = "quadratic_bezier"
    points: list[tuple[int, int]]

    def __post_init__(self):
        if len(self.points) != 3:
            raise ValueError("Quadratic Bezier curves must be defined with and only with 3 points!")

    @property
    def start_point(self) -> tuple[int, int]:
        return self.points[0]

    @property
    def end_point(self) -> tuple[int, int]:
        return self.points[-1]

@dataclass
class CubicBezier(LinePath):
    """Represents cubic Bezier curves."""
    type: typing.ClassVar[str] = "cubic_bezier"
    points: list[tuple[int, int]]

    def __post_init__(self):
        if len(self.points) != 4:
            raise ValueError("Cubic Bezier curves must be defined with and only with 4 points!")

    @property
    def start_point(self) -> tuple[int, int]:
        return self.points[0]

    @property
    def end_point(self) -> tuple[int, int]:
        return self.points[-1]

# endregion

# region Shapes

class CharmyShapeError(Exception): ...

class AnyShape(CharmyObject):
    """Base class of all shapes."""

    def __init__(self, lines: list[LinePath]):
        """To represent a shape.

        Args:
            lines: List of lines forming the shape.
        """
        super().__init__()

        self.lines: list[LinePath] = lines

        if not self._validate_lines():
            raise CharmyShapeError("Specified lines do not form a valid closed shape.")

    def _validate_lines(self):
        """Validate if lines form a valid closed shape."""
        last_line_end: tuple[int, int] = self.lines[-1].end_point
        # 👆 Set last_line_end to end point of the last line, a valid shape must be closed.
        for line in self.lines:
            if line.start_point != last_line_end:
                return False
            last_line_end = line.end_point
            # 👆 Set last_line_end to end point of current line, lines must be connected.
        return True

    def draw(self):
        """Draw the shape using backend."""
        NotImplemented

# endregion