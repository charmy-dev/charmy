from .container import Container
from .windowbase import WindowBase


class Window(WindowBase, Container):
    def __init__(self, *args, **kwargs):
        WindowBase.__init__(self, *args, **kwargs)
        self.new("children", [])
        self.set("ui.draw_func", self.skia_draw_func)

    def skia_draw_func(self, canvas):
        canvas.clear(self.skia.ColorWHITE)
