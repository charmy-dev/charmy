import typing

from .object import CharmyObject
from .pos import Pos
from .size import Size


class Rect(CharmyObject):
    """Rect is a class to store the position and size of a rectangle.

    Attributes:
        pos (Pos): the position of the rectangle.
        size (Size): the size of the rectangle.
    """

    def __init__(self):
        super().__init__()
        # 默认是XYWH坐标系
        self.pos = Pos(0, 0)
        self.size = Size(0, 0)

    def make_XYWH(self, x: int | float | None = None, y: int | float | None = None, width: int | float | None = None, height: int | float | None = None) -> typing.Self:
        self.pos(x, y)
        self.size(width, height)
        return self

    def make_LTRB(self, left: int | float | None = None, top: int | float | None = None, right: int | float | None = None, bottom: int | float | None = None) -> typing.Self:
        self.pos(left, top)
        self.size(right - left, bottom - top)
        return self

    def __str__(self):
        """Return position in string."""
        return f"Rect({self.pos.x}, {self.pos.y}, {self.size.width}, {self.size.height})"

    # region Attributes set/get

    @property
    def left(self):
        return self.pos.x

    @property
    def top(self):
        return self.pos.y

    @property
    def right(self):
        return self.pos.x + self.size.width

    @property
    def bottom(self):
        return self.pos.y + self.size.height

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.y

    @property
    def width(self):
        return self.size.width

    @property
    def height(self):
        return self.size.height

    # endregion
