import typing

from . import window
from ..object import CharmyObject
from ..event import EventHandling
from .container import Container
from .. import styles
from .. import graphics


class Widget(CharmyObject, EventHandling):
    """Widget base class."""

    def __init__(self, parent: Container, style: dict):
        """To initialize a widget.

        :param parent: Parent of tht widget
        :param style: Style of the widget
        """

        self._initialized: bool = False

        super().__init__()

        self.parent: Container = parent
        self.parent.add_child(self)

        self.style: dict = style

        self.pos: styles.shape.Point = (0, 0)
        self.size: styles.shape.Size = (0, 0)
        self.is_visible: bool = False

    def __post_init__(self):
        """After initialization of widget."""
        self._initialized = True
        self._update_draw_list()

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
    def root_container(self) -> window.Window | None:
        """Get the root container that contains the widget.

        :return window: Either the window, or None meaning that not contained in a root container
        """
        if isinstance(self.parent, window.Window):
            return self.parent
        else:
            if isinstance(self.parent, Widget):
                # If parent is widget, then get widget's root_container to trace root
                return self.parent.root_container
            else:
                # If not contained by neither a widget nor a root_container, …
                # … then the widget is not inside in a root container
                return None

    def _update_draw_list(self):
        """Update a widget's draw list, for internal use only.

        For widget base, this clears the draw list.
        """
        self._draw_list = []

    def __setattr__(self, name: str, value: typing.Any) -> None:
        """When changing attributes of a widget.

        Currently, updates the draw list of the widget after setting new attributes.

        :param name: Name of the attribute to set
        :param value: The new value
        """
        return_val = super().__setattr__(name, value)
        if not name.startswith("_"): # Skip internal vars to avoid endless recursion
            # (only do update for props changes)
            if self._initialized: # Skip update for initialization
                self._update_draw_list()
        return return_val

    def draw(self, 
            pos: styles.shape.Point, 
            size: typing.Optional[styles.shape.Size], 
            *args, **kwargs, 
            ) -> typing.Self:
        """Draw the widget, does nothing on base class."""
        if pos is not None:
            self.pos = pos
        if size is not None:
            self.size = size
        # for draw_object in self._draw_list:
        #     if self.root_container:
        #         if draw_object not in self.root_container.backend_base.drawing_list:
        #             draw_object.draw(self.root_container)
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