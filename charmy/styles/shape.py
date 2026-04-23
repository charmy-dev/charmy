import typing

import warnings

from ..object import CharmyObject

if typing.TYPE_CHECKING:
    from ..backend.template import Backend
    from ..widgets.window import Window


# region Lines

class LinePath(CharmyObject):
    """Base class of all line paths"""

    def __init__(self, points: list[tuple[int, int]]):
        """Initialize the line.

        Args:
            points: List of points that determines the line.
        """
        super().__init__()

        self.type: str = "line_path_class"
        self.points: list[tuple[int, int]] = points

    def draw(self, window: Window):
        """Draw the line."""
        if self.type == "line_path_class":
            raise TypeError("LinePath class is a template, cannot be drawn.")
        else:
            if self.type in window.backend_base.backend.LineBase.supports:
                # If supported by the windows' backend.
                NotImplemented
            else:
                warnings.warn(f"Line type {self.type} is not supported by "
                              "backend {self.backend.friendly_name}")


class PolyLine(LinePath):
    """Represents polylines."""

    def __init__(self, **kwargs):
        """To create a polyline.

        Args:
            points: List of points that determines the line.
        """
        super().__init__(**kwargs)
        self.type = "polyline"

class Arc(LinePath):
    """Represents arcs."""

    def __init__(self, **kwargs):
        """To create an arc.

        Args:
            points: List of points that determines the line.
        """
        super().__init__(**kwargs)
        self.type = "arc"

class Beizer(LinePath):
    """Represents arcs."""

    def __init__(self, **kwargs):
        """To create a Beizer curve.

        Args:
            points: List of points that determines the line.
        """
        super().__init__(**kwargs)
        self.type = "beizer"

# endregion

# region Shapes

class CharmyShapeError(Exception):
    pass

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
        last_line_end: tuple[int, int] = self.lines[-1].points[-1]
        # 👆 Set last_line_end to end point of the last line, a valid shape must be closed.
        for line in self.lines:
            if line.points[0] != last_line_end:
                return False
            last_line_end = line.points[-1]
            # 👆 Set last_line_end to end point of current line, lines must be connected.
        return True

    def draw(self):
        """Draw the shape using backend."""
        NotImplemented

# endregion