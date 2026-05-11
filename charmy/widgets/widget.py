import typing

from . import window
from ..object import CharmyObject
from ..event import EventHandling
from .container import Container
from .. import styles


class Widget(CharmyObject, EventHandling):
    """Widget base class."""

    def __init__(self, parent: Container):
        super().__init__()
        # if parent is None:
        #     for window_ref in window.Window.instances:
        #         if window_ref() is not None:
        #             parent = window_ref()
        #     else:
        #         raise RuntimeError("No available window to put widget!")
        self.parent: Container = parent
        self.parent.add_child(self)

        self.pos: styles.shape.Point = (0, 0)
        self.size: styles.shape.Size = (0, 0)
        self.is_visible: bool = False
        self._draw_list: list = []

    @property
    def x(self) -> int:
        """x position of the widget."""
        return self.pos[0]

    @x.setter
    def x(self, new: int):
        self.pos = (new, self.pos[1])

    @property
    def y(self) -> int:
        """y position of the widget."""
        return self.pos[1]

    @x.setter
    def x(self, new: int):
        self.pos = (self.pos[0], new)

    @property
    def width(self) -> int:
        """Width of the widget."""
        return self.size[0]

    @width.setter
    def width(self, new: int):
        self.size = (new, self.size[1])

    @property
    def height(self) -> int:
        """Height of the widget."""
        return self.size[1]

    @height.setter
    def height(self, new: int):
        self.size = (self.size[0], new)

    def place(self, pos: styles.shape.Point, size: typing.Optional[styles.shape.Size] = None):
        """Add the widget to window, using place layout"""
        self.pos = pos
        if size is not None:
            self.size = size

    def add_element(self, element):
        """Add an element to this widget's draw list."""
        self._draw_list.append(element)