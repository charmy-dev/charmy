import sys

from ..object import AqObject
from ..pos import AqPos
from ..size import AqSize
from .app import AqApp


class AqWindowBase(AqObject):
    def __init__(self, parent: AqApp = None, *, title: str = "Aquaui", fha: bool = True):
        super().__init__()

        if parent is None:
            parent = self.get_obj("aqapp0")
            if parent is None:
                raise ValueError("Not found AqApp")

        self.new("parent", parent)

        if isinstance(parent, AqApp):
            self.new("app", parent)
        elif isinstance(parent, AqWindowBase):
            self.new("app", parent.get("app"))
        self.get("app").get("windows").append(self)

        def _get_ui_framework():
            return self["app"].get("ui.framework")

        def _get_ui_is_vsync():
            return self["app"].get("ui.is_vsync")

        self.new("ui.framework", _get_ui_framework(), get_func=_get_ui_framework)
        self.new("ui.is_vsync", _get_ui_is_vsync(), get_func=_get_ui_is_vsync)

        self.new("is_force_hardware_acceleration", fha)
        self.new("pos", AqPos(0, 0))
        self.new("root_pos", AqPos(0, 0))
        self.new("title", title)
        self.new("visible", False)

        self.the_window = self.create()

    def create(self):
        window = None

        match self.get("ui.framework"):
            case "glfw":
                import glfw

                glfw.window_hint(
                    glfw.CONTEXT_RELEASE_BEHAVIOR, glfw.RELEASE_BEHAVIOR_NONE
                )  # mystery optimize
                glfw.window_hint(glfw.STENCIL_BITS, 8)
                glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, glfw.TRUE)  # macOS
                glfw.window_hint(glfw.SCALE_TO_MONITOR, glfw.TRUE)  # Windows/Linux

                # see https://www.glfw.org/faq#macos
                if sys.platform.startswith("darwin"):
                    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
                    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
                    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
                    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
                else:
                    if self.get("is_force_hardware_acceleration"):
                        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
                        glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
                        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
                        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
                        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

                window = glfw.create_window(
                    self.width, self.height, self.get("title"), None, None
                )
                if not window:
                    raise RuntimeError("无法创建GLFW窗口")

                self.set("visible", True)

                pos = glfw.get_window_pos(window)

                root_point = self.get("root_point")
                root_point.set("x", pos[0])
                root_point.set("y", pos[1])

        return window

    def update(self):
        from glfw import poll_events, wait_events, get_current_context, swap_interval

        input_mode: bool = True

        # poll_events()

        for window in self.windows:
            if window.visible and window.alive:
                window.update()
                if window.mode == "input":
                    input_mode = True
                if get_current_context():
                    swap_interval(1 if self.get("ui.is_vsync") else 0)  # 是否启用垂直同步

        if input_mode:
            poll_events()
        else:
            # if self._check_delay_events()
            wait_events()
