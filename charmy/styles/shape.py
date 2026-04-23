import typing

import warnings

from ..object import CharmyObject

if typing.TYPE_CHECKING:
    from ..backend.template import Backend
    from ..widgets.window import Window


# region Lines

class _LinePath(CharmyObject):
    """Base class of all line paths"""

    def __init__(self, window: Window, points: list[tuple[int, int]]):
        """Initialize the line.
        
        Args:
            points: List of points that determines the line.
            backend: The backend used
        """
        self.window: Window = window
        self.backend: Backend = self.window.backend_base.backend
        self.type: str = "line_path_class"
        self.points: list[tuple[int, int]] = points

    def draw(self, window):
        """Draw the line."""
        if self.type == "line_path_class":
            raise TypeError("_LinePath class is a template, cannot be drawn.")
        else:
            if self.type in self.backend.LineBase.supports:
                NotImplemented
            else:
                warnings.warn(f"Line type {self.type} is not supported by "
                              "backend {self.backend.friendly_name}")


class PolyLine(_LinePath):
    """Represents polylines."""

    def __init__(self, **kwargs):
        """To create a polyline."""
        super().__init__(**kwargs)
        self.type = "polyline"

class Arc(_LinePath):
    """Represents arcs."""

    def __init__(self, **kwargs):
        """To create an arc."""
        super().__init__(**kwargs)
        self.type = "arc"

class Beizer(_LinePath):
    """Represents arcs."""

    def __init__(self, **kwargs):
        """To create a Beizer curve."""
        super().__init__(**kwargs)
        self.type = "beizer"

# endregion

# region Shapes

class _Shape(CharmyObject):
    ...