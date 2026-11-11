from __future__ import annotations as _

import typing as _typing

import dataclasses as _dataclasses
from abc import abstractmethod as _abstractmethod

from .. import event as _event
from .on_setattr import apply_on_setattr as _apply_on_setattr

if _typing.TYPE_CHECKING:
    from ..styles import shape as _shape
    from ..widgets import widget as _widget


@_apply_on_setattr
class LayoutProfile(_event.EventHandling):
    """Base class of all layout profiles."""
    type: _typing.ClassVar[str] = "nolayout"

    def __init__(self):
        self._alive: bool = False

        super().__init__()

        self.subject: _widget.Widget
        self.pos: _shape.Point
        self.size: _shape.Size

    def _on_setattr(self, name: str, value: _typing.Any, old: _typing.Any) -> None:
        # super().__setattr__(name, value)
        if not hasattr(self, "_alive"):
            return
        if not self._alive:
            return
        if name != "type":
            self.trigger(_event.event_types.LayoutChanged(self, name, old))
            # print(f"Layout changed: {name}")

@_dataclasses.dataclass
class PlaceProfile(LayoutProfile):
    """Place layout profile, to directly specify the position and size of the widget."""
    type: _typing.ClassVar[str] = "place"

    def __post_init__(self) -> ...:
        super().__init__()

    subject: _widget.Widget
    pos: _shape.Point
    size: _typing.Optional[_shape.Size] = None

@_dataclasses.dataclass
class ManagedLayoutProfile(LayoutProfile):
    """Base class of maneged layouts. Should never be used directly."""
    type: _typing.ClassVar[str] = "managed"

    subject: _widget.Widget

    @property
    @_abstractmethod
    def pos(self) -> _shape.Point:
        """Nope!"""
        ...

    @pos.setter
    def pos(self) -> None: raise NotImplementedError(
        "Not supported to set pos for managed layout.")

    @property
    @_abstractmethod
    def size(self) -> _shape.Size:
        """Nope!"""
        ...

    @size.setter
    def size(self) -> None: raise NotImplementedError(
        "Not supported to set size for managed layout.")

    def update(self) -> None:
        """Update widget layout info in this managed layout.

        Note that this is not compulsory for all managed layouts. In such cases, this function will
        do nothing.
        """
        return

@_dataclasses.dataclass
class FlexLayout(ManagedLayoutProfile):
    """Flex layout profile."""
    type: _typing.ClassVar[str] = "flex"

    expand_priority: int = -1

    def __post_init__(self):
        self._widget_boundaries: dict[_widget.Widget, _shape.RectRange] = {}

    @property
    def pos(self) -> _shape.Point:
        """Calculated pos for the widget by the flex layout."""
        return self._widget_boundaries[self.subject][0]

    @property
    def size(self) -> _shape.Size:
        """Calculated size for the widget by the flex layout."""
        return self._widget_boundaries[self.subject][1]

    def update(self):
        """Update boundaries of all widgets in their parent container."""
        for direction in (0, 1):
            # For each direction (x and y, which is index 0 and 1 in every pos and size)
            widget_suggested_sizes: dict[_widget.Widget, _shape.Size] = {}
            widget_min_sizes: dict[_widget.Widget, _shape.Size] = {}
            widget_max_sizes: dict[_widget.Widget, _shape.Size] = {}
            for widget in self.subject.parent.children:
                suggested = widget.migrate_full_curr_profile().size
                min_ = widget.migrate_full_curr_profile().min_size
                max_ = widget.migrate_full_curr_profile().max_size
                # widget_suggested_sizes[widget] = widget.migrate_full_curr_profile().size