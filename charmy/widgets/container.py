"""This module contains all ability of a container to manage layouts."""

import typing

from abc import abstractmethod

from ..utils import layout_profiles # Expose them as (...).container.layout_profiles
from ..styles import shape

if typing.TYPE_CHECKING:
    from . import widget

__all__ = ["Container", "layout_profiles"]


class Container:
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

    # region Context

    def __enter__(self) -> typing.Self:
        """Enter the context."""
        Container._with_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> typing.Literal[False]:
        """Exit the context."""
        Container._with_stack.pop()
        return False # Does not handle exceptions

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

    @property
    @abstractmethod
    def pos(self) -> shape.Point: ...

    # endregion