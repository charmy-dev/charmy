from ..event import EventHandling
from ..pos import Pos
from ..rect import Rect
from ..size import Size
from .canvas import CanvasBase
from .container import Container, auto_find_parent


@auto_find_parent
class Widget(CanvasBase, EventHandling):
    """Basic widget class."""

    def __init__(self, parent: Container | None = None):
        super().__init__()

        if parent is None:
            parent = self.find("Window0", default=None)

        self.parent: Container = parent
        self.size = Size(100, 100)
        self.pos = Pos(0, 0)

        # Automatically add to parent's children list if parent exists
        if parent is not None:
            parent.add_child(self)

    @property
    def rect(self) -> Rect:
        return Rect().make_XYWH(x=self.x, y=self.y, width=self.width, height=self.height)

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
