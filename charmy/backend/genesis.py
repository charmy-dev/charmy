# The Genesis Backend
# 2026 by XiangQinXi & rgzz666

# This is a backend for early development only! It is also used as a template if Charmy backends.

# Under dev

import glfw
import skia
from . import template


class Backend(template.Backend):

    def __init__(self):
        """Here goes the backend's metadata."""
        self.name = "genesis"
        self.friendly_name = "Genesis (early development)"
        self.version = "0.1.0"
        self.author = ["XiangQinXi", "rgzz666"]

    # part: window
    
    @staticmethod
    def create_window(self, size, title, **kwargs) -> dict[str, typing.Any]:
        # mystery optimize
        self.glfw.window_hint(self.glfw.CONTEXT_RELEASE_BEHAVIOR, self.glfw.RELEASE_BEHAVIOR_NONE)

        self.glfw.window_hint(self.glfw.STENCIL_BITS, 8)

        # see https://www.glfw.org/faq#macos
        if PLATFORM == "macos":
            self.glfw.window_hint(self.glfw.COCOA_RETINA_FRAMEBUFFER, self.glfw.TRUE)
            self.glfw.window_hint(self.glfw.OPENGL_FORWARD_COMPAT, True)
        else:  # Windows/Linux
            self.glfw.window_hint(self.glfw.SCALE_TO_MONITOR, self.glfw.TRUE)

        self.glfw.window_hint(self.glfw.CONTEXT_VERSION_MAJOR, 3)
        self.glfw.window_hint(self.glfw.CONTEXT_VERSION_MINOR, 2 if PLATFORM == "macos" else 3)

        self.glfw.window_hint(self.glfw.OPENGL_PROFILE, self.glfw.OPENGL_CORE_PROFILE)

        # create window
        window = self.glfw.create_window(size.width, size.height, title, None, None)

        if window == None:
            raise RuntimeError("Can't create window")