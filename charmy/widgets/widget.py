"""Charmy widgets base class"""

import typing

from . import window
from ..object import CharmyObject
from ..event import EventHandling
from .container import Container, layout_profiles
from .. import styles


class Widget(CharmyObject, EventHandling):
    """Widget base class."""

    def __init__(self, parent: Container | None = None, style: dict = {":default": {"size": (0, 0)}}):
        """To initialize a widget.

        :param parent: Parent of the widget, or None in `with` context
        :param style: Style of the widget
        """

        if parent is None:
            if len(Container._with_stack) == 0:
                raise TypeError(
                    "Param parent can only be None within a with Container() context."
                    )
            else:
                parent = Container._with_stack[-1]

        self._initialized: bool = False

        super().__init__()

        self.parent: Container = parent
        self.parent.add_child(self)

        self.style: dict = style
        self.theme: typing.Optional[styles.theme.Theme] = None

        self.is_visible: bool = False
        self.layout_profile: layout_profiles.LayoutProfile = layout_profiles.LayoutProfile()

        self.state: str = "normal"

    def __post_init__(self):
        """After initialization of widget."""
        self._initialized = True
        self._update_drawing_objects()

    @property
    def pos(self) -> styles.shape.Point:
        """Position of the widget"""
        match self.layout_profile:
            case layout_profiles.PlaceProfile():
                return self.layout_profile.pos
            case _:
                return (0, 0)
        return (0, 0)

    @property
    def x(self) -> int:
        """x-position of the widget."""
        return self.pos[0]

    @property
    def y(self) -> int:
        """y-position of the widget."""
        return self.pos[1]

    @property
    def abs_pos(self) -> styles.shape.Point:
        """Absolute position of the widget in its root container."""
        if not isinstance(self.parent, window.WindowEntity):
            parent_pos = self.parent.pos
            self_pos = self.pos
            return (parent_pos[0] + self_pos[0], parent_pos[1] + self_pos[1])
        else:
            return self.pos

    @property
    def size(self) -> styles.shape.Size:
        """Size of the widget"""
        if self.layout_profile.final_size is not None:
            # If specified by layout
            return self.layout_profile.final_size
        else:
            # If not, get from style
            # curr_style = self.curr_state_styles
            target_style_state = self.state if self.state in self.style else "default"
            if not "size" in self.style[f":{target_style_state}"]:
                if "size" in self.style[f":default"]:
                    target_style_state = "default" # Fallback to default style
                else:
                    return (0, 0) # Unspecified in style
            return styles.style.fill_vars(
                self.style[f":{target_style_state}"]["size"]
                )

    @property
    def width(self) -> int:
        """Width of the widget."""
        return self.size[0]

    @property
    def height(self) -> int:
        """Height of the widget."""
        return self.size[1]

    @property
    def root_container(self) -> window.Window:
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
                raise RuntimeError(f"Nowhere to put {self.id} as it is not in a valid window!")

    def _update_drawing_objects(self):
        """Update a widget's draw list, for internal use only.

        For widget base, this clears the draw list.
        """
        # self.trigger(NotImplemented) # TODO: Trigger style change event
        # self.draw()
        pass

    # def __setattr__(self, name: str, value: typing.Any) -> None:
    #     """When changing attributes of a widget.

    #     Currently, updates the draw list of the widget after setting new attributes.

    #     :param name: Name of the attribute to set
    #     :param value: The new value
    #     """
    #     return_val = super().__setattr__(name, value)
    #     if not name.startswith("_"): # Skip internal vars to avoid endless recursion
    #         # (only do update for props changes)
    #         if self._initialized: # Skip update for initialization
    #             self._update_drawing_objects()
    #     return return_val

    @property
    def curr_state_styles(self) -> dict[str, typing.Any]:
        style_vars = (
            self.theme, 
            self.root_container, 
            self
            )
        style_state = ':' + (self.state if self.state in self.style.keys() else "default")
        curr_style = styles.style.fill_vars(self.style[style_state], *style_vars)
        return curr_style

    def draw_components(self, *args, **kwargs) -> typing.Self:
        return self

    def draw(self, *args, **kwargs) -> typing.Self:
        """Draw the widget, does nothing on base class."""
        self._update_drawing_objects()

        self.draw_components(*args, **kwargs)

        if isinstance(self, Container):
            self.draw_children()

        return self

    def place(self, 
            pos: styles.shape.Point, 
            size: typing.Optional[styles.shape.Size] = None, 
            ) -> typing.Self:
        """Add the widget to parent, using place layout.

        :param pos: The position to place the widget
        :param size: The size of this widget
        """
        self.layout_profile = layout_profiles.PlaceProfile(pos, size)
        return self
