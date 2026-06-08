"""Charmy widgets base class"""

import typing

import reactive_caching

from . import window
from ..cm_object import CharmyObject
from ..event import EventHandling, event_types
from .container import Container, layout_profiles
from .. import graphics
from .. import styles

__all__ = ["Widget"]


class Widget(CharmyObject, EventHandling, reactive_caching.CachedClass):
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

        super().__init__()
        EventHandling.__init__(self)
        reactive_caching.CachedClass.__init__(self)

        self.parent: Container = parent
        self.parent.add_child(self)

        self.style: dict = style
        self.theme: typing.Optional[styles.theme.Theme] = None

        self.is_visible: bool = False
        self.layout_profile: layout_profiles.LayoutProfile = layout_profiles.LayoutProfile()

        self.state: str = "normal"
        self._components: typing.Tuple[graphics.DrawnShape, ...] = ()
        self._alive: bool = True

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
            parent_pos = self.parent.abs_pos
            self_pos = self.pos
            return (parent_pos[0] + self_pos[0], parent_pos[1] + self_pos[1])
        else:
            return self.pos

    @reactive_caching.cached_property(["layout_profile", "style"])
    def size(self) -> styles.shape.Size:
        """Size of the widget"""
        layout_specified: typing.Optional[styles.shape.Point]
        if type(self.layout_profile) is layout_profiles.LayoutProfile:
            # If no layout profile specified
            layout_specified = None
        else:
            layout_specified = self.layout_profile.size
        if layout_specified is None:
            # If size not given, get from style
            # curr_style = self.curr_state_styles
            target_style_state = self.state if self.state in self.style else "default"
            if not "size" in self.style[f":{target_style_state}"]:
                if "size" in self.style[f":default"]:
                    target_style_state = "default" # Fallback to default style
                else:
                    return (0, 0) # Unspecified in style
            style_specified = styles.style.fill_vars(
                self.style[f":{target_style_state}"]["size"]
                )
            if type(style_specified) is not tuple:
                return (0, 0)
            if len(style_specified) != 2:
                return (0, 0)
            if type(style_specified[0]) is not int or type(style_specified[1]) is not int:
                return (0, 0)
            return style_specified
        else:
            return layout_specified

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

    @reactive_caching.cached_property("-exposed-")
    def components(self) -> typing.Tuple[graphics.DrawnObject, ...]:
        """Components (drawn objects) that make up the button.

        For widget base class, it does not have any component.
        """
        return ()

    @property
    def curr_state_styles(self) -> dict[str, typing.Any]:
        style_vars = (
            self.theme, 
            self.root_container, 
            self
            )
        style_state = f":{self.state}"
        if style_state not in self.style:
            style_state = ":default"
        # print(style_state)
        curr_style = styles.style.fill_vars(self.style[style_state], *style_vars)
        return curr_style

    def draw(self, *args, **kwargs) -> typing.Self:
        """Draw the widget, does nothing on base class."""
        if not self._alive:
            return self

        for component in self.components:
            component.draw(self.root_container)

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

    def destroy(self) -> None:
        """Destroy a widget when no longer needed."""
        self.trigger(event_types.WidgetDestroy(self))
        self._alive = False
        if isinstance(self, Container):
            # Also destroy children if self is container
            self._clear_chidren()

    def __contains__(self, pos: styles.shape.Point) -> bool:
        point = (pos[0] - self.x, pos[1] - self.y)
        for component in self.components:
            if point in component:
                return True
        else:
            return False

    def _on_cache_dirty(self, prop_name: str) -> None:
        if prop_name == "components":
            for component in self.components:
                component = typing.cast(graphics.DrawnObject, component)
                component._need_redraw = True