"""Charmy widgets base class"""

import typing

import dataclasses
import reactive_caching

from . import window
from ..cm_object import CharmyObject
from ..event import EventHandling, event_types
from .container import Container, layout_profiles
from .. import graphics
from .. import styles

__all__ = ["Widget", "WidgetProfile"]

@dataclasses.dataclass
class WidgetProfile:
    """Class to store configs of a specific widget under a specific state.

    Each `WidgetProfile` represents a profile for `Widget`. Further, `ButtonProfile` for 
    `Button`, `TextProfile` for `Text`, and so on. An instance of `WidgetProfile` or its subclasses 
    comes with default values for such type of widget. These default values will be affected by 
    themes.
    """
    # TODO: Support themes in WidgetProfiles
    size: typing.Optional[styles.shape.Size] = None
    fallback_state: str = "default"
    # _fallback_target: typing.Self | None | typing.Literal["widget_specify"] = "widget_specify"

    @classmethod
    def default(cls) -> typing.Self:
        """To generate a profile with full default values for this widget."""
        instance = cls(
            size=(0, 0)
            )
        return instance

    def __contains__(self, item: str) -> bool:
        """To see whether an specific item is contained and specified in this profile."""
        if not hasattr(self, item):
            return False
        return getattr(self, item) is not None


class Widget(CharmyObject, EventHandling, reactive_caching.CachedClass):
    """Widget base class."""

    def __init__(self, 
        parent: Container | None = None, 
        profiles: typing.Optional[dict[str, WidgetProfile]] = None
        ) -> None:
        """To initialize a widget.

        Profiles
        --------
        Profiles are used to specify the appearance of a specific widget, including its shape, 
        color, text(s) or element(s) inside… Each widget's profiles are stored in attribute 
        `profiles`, in form of `{"state name": WidgetProfile()}`.

        Each widget comes with default profiles config, which can be changed by specifying 
        `profiles` when initializing them. Contents specified in `profiles` arg will override 
        defaults (Note: minimum overriding unit is a `WidgetProfile` instance specified for a 
        specific state).

        The `default` state's profile is a fallback profile.

        :param parent: Parent of the widget, or None in `with` context
        :param profiles: Profiles config of the widget
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

        self.profiles: dict[str, WidgetProfile] = {"default": WidgetProfile().default()}
        if profiles is not None:
            self.profiles.update(profiles)
        self.theme: typing.Optional[styles.theme.Theme] = None # TODO: Support theme

        self.is_visible: bool = False
        self.layout_profile: layout_profiles.LayoutProfile = layout_profiles.LayoutProfile()

        self.state: str = "normal"
        self._components: typing.Tuple[graphics.DrawnShape, ...] = ()
        self._alive: bool = True

    def _negotiate_profile_state(self, target_state: str, target_item: str):
        """Negotiate and deduce a valid profile state when getting a value from a profile.

        In other words, this is the fallback routine when getting a value from a profile.
        """
        if target_state not in self.profiles:
            return "default" # Fallback to default state derectly if state not exists
        if target_item not in target_state:
            # If target item remains not specified (with value None) in target state's profile
            return self._negotiate_profile_state(
                self.profiles[target_state].fallback_state, target_item
                ) # Return negotiated fallback state
            # BUG: Cannot correctly handle inter-fallback profiles. Current code is expected to 
            #      give a max recursion error in such case, but it should give default state.
        return target_state

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
        """Size of the widget.

        Firts try to deduce from layout profile, then get from config if not specified.
        """
        layout_specified: typing.Optional[styles.shape.Point]
        if type(self.layout_profile) is layout_profiles.LayoutProfile:
            # If no layout profile specified
            layout_specified = None
        else:
            layout_specified = self.layout_profile.size
        if layout_specified is None:
            # If size not given, get from style
            # curr_style = self.curr_state_styles
            target_profile_state = self._negotiate_profile_state(self.state, "size")
            profile_specified = self.profiles[target_profile_state].size
            if type(profile_specified) is not tuple:
                return (0, 0)
            if len(profile_specified) != 2:
                return (0, 0)
            if type(profile_specified[0]) is not int or type(profile_specified[1]) is not int:
                return (0, 0)
            return profile_specified
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

    def draw(self, *args, **kwargs) -> typing.Self:
        """Draw the widget, does nothing on base class."""
        if not self._alive:
            return self

        for component in self.components:
            component = typing.cast(graphics.DrawnObject, component)
            component.draw()

        if isinstance(self, Container):
            Container.draw_children(self)

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
                # print(f"Point {point} in {self.id}-{component.id}")
                return True
        else:
            return False

    # def _on_cache_dirty(self, prop_name: str) -> None:
    #     if prop_name == "components":
    #         for component in self.components:
    #             component = typing.cast(graphics.DrawnObject, component)
    #             component._need_redraw = True