from __future__ import annotations as _

import typing

from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from ..styles import shape as _shape


@dataclass
class LayoutProfile:
    type: typing.ClassVar[str] = "no_layout"

    @property
    def final_size(self) -> typing.Optional[_shape.Size]:
        return None

@dataclass
class PlaceProfile(LayoutProfile):
    type: typing.ClassVar[str] = "place"
    pos: _shape.Point
    size: typing.Optional[_shape.Size] # = None

    @property
    def final_size(self) -> typing.Optional[_shape.Size]:
        return self.size