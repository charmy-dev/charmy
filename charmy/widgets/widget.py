import typing

from . import window
from ..object import CharmyObject
from ..event import EventHandling
from ..rect import Rect
from .canvas import CanvasBase
from .container import Container


class Widget(CharmyObject, EventHandling):
    """Widget base class."""

    def __init__(self, parent: typing.Optional[Container] = None):
        super().__init__()
        if parent is None:
            for window_ref in window.Window.instances:
                if window_ref() is not None:
                    parent = window_ref()
            else:
                raise RuntimeError("No available window to put widget!")

    @property
    def x(self) -> int:
        """x position of the widget."""
        return 0

    @property
    def y(self) -> int:
        """y position of the widget."""
        return 0

    @property
    def width(self) -> int:
        """Width of the widget."""
        return 0

    @property
    def height(self) -> int:
        """Height of the widget."""
        return 0

    def place(self, x: int, y: int):
        """Add the widget to window, using place layout"""
        pass


# @auto_find_parent
class WidgetOld(CanvasBase, EventHandling):
    """Basic widget class."""

    def __init__(self, parent: Container | None = None):
        super().__init__()

        if parent is None:
            for window_ref in window.Window.instances:
                if window_ref() is not None:
                    parent = window_ref()
            else:
                raise RuntimeError("No available window to put widget!")

        self.parent: Container = parent
        self.rect = Rect()

        # Automatically add to parent's children list if parent exists
        if parent is not None:
            parent.add_child(self)

    @property
    def x(self) -> int | float:
        """Return the x position of the widget."""
        return self.rect.x

    @property
    def y(self) -> int | float:
        """Return the y position of the widget."""
        return self.rect.y

    @property
    def width(self) -> int | float:
        """Return the width of the widget."""
        return self.rect.width

    @property
    def height(self) -> int | float:
        """Return the height of the widget."""
        return self.rect.height

    def place(self, x, y, width, height) -> typing.Self:
        """Place the widget at the specified position and size.

        Place the widget at the specified position and size.

        Args:
            x (int | float): The x position of the widget.
            y (int | float): The y position of the widget.
            width (int | float): The width of the widget.
            height (int | float): The height of the widget.
        """
        self.rect.make_XYWH(x, y, width, height)
        return self
