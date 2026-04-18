# The Genesis Backend
# 2026 by XiangQinXi & rgzz666

# This is a backend for early development only! 
# It is also used as an example of developing a Charmy backend.

# Under dev

from dataclasses import dataclass
import glfw
# import skia
import sys

from . import template


class Backend(template.Backend):

    def __init__(self):
        """Here goes the backend's metadata."""
        super().__init__()
        self.name = "genesis"
        self.friendly_name = "Genesis (early development)"
        self.version = "0.1.0"
        self.author = ["XiangQinXi", "rgzz666"]

        self.WindowBase = WindowBase
    
    def init(self, **kwargs) -> None:
        if not glfw.init():
            raise glfw.GLFWError("GLFW init failed")

        glfw.window_hint(glfw.STENCIL_BITS, 8)
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
        glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, True)
        # TODO: cmm also has samples, I have to figure out whether objects' attributes are shared or not
        # TODO: combine them?
        glfw.window_hint(glfw.SAMPLES, kwargs.get("samples", 4))

        if sys.platform == "win32":
            glfw.window_hint(glfw.WIN32_KEYBOARD_MENU, True)

        if kwargs.get("error_callback", None):
            glfw.set_error_callback(kwargs["error_callback"])


@dataclass
class WindowSupportState(template.WindowSupportState):
    """Flags all supported features."""
    set_title               = True
    set_icon                = True
    resize                  = True
    set_scale_mode          = True
    set_background          = True
    translucent             = True
    set_state               = True
    fullscreen              = True
    customize_titlebar      = True

class WindowBase(template.WindowBase):
    """Window APIs in GLFW backend."""
    
    def __init__(self):
        """Creates a window"""
        super().__init__()

        self.title = "Charmy GLFW Window"
        self.size = (540, 480)

        # mysterious optimization
        glfw.window_hint(glfw.CONTEXT_RELEASE_BEHAVIOR, glfw.RELEASE_BEHAVIOR_NONE)

        glfw.window_hint(glfw.STENCIL_BITS, 8)

        # see https://www.glfw.org/faq#macos
        if sys.platform == "darwin":
            glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, glfw.TRUE)
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        else:  # Windows / Linux
            glfw.window_hint(glfw.SCALE_TO_MONITOR, glfw.TRUE)

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2 if sys.platform == "darwin" else 3)

        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # create window
        self.window = glfw.create_window(self.size[0], self.size[1], self.title, None, None)

        if self.window == None:
            raise RuntimeError("Can't create window")
    
    def show(self):
        glfw.show_window(self.window)