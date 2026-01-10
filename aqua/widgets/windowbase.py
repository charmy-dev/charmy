import sys
import typing

from ..const import UIFrame
from ..object import AqObject
from ..pos import AqPos
from ..size import AqSize
from .app import AqApp


class AqWindowBase(AqObject):
    def __init__(self, parent: AqApp = None, *, title: str = "Aquaui", size: tuple[int, int] = (100, 100), fha: bool = True):
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
        self.new("size", AqSize(size[0], size[1]))
        self.new("title", title)
        self.new("visible", False)
        self.new("alive", True)

        self.new("the_window", self.create())

    def create(self):
        window = None

        match self.get("ui.framework"):
            case UIFrame.GLFW:
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

                _size = self.get("size")
                window = glfw.create_window(
                    _size["width"], _size["height"], self.get("title"), None, None
                )
                if not window:
                    raise RuntimeError("无法创建GLFW窗口")

                self.set("visible", True)

                pos = glfw.get_window_pos(window)

                _root_point = self.get("root_pos")
                _root_point.set("x", pos[0])
                _root_point.set("y", pos[1])

        return window

    def update(self):
        pass

    def destroy(self) -> None:
        """Destroy the window.

        :return: None
        """
        # self._event_init = False
        # print(self.id)
        self["app"].destroy_window(self)
        match self.get("ui.framework"):
            case UIFrame.GLFW:
                import glfw
                try:
                    glfw.destroy_window(self["the_window"])
                except TypeError:
                    pass

        self["alive"] = False
        #self.draw_func = None
        self["the_window"] = None  # Clear the reference

    def can_be_close(self, value: bool | None = None) -> typing.Self | bool:
        """Set whether the window can be closed.

        Prevent users from closing the window, which can be used in conjunction with prompts like "Save before closing?"

        >>> def delete(_: SkEvent):
        >>>     window.can_be_close(False)
        >>> window.bind("delete_window", delete)


        :param value: Whether the window can be closed
        :return: None
        """
        match self.get("ui.framework"):
            case UIFrame.GLFW:
                import glfw
                if value is not None:
                    glfw.set_window_should_close(self["the_window"], value)
                    return self
                else:
                    if self["the_window"]:
                        return glfw.window_should_close(self["the_window"])
                    else:
                        return False
        return True