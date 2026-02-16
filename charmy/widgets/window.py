from ..const import Backends
from ..rect import Rect
from .container import Container
from .windowbase import WindowBase


class Window(WindowBase, Container):
    """Window class."""

    def __init__(self, *args, **kwargs):
        WindowBase.__init__(self, *args, **kwargs)
        self.new("children", [])
        match self["framework"].drawing_name:
            case "SKIA":
                self.set(
                    "ui.draw_func", self.skia_draw_func
                )  # When `draw` is called, trigger `ui.draw_func`

    # TODO: why specific drawing frame?
    def skia_draw_func(self, canvas):
        """Draw function for Skia."""
        canvas.clear(self.skia.ColorGRAY)
        self.draw_children(canvas)
