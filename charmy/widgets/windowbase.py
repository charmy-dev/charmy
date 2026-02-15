import importlib
import sys
import typing

from ..const import BackendFrame, DrawingFrame, DrawingMode, UIFrame
from ..event import Event, EventHandling
from ..object import CharmyObject
from ..pos import Pos
from ..size import Size
from .app import App


class WindowBase(EventHandling, CharmyObject):
    """WindowBase is a base class for window.

    Args:
        parent: The parent CApp object,
        title: The title of the window,
        size: The size of the window,
        fha: Whether to force hardware acceleration
        drawing_mode: The drawing mode of the window,
    """

    def __init__(
        self,
        parent: App = None,
        *,
        title: str = "Charmy GUI",
        size: tuple[int, int] = (100, 100),
        fha: bool = True,
        drawing_mode: DrawingMode = DrawingMode.IMMEDIATE,
    ):
        super().__init__()

        # Auto find CApp Object
        if parent is None:
            parent = self.get_obj("app0")
            if parent is None:
                raise ValueError("Not found main App")

        # Init parent attribute
        self.parent = parent

        if isinstance(parent, App):
            self.app = parent
        elif isinstance(parent, WindowBase):
            self.app = parent.app
        self.app.add_window(self)

        # Init Attributes
        self.new(
            "ui.framework", self._get_ui_framework(), get_func=self._get_ui_framework
        )  # The UI Framework
        self.new(
            "ui.is_vsync", self._get_ui_is_vsync(), get_func=self._get_ui_is_vsync
        )  # Whether to enable VSync

        match self["ui.framework"]:
            case UIFrame.GLFW:
                self.glfw = self.app.glfw
            case UIFrame.SDL:
                self.sdl3 = self.app.sdl3
            case _:
                raise ValueError(f"Unknown UI Framework: {self['ui.framework']}")

        self.new("ui.draw_func", None)

        self.new(
            "drawing.framework",
            self._get_drawing_framework(),
            get_func=self._get_drawing_framework,
        )
        self.new("drawing.mode", drawing_mode)

        match self["drawing.framework"]:
            case DrawingFrame.SKIA:
                self.skia = self.app.skia
                self.new("drawing.surface", None)
            case _:
                raise ValueError(f"Unknown Drawing Framework: {self['drawing.framework']}")

        self.new(
            "backend.framework",
            self._get_backend_framework(),
            get_func=self._get_backend_framework,
        )

        match self["backend.framework"]:
            case BackendFrame.OPENGL:
                self.opengl = self.app.opengl
                self.opengl_GL = self.app.opengl_GL
                self.new("backend.context", None)
            case _:
                raise ValueError(f"Unknown Backend Framework: {self['backend.framework']}")

        self.new("pos", Pos(0, 0))  # Always (0, 0)
        self.new("canvas_pos", Pos(0, 0))  # Always (0, 0)
        self.new("root_pos", Pos(0, 0), set_func=self._set_pos)  # The position of the window
        self.new("size", Size(size[0], size[1]), set_func=self._set_size)  # The size of the window
        self.new("title", title, set_func=self._set_title)  # The title of the window

        self.is_dirty: bool = False
        self.is_force_hardware_acceleration: bool = fha
        self.is_visible: bool = False  # Is the window visible
        self.is_alive: bool = False  # Is the window alive

        self.the_window = self.create()  # GLFW/SDL Window

        self.create_event_bounds()

        self.bind("on_move", self._on_move)
        self.bind("on_resize", self._on_resize)

    def create(self):
        """Create the window."""
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
                    if self.is_force_hardware_acceleration:
                        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
                        glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
                        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
                        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
                        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

                _size = self.get("size", skip=True)
                window = glfw.create_window(
                    _size["width"], _size["height"], self.get("title"), None, None
                )
                if not window:
                    raise RuntimeError("Can't create window")

                self.is_visible = True
                self.is_alive = True

                pos = glfw.get_window_pos(window)

                _root_point = self.get("root_pos", skip=True)
                _root_point.set("x", pos[0])
                _root_point.set("y", pos[1])

        return window

    def create_event_bounds(self):
        """Create event bounds."""
        match self.get("ui.framework"):
            case UIFrame.GLFW:
                self.glfw.set_window_size_callback(
                    self.the_window,
                    lambda window, width, height: self.trigger(
                        Event(self, "resize", width=width, height=height)
                    ),
                )
                self.glfw.set_window_pos_callback(
                    self.the_window,
                    lambda window, root_x, root_y: self.trigger(
                        Event(self, "move", x_root=root_x, y_root=root_y)
                    ),
                )

    def update(self):
        """Update the window. When is_dirty is True, draw the window."""
        if self.is_visible:
            match self["drawing.mode"]:
                case DrawingMode.IMMEDIATE:
                    self.draw()
                case DrawingMode.RETAINED:
                    if self.is_dirty:
                        self.draw()
                        self.is_dirty = False

    import contextlib

    @contextlib.contextmanager
    def skia_surface(self, arg: typing.Any):
        """Create a Skia surface for the window.

        :param arg: GLFW or SDL2 Window/Surface
        :return: Skia Surface
        """
        match self["ui.framework"]:
            case UIFrame.GLFW:
                if not self.glfw.get_current_context() or self.glfw.window_should_close(arg):
                    yield None
                    return

                match self["backend.framework"]:
                    case BackendFrame.OPENGL:
                        match self["drawing.framework"]:
                            case DrawingFrame.SKIA:
                                self["backend.context"] = self.skia.GrDirectContext.MakeGL()
                                fb_width, fb_height = self.glfw.get_framebuffer_size(arg)
                                backend_render_target = self.skia.GrBackendRenderTarget(
                                    fb_width,
                                    fb_height,
                                    0,
                                    0,
                                    self.skia.GrGLFramebufferInfo(0, self.opengl_GL.GL_RGBA8),
                                )
                                surface = self.skia.Surface.MakeFromBackendRenderTarget(
                                    self["backend.context"],
                                    backend_render_target,
                                    self.skia.kBottomLeft_GrSurfaceOrigin,
                                    self.skia.kRGBA_8888_ColorType,
                                    self.skia.ColorSpace.MakeSRGB(),
                                )
                                self["backend.context"].setResourceCacheLimit(16 * 1024 * 1024)

                                if surface is None:
                                    raise RuntimeError("Failed to create Skia surface")

                                yield surface

            case UIFrame.SDL:
                import ctypes

                width, height = arg.w, arg.h
                pixels_ptr = arg.pixels
                pitch = arg.pitch

                # SDL 像素包装成 buffer
                buf_type = ctypes.c_uint8 * (pitch * height)
                buf = buf_type.from_address(pixels_ptr)  # NOQA

                imageinfo = self.skia.ImageInfo.MakeN32Premul(width, height)  # NOQA
                surface = self.skia.Surface.MakeRasterDirect(imageinfo, buf, pitch)

                if surface is None:
                    raise RuntimeError("Failed to create Skia surface")

                yield surface  # ⚠️ 必须用 yield，不要 return

    def draw(self, event: Event = None) -> None:  # NOQA
        """Draw the window.

        Args:
            event (CEvent, optional): The event that triggered the draw. Defaults to None.
        """
        if self.is_visible:
            # Set the current context for each arg
            # 【为该窗口设置当前上下文】
            match self["ui.framework"]:
                case UIFrame.GLFW:
                    self.glfw.make_context_current(self.the_window)

                    match self["drawing.framework"]:
                        case DrawingFrame.SKIA:
                            # Create a Surface and hand it over to this arg.
                            # 【创建Surface，交给该窗口】
                            with self.skia_surface(self.the_window) as self[
                                "drawing.surface"
                            ]:  # NOQA
                                if self["drawing.surface"]:
                                    with self["drawing.surface"] as canvas:
                                        # Determine and call the drawing function of this arg.
                                        # 【判断并调用该窗口的绘制函数】
                                        if self["ui.draw_func"]:
                                            self["ui.draw_func"](canvas)

                                    self["drawing.surface"].flushAndSubmit()
                    if self.is_alive:
                        self.glfw.swap_buffers(self.the_window)
                case "sdl2":
                    import sdl2

                    surface = sdl2.SDL_GetWindowSurface(self.the_window).contents

                    with self.skia_surface(surface) as self["drawing.surface"]:  # NOQA
                        if self["drawing.surface"]:
                            with self["drawing.surface"] as canvas:
                                if self["ui.draw_func"]:
                                    self["ui.draw_func"](canvas)

                    sdl2.SDL_UpdateWindowSurface(self.the_window)  # NOQA
        if self["backend.context"]:
            self["backend.context"].freeGpuResources()
            self["backend.context"].releaseResourcesAndAbandonContext()
        # for child in self.children:
        #    child.need_redraw = False
        self.trigger(Event(self, "draw"))

    def dirty(self):
        """Set the dirty flag."""
        self.is_dirty = True

    def cancel_dirty(self):
        """Cancel the dirty flag."""
        self.is_dirty = False

    def destroy(self) -> None:
        """Destroy the window.

        :return: None
        """
        # self._event_init = False
        # print(self.id)
        self.app.destroy_window(self)
        match self.get("ui.framework"):
            case UIFrame.GLFW:
                import glfw

                try:
                    glfw.destroy_window(self.the_window)
                except TypeError:
                    pass

        self.is_alive = False
        # self.draw_func = None
        self.the_window = None  # Clear the reference

    def can_be_close(self, value: bool | None = None) -> typing.Self | bool:
        """Set whether the window can be closed.

        Prevent users from closing the window, which can be used in conjunction with prompts like "Save before closing?"

        >>> def delete(_: SkEvent):  # NOQA
        >>>     window.can_be_close(False)  # NOQA
        >>> window.bind("delete_window", delete)  # NOQA


        :param value: Whether the window can be closed
        :return: None
        """
        match self.get("ui.framework"):
            case UIFrame.GLFW:
                import glfw

                if value is not None:
                    glfw.set_window_should_close(self.the_window, value)
                    return self
                else:
                    if self.the_window:
                        return glfw.window_should_close(self.the_window)
                    else:
                        return False
        return True

    # region Getters and Setters
    def _get_ui_framework(self):
        return self.app.get("ui.framework")

    def _get_drawing_framework(self):
        return self.app.get("drawing.framework")

    def _get_backend_framework(self):
        return self.app.get("backend.framework")

    def _get_ui_is_vsync(self):
        return self.app.get("ui.is_vsync")

    def _set_size(self, size: Size | tuple[int, int]) -> None:
        """Set the size of the window.

        Args:
            size (Size | tuple[int, int]): Size to set.
        Returns:
            None
        """
        if isinstance(size, tuple):
            match self["ui.framework"]:
                case UIFrame.GLFW:
                    self.glfw.set_window_size(self.the_window, size[0], size[1])
        else:
            match self["ui.framework"]:
                case UIFrame.GLFW:
                    self.glfw.set_window_size(self.the_window, size["width"], size["height"])

    def resize(self, size: Size | tuple[int, int]) -> None:
        """Resize the window to the given size.

        Args:
            size: Size to resize.
        Returns:
            None
        """
        self.set("size", size)

    def _set_pos(self, pos: Pos | tuple[int, int]) -> None:
        """Set the position of the window.

        Args:
            pos (CPOS | tuple[int, int]): Position to set
        Returns:
            None
        """
        if isinstance(pos, tuple):
            if self["ui.framework"] == UIFrame.GLFW:
                self.glfw.set_window_pos(self.the_window, pos[0], pos[1])
        else:
            if self["ui.framework"] == UIFrame.GLFW:
                self.glfw.set_window_pos(self.the_window, pos["x"], pos["y"])

    def move(self, pos: Pos | tuple[int, int]) -> None:
        """Move the window to the given position.

        Args:
            pos: Position to move
        Returns:
            None
        """
        self.set("root_pos", pos)

    def _set_title(self, title: str) -> None:
        """Set the title of the window.

        Args:
            title (str): Title to set
        Returns:
            None
        """
        if self["ui.framework"] == UIFrame.GLFW:
            self.glfw.set_window_title(self.the_window, title)

    # endregion

    # region Events

    def _on_move(self, event: Event):
        """Handle the move event.

        Args:
            event (Event): The move event.
        """
        _root_point = self.get("root_pos", skip=True)
        _root_point.set("x", event["x_root"])
        _root_point.set("y", event["y_root"])

    def _on_resize(self, event: Event):
        """Handle the resize event.

        Args:
            event (Event): The resize event.
        """
        _size = self.get("size", skip=True)
        _size(event["width"], event["height"])
        self.dirty()

    # endregion
