import typing

from . import window
from ..object import CharmyObject
from ..event import EventHandling
from .container import Container
from .. import styles


class Widget(CharmyObject, EventHandling):
    """Widget base class."""

    def __init__(self, parent: Container, style: dict):
        super().__init__()
        # DEPRECATED: Auto find parent for widgets
        # if parent is None:
        #     for window_ref in window.Window.instances:
        #         if window_ref() is not None:
        #             parent = window_ref()
        #     else:
        #         raise RuntimeError("No available window to put widget!")
        self.parent: Container = parent
        self.parent.add_child(self)

        self.style: dict = style

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

    @property
    def root_container(self) -> Container | None:
        """Get the root container that contains the widget.

        :return window: Either the window, or None meaning that not contained in a root container
        """
        if self.parent.is_root_container:
            return self.parent
        else:
            if isinstance(self.parent, Widget):
                # If parent is widget, then get widget's root_container to trace root
                return self.parent.root_container
            else:
                # If not contained by neither a widget nor a root_container, …
                # … then the widget is not inside in a root container
                return None

    def draw(self, 
            pos: styles.shape.Point, 
            size: typing.Optional[styles.shape.Size], 
            *args, **kwargs, 
            ) -> typing.Self:
        """Draw the widget, does nothing on base class."""
        if size is None:
            size = self.size
        self.draw_ext(pos, size, *args, **kwargs)
        return self

    def draw_ext(self, *args, **kwargs) -> typing.Any:
        """Extention of draw func. To be override by subclasses or users etc."""
        return None

    def place(self, 
            pos: styles.shape.Point, 
            size: typing.Optional[styles.shape.Size] = None, 
            ) -> typing.Self:
        """Add the widget to parent, using place layout.

        :param pos: The position to place the widget
        :param size: The size of this widget
        """
        self.pos = pos
        if size is not None:
            self.size = size
        return self

    def add_element(self, element):
        """Add an element to this widget's draw list."""
        self._draw_list.append(element)