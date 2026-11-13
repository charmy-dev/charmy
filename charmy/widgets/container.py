"""This module contains all ability of a container to manage layouts."""

from __future__ import annotations as _

import typing

from abc import abstractmethod
import reactive_caching

from ..utils import layout_profiles # Expose them as (...).container.layout_profiles
from ..utils import type_checking
from ..styles import shape, texture
from .. import cm_object

if typing.TYPE_CHECKING:
    from . import widget

__all__ = ["Container", "layout_profiles"]


class Container(reactive_caching.CachedClass):
    """Container represents a widget's ability to contain and arrange other widgets inside.

    The `Container` class contains the ability of managing widgets within the container, and should 
    be inherited by all types of containers including windows, frames, etc., but not supposed to be 
    instantiated directly.
    """

    _with_stack: typing.ClassVar[list[Container]] = [] # Used to store embedding stack in with as

    def __init__(self, 
            managed_layout_type: type[layout_profiles.ManagedLayout] | str = \
                layout_profiles.FlexLayout, 
            flex_direction: typing.Literal[0, 1] = 1, 
            *args, **kwargs):
        """Initialize a container base class.

        The container base class is not supposed to be instantiated directly, make sure you are 
        executing this method during subclassing.
        """
        super().__init__(*args, **kwargs)

        if type(managed_layout_type) is str:
            # Search for subclasses of managed layout base class to convert string param to class
            for subclass in layout_profiles.ManagedLayout.__subclasses__():
                if subclass.type == managed_layout_type:
                    managed_layout_type = subclass
                    break
            else:
                raise ValueError(
                    "Specified invalid managed layout type name "
                    f"'{managed_layout_type}' for container"
                    )
        managed_layout_type = typing.cast(type[layout_profiles.ManagedLayout], managed_layout_type)

        self.children: list[widget.Widget] = []
        self._flex_dist: dict[widget.Widget, int] = {}

        self.background: texture.Texture | texture.TextureLike
        # TODO: Change this⬆️ to let it only be specified with profiles, in specific widgets
        self.managed_layout_type: type[layout_profiles.ManagedLayout] = managed_layout_type
        self.flex_direction: typing.Literal[0, 1] = flex_direction

    @reactive_caching.cached_property(["children", "background"])
    def layers(self) -> \
        tuple[texture.Texture | texture.TextureLike, list[widget.Widget], list[widget.Widget]]:
        place_list = []
        managed_list = []
        for child in self.children:
            if isinstance(child.layout_profile, layout_profiles.ManagedLayout):
                managed_list.append(child)
            else:
                place_list.append(child)
        return (self.background, managed_list, place_list)

    @property
    @abstractmethod
    def pos(self) -> shape.Point: ...

    @property
    @abstractmethod
    def abs_pos(self) -> shape.Point: ...

    @property
    @abstractmethod
    def size(self) -> shape.Size: ...

    # region Context

    def __enter__(self) -> typing.Self:
        """Enter the context."""
        Container._with_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> typing.Literal[False]:
        """Exit the context."""
        Container._with_stack.pop()
        return False # Does not handle exceptions

    # endregion

    def add_child(self, child: widget.Widget) -> typing.Self:
        """Add a child object.

        Note
        ----
        The child list is **rebound** rather than mutated in place on purpose. The `layers` 
        cached property is only invalidated through `__setattr__`, so an in-place `append()` would 
        leave the cache stale and the newly added child would never be drawn.
        """
        if child not in self.children:
            self.children = [*self.children, child]
        return self

    def remove_child(self, child: widget.Widget) -> typing.Self:
        """Remove a child object, so that it is no longer drawn or hit-tested.

        This seem like a vibed function, and I cannot ensure its source.  —— rgzz666
        """
        if child in self.children:
            # Identity comparison: never drop a merely "equal" sibling object
            self.children = [sibling for sibling in self.children if sibling is not child]
        return self

    def update_layout(self):
        """Update layout results."""
        match self.managed_layout_type:
            case layout_profiles.FlexLayout:
                # Flex layout logic
                d = self.flex_direction # d for direction or dimension
                total_length = self.size[d]
                remain_length = total_length
                max_priority = 0
                for child in self.children:
                    if isinstance(child.layout_profile, layout_profiles.FlexLayout):
                        remain_length -= child.size[d]
                        if child.layout_profile.expand_priority > max_priority:
                            max_priority = child.layout_profile.expand_priority
            case _:
                self_id = self.id if isinstance(self, cm_object.CharmyObject) else "without ID"
                raise ValueError(f"Managed layout type chosen for container {self_id} is invalid.")

    def draw_children(self) -> typing.Self:
        """Draw the container and its children."""
        _, managed_layer, place_layer = self.layers
        if typing.TYPE_CHECKING:
            managed_layer = typing.cast(list[widget.Widget], managed_layer)
            place_layer = typing.cast(list[widget.Widget], place_layer)
        for layer in place_layer, managed_layer:
            for child in layer:
                child._check_change()
        return self

    def _clear_children(self):
        """Destroy every child, then drop them from the child list."""
        # 👇 Iterate a copy: destroy() removes each child from `self.children` as it goes
        for child in list(self.children):
            child.destroy()
        self.children = []

    def __contains__(self, target: widget.Widget) -> bool:
        return target in self.children
    
    def get_mouse_hover(self, abs_pos: shape.Point) -> typing.List[Container | widget.Widget]:
        layers: \
            tuple[texture.Texture | texture.TextureLike, 
                  list[widget.Widget], list[widget.Widget]] = self.layers
        pos = (abs_pos[0] - self.abs_pos[0], abs_pos[1] - self.abs_pos[1])
        placed_children = layers[2]
        managed_children = layers[1]
        for layer in (reversed(placed_children), reversed(managed_children)): # For each layer
            for child in layer: # For each child
                result: typing.List[Container | widget.Widget] = []# TODO: Sure???
                if pos in child:
                    if isinstance(child, Container):
                        result = child.get_mouse_hover(pos)
                        if len(result) == 0:
                            # Not hovering on anything, not even background
                            continue # Check if hovering of widgets below
                    else:
                        result = [child]
                    result.insert(0, self)
                    return result
        else:
            if isinstance(texture.ensure_texture(self.background), texture.Transparent) and \
                not isinstance(self, type_checking.WindowLike):
                # Self is not a window and self has transparent back
                return []
            else:
                return [self]