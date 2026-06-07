from __future__ import annotations as _

import typing

from dataclasses import dataclass as _dataclass
from abc import abstractmethod as _abstractmethod

if typing.TYPE_CHECKING:
    from ..styles import shape as _shape


class LayoutProfile:
    """Base class of all layout profiles."""
    type: typing.ClassVar[str] = "nolayout"

    def __init__(self):
        self.pos: _shape.Point
        self.size: _shape.Size

@_dataclass
class PlaceProfile(LayoutProfile):
    """Place profile, to directly specify the position and size of the widget."""
    type: typing.ClassVar[str] = "place"

    pos: _shape.Point
    size: typing.Optional[_shape.Size] = None

@_dataclass
class ManagedLayoutProfile(LayoutProfile):
    type: typing.ClassVar[str] = "managed"

    @property
    @_abstractmethod
    def pos(self) -> _shape.Point: ...

    @property
    @_abstractmethod
    def size(self) -> _shape.Size: ...