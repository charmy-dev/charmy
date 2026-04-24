# The Genesis Backend
# 2026 by XiangQinXi & rgzz666

# This is a backend for early development only! 
# It is also used as an example of developing a Charmy backend.

# Under dev

import typing

from dataclasses import dataclass
import sdl2
import sdl2.ext
import cairo
import sys
import ctypes

from . import template


class Backend(template.Backend):
    """The Genesis backend."""

    name =          "genesis"
    friendly_name = "Genesis (early development)"
    version =       "0.1.0"
    author =        ["XiangQinXi", "rgzz666"]

    def __init__(self):
        """APIs are alised here."""
        super().__init__()

        self.WindowBase = WindowBase
    
    def backend_init(self, **kwargs) -> None:
        sdl2.ext.init()


@dataclass
class WindowSupportState(template.WindowSupportState):
    """Flags all supported window features."""
    set_title               = True
    set_icon                = True
    resize                  = True
    set_scale_mode          = False
    set_background          = True
    translucent             = True
    set_state               = True
    fullscreen              = True
    customize_titlebar      = False

class WindowBase(template.WindowBase):
    """Window APIs in Genesis backend."""
    supports = WindowSupportState()
    Backend = Backend

    def __init__(self, backend: template.Backend):
        """Creates a window.
        
        Args:
            backend: The backend that this window uses (can be get from CharmyManager)
        """
        super().__init__(backend)

        self.title = "Charmy SDL2 Window"
        self.size = (540, 480)

        # create window
        self.window: typing.Any = sdl2.SDL_CreateWindow(
            self.title.encode('utf-8'),
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            self.size[0], self.size[1],
            sdl2.SDL_WINDOW_SHOWN
        )
        
        if not self.window:
            raise RuntimeError("Can't create window")
        self._window_surface = sdl2.SDL_GetWindowSurface(self.window)

        if self.window == None:
            raise RuntimeError("Can't create window")
        
        # Initialize Cairo canvas
        self.surface: cairo.ImageSurface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self.size[0], self.size[1])
        self.cairo_context: cairo.Context = cairo.Context(self.surface)
        self.cairo_context.set_source_rgb(0, 0, 0)  # 黑色背景
        self.cairo_context.paint()

    def show(self) -> typing.Self:
        """Show the window.

        Returns:
            self: The WindowBase itself.
        """
        # self.window.show()
        return self

    def set_title(self, new: str) -> typing.Self:
        """Set window title."""
        self.window.title = new
        return self
    
    def update(self):
        """Update the window.
        
        Returns:
            self: The WindowBase itself.
        """
        self.draw_frame()

        # Following Vibed with Deepseek

        # Get Cairo data（memoryview）
        cairo_data = self.surface.get_data()

        # Get SDL2 window surface
        self._window_surface = sdl2.SDL_GetWindowSurface(self.window)
        # Lock the surface
        sdl2.SDL_LockSurface(self._window_surface)

        # Get pixels pointer
        pixels_ptr = self._window_surface.contents.pixels
        # Improvement: Get lower level pointer directly to avoid tobytes() copy
        # Calc data size
        pitch = self._window_surface.contents.pitch
        data_size = pitch * self.size[1]
        # Convert memoryview to ctypes data
        cairo_ptr = ctypes.cast(
            (ctypes.c_char * data_size).from_buffer(cairo_data),
            ctypes.c_void_p
        )

        # Copy data
        ctypes.memmove(pixels_ptr, cairo_ptr, data_size)
        # Unlock surface
        sdl2.SDL_UnlockSurface(self._window_surface)

        # Update display
        sdl2.SDL_UpdateWindowSurface(self.window)

        # Handle events
        for event in sdl2.ext.get_events():
            match event.type:
                case sdl2.SDL_QUIT:
                    sys.exit(0)
                    NotImplemented

    def draw_frame(self) -> None:
        # Test code for drawing, vibed with Doubao or Deepseek (whatever, I forgot)

        self.cairo_context.set_source_rgb(1, 1, 1)  # 使用 set_source_rgb 而不是 set_source_rgba
        self.cairo_context.paint()
        
        # 绘制红色圆形
        self.cairo_context.set_source_rgb(1, 0, 0)  # 完全不透明的红色
        self.cairo_context.arc(270, 240, 80, 0, 6.28)
        self.cairo_context.fill()
        
        # 可选：添加边框让圆形更明显
        self.cairo_context.set_source_rgb(0, 0, 0)
        self.cairo_context.arc(270, 240, 80, 0, 6.28)
        self.cairo_context.set_line_width(2)
        self.cairo_context.stroke()
    
    def mainloop(self):
        while True:
            self.update()


@dataclass
class LineSupportState(template.LineSupportState):
    """Flags all supported line types."""
    polyline     = True
    arc          = True
    beizer       = True

class LineBase():
    """Represents lines in backend."""

    supports: LineSupportState = LineSupportState()
    Backend: type[Backend] = Backend

    def __init__(self):
        ...