import typing

from dataclasses import dataclass

from ..styles import shape


@dataclass
class LayoutProfile:
    type: typing.ClassVar[str] = "no_layout"

    @property
    def final_size(self) -> typing.Optional[shape.Size]:
        return None

@dataclass
class PlaceProfile(LayoutProfile):
    type: typing.ClassVar[str] = "place"
    pos: shape.Point
    size: typing.Optional[shape.Size] # = None

    @property
    def final_size(self) -> typing.Optional[shape.Size]:
        return self.size