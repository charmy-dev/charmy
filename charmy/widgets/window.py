from ..event import CEvent
from .container import CContainer
from .windowbase import CWindowBase


class CWindow(CWindowBase, CContainer):
    def __init__(self, *args, **kwargs):
        CWindowBase.__init__(self, *args, **kwargs)
        self.new("children", [])
        self.set("ui.draw_func", self.skia_draw_func)

    def skia_draw_func(self, canvas):
        canvas.clear(self.skia.ColorWHITE)