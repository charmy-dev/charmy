import typing

from . import window
from ..object import CharmyObject
from ..event import EventHandling
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