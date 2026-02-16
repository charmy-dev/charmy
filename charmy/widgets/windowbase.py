import typing

from ..const import MANAGER_ID, Backends, DrawingMode
from ..event import Event, EventHandling
from ..object import CharmyObject
from ..pos import Pos
from ..size import Size
from .cmm import CharmyManager


class WindowBase(EventHandling, CharmyObject):
    """WindowBase is a base class for window.

    Args:
        parent: The CharmyManager object,
        title: The title of the window,
        size: The size of the window,
        fha: Whether to force hardware acceleration
        drawing_mode: The drawing mode of the window,
    """

    def __init__(
        self,
        parent: CharmyManager | None = None,
        *,
        title: str = "Charmy GUI",
        size: tuple[int, int] = (100, 100),
        fha: bool = True,
        drawing_mode: DrawingMode = DrawingMode.RETAINED,
    ):
        super().__init__()

        # Init parent attribute
        if parent is None:
            parent = self.get_obj(MANAGER_ID)

        if isinstance(parent, CharmyManager):
            self.manager = parent
        elif isinstance(parent, WindowBase):
            self.manager = parent.manager
        self.manager.add_window(self)

        # Init Attributes
        self.new("framework", self._get_framework(), get_func=self._get_framework)  # The Framework
        self.new(
            "ui.is_vsync", self._get_ui_is_vsync(), get_func=self._get_ui_is_vsync
        )  # Whether to enable VSync

        self.new("ui.draw_func", None)

        self.new("drawing.mode", drawing_mode)

        match self["framework"].ui_name:
            case "GLFW":
                self.glfw = self["framework"].ui.glfw
            case _:
                raise ValueError(f"Unknown UI Framework: {self['framework'].ui_name}")

        match self["framework"].drawing_name:
            case "SKIA":
                self.skia = self["framework"].drawing.skia
                self.new("drawing.surface", None)
            case _:
                raise ValueError(f"Unknown Drawing Framework: {self['framework'].drawing_name}")

        match self["framework"].backend_name:
            case "OPENGL":
                self.opengl = self["framework"].backend.opengl
                self.opengl_GL = self["framework"].backend.opengl_GL
                self.new("backend.context", None)
            case _:
                raise ValueError(f"Unknown Backend Framework: {self['framework'].backend_name}")

        self.new("pos", Pos(0, 0))  # Always (0, 0)
        self.new("canvas_pos", Pos(0, 0))  # Always (0, 0)
        self.new("root_pos", Pos(0, 0), set_func=self._set_pos)  # The position of the window
        self.new("size", Size(size[0], size[1]), set_func=self._set_size)  # The size of the window
        self.new("title", title, set_func=self._set_title)  # The title of the window

        self.is_dirty: bool = True
        self.is_force_hardware_acceleration: bool = fha
        self.is_visible: bool = False  # Is the window visible
        self.is_alive: bool = False  # Is the window alive

        self.the_window = self.create()  # GLFW/SDL Window

        self.create_event_bounds()

        self.bind("move", self._on_move)
        self.bind("resize", self._on_resize)

    def create(self):
        """Create the window."""
        arg = self["framework"].ui.create(
            size=self.get("size", skip=True),
            title=self.get("title"),
            fha=self.is_force_hardware_acceleration,
        )

        _root_point = self.get("root_pos", skip=True)(arg["pos"][0], arg["pos"][1])

        self.is_visible = True
        self.is_alive = True

        return arg["window"]

    def create_event_bounds(self):
        """Create event bounds."""
        self["framework"].ui.create_event_bounds(the_window=self.the_window, window_class=self)

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
        match self["framework"].ui_name:
            case "GLFW":
                if not self.glfw.get_current_context() or self.glfw.window_should_close(arg):
                    yield None
                    return

                match self["framework"].backend_name:
                    case "OPENGL":
                        match self["framework"].drawing_name:
                            case "SKIA":
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

            case "SDL":
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

    def draw(self, event: Event | None = None) -> None:  # NOQA
        """Draw the window.

        Args:
            event (CEvent, optional): The event that triggered the draw. Defaults to None.
        """
        if self.is_visible:
            # Set the current context for each arg
            # 【为该窗口设置当前上下文】
            match self["framework"].ui_name:
                case "GLFW":
                    self["framework"].ui.make_context_current(self.the_window)

                    match self["framework"].drawing_name:
                        case "SKIA":
                            # Create a Surface and hand it over to this arg.
                            # 【创建Surface，交给该窗口】
                            with self.skia_surface(self.the_window) as self[  # NOQA
                                "drawing.surface"
                            ]:  # NOQA
                                if self["drawing.surface"]:
                                    with self["drawing.surface"] as canvas:
                                        # Determine and call the drawing function of this arg.
                                        # 【判断并调用该窗口的绘制函数】
                                        if self["ui.draw_func"]:
                                            self["ui.draw_func"](canvas)

                                    self["drawing.surface"].flushAndSubmit()
                case "SDL":
                    import sdl2  # NOQA

                    surface = sdl2.SDL_GetWindowSurface(self.the_window).contents

                    with self.skia_surface(surface) as self["drawing.surface"]:  # NOQA
                        if self["drawing.surface"]:
                            with self["drawing.surface"] as canvas:
                                if self["ui.draw_func"]:
                                    self["ui.draw_func"](canvas)

                    sdl2.SDL_UpdateWindowSurface(self.the_window)  # NOQA

            if self.is_alive:
                self["framework"].ui.swap_buffers(self.the_window)

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
        try:
            self["framework"].ui.destroy(the_window=self.the_window)
        except TypeError:
            pass
        finally:
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
        match self["framework"].ui_name:
            case "GLFW":
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
    def _get_framework(self):
        return self.manager.get("framework")

    def _get_ui_is_vsync(self):
        return self.manager.get("ui.is_vsync")

    def _set_size(self, size: Size | tuple[int, int]) -> None:
        """Set the size of the window.

        Args:
            size (Size | tuple[int, int]): Size to set.
        Returns:
            None
        """
        self["framework"].ui.set_size(the_window=self.the_window, size=size)

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
        self["framework"].ui.set_pos(the_window=self.the_window, pos=pos)

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
        self["framework"].ui.set_title(the_window=self.the_window, title=title)

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
