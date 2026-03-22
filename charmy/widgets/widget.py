import typing

from ..event import EventHandling
from ..rect import Rect
from .canvas import CanvasBase
from .container import Container, auto_find_parent


@auto_find_parent
class Widget(CanvasBase, EventHandling):
    """Basic widget class."""

    def __init__(self, parent: Container | None = None):
        super().__init__()

        if parent is None:
            parent = self.find("Window0", default=None)

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
