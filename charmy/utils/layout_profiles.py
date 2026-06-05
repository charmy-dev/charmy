from __future__ import annotations as _

import typing

from dataclasses import dataclass as _dataclass
from abc import abstractmethod as _abstractmethod

if typing.TYPE_CHECKING:
    from ..styles import shape as _shape


@_dataclass
class LayoutProfile:
    type: typing.ClassVar[str] = "nolayout"

    @property
    def final_size(self) -> typing.Optional[_shape.Size]:
        return None

    @property
    @_abstractmethod
    def size(self) -> _shape.Size: ...

@_dataclass
class PlaceProfile(LayoutProfile):
    type: typing.ClassVar[str] = "place"
    pos: _shape.Point
    size: typing.Optional[_shape.Size] # = None

    @property
    def final_size(self) -> typing.Optional[_shape.Size]:
        return self.size

@_dataclass
class ManagedLayoutProfile(LayoutProfile):
    type: typing.ClassVar[str] = "managed"

    @property
    @_abstractmethod
    def pos(self) -> _shape.Point: ...

    @property
    @_abstractmethod
    def size(self) -> _shape.Size: ...