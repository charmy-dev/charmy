from .template import Drawing
import skia


class Skia(Drawing):
    def __init__(self):
        self.skia = skia

    def surface_with_gl(self, wnd):
        backend_context = self.skia.GrDirectContext.MakeGL()  # Make a direct context for OpenGL
