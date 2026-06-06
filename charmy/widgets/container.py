"""This module contains all ability of a container to manage layouts."""

from __future__ import annotations as _

import typing

from abc import abstractmethod
import reactive_caching

from ..utils import layout_profiles # Expose them as (...).container.layout_profiles
from ..utils import type_checking
from ..styles import shape, texture

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

    def __init__(self, *args, **kwargs):
        """Initialize a container base class.

        The container base class is not supposed to be instantiated directly, make sure you are 
        executing this method during subclassing.
        """
        super().__init__(*args, **kwargs)

        self.children: list[widget.Widget] = []

        self.background: texture.Texture | texture.TextureLike

    @reactive_caching.cached_property(["children", "background"])
    def layers(self) -> \
        tuple[texture.Texture | texture.TextureLike, list[widget.Widget], list[widget.Widget]]:
        place_list = []
        managed_list = []
        for child in self.children:
            if isinstance(child.layout_profile, layout_profiles.ManagedLayoutProfile):
                managed_list.append(child)
            else:
                place_list.append(child)
        return (self.background, managed_list, place_list)

    @property
    @abstractmethod
    def pos(self) -> shape.Point: ...

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
        """Add a child object."""
        if child not in self.children:
            self.children.append(child)
        return self

    def draw_children(self) -> typing.Self:
        """Draw the container and its children."""
        for child in self.children:
            child.draw()
        return self

    def _clear_chidren(self):
        for child in self.children:
            child.destroy()

    def __contains__(self, target: widget.Widget) -> bool:
        return target in self.children
    
    def get_mouse_hover(self, pos: shape.Point) -> typing.List[Container | widget.Widget]:
        layers: \
            tuple[texture.Texture | texture.TextureLike, 
                  list[widget.Widget], list[widget.Widget]] = self.layers
        placed_children = layers[2]
        managed_children = layers[1]
        for layer in placed_children, managed_children:
            for child in layer:
                if pos in child:
                    if isinstance(child, Container):
                        result = self.get_mouse_hover(pos)
                        if len(result) == 0:
                            # Not hovering on anything, not even background
                            continue # Check hovering of widgets below
                        result.insert(0, self)
                        return result
                    else:
                        return [child]
        else:
            if isinstance(texture.ensure_texture(self.background), texture.Transparent) and \
                not isinstance(self, type_checking.WindowLike):
                return []
            else:
                return [self]