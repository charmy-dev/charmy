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
        self.parent: Container = parent
        self.parent.add_child(self)

        self._x: int | float = 0
        self._y: int | float = 0
        self._width: int | float = 0
        self._height: int | float = 0
        self.is_visible: bool = False
        self._draw_list: list = []

    @property
    def x(self) -> int | float:
        """x position of the widget."""
        return self._x

    @property
    def y(self) -> int | float:
        """y position of the widget."""
        return self._y

    @property
    def width(self) -> int | float:
        """Width of the widget."""
        return self._width

    @property
    def height(self) -> int | float:
        """Height of the widget."""
        return self._height

    def place(self, x: int | float, y: int | float, width: int | float = None, height: int | float = None):
        """Add the widget to window, using place layout"""
        self._x = x
        self._y = y
        if width is not None:
            self._width = width
        if height is not None:
            self._height = height

    def add_element(self, element):
        """Add an element to this widget's draw list."""
        self._draw_list.append(element)