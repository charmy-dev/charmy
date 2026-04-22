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
import rsvg
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
    """Flags all supported features."""
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
    
    def __init__(self):
        """Creates a window."""
        super().__init__()

        self.supports = WindowSupportState()

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

        # 获取 Cairo 数据（memoryview）
        cairo_data = self.surface.get_data()
        
        # 获取窗口表面
        self._window_surface = sdl2.SDL_GetWindowSurface(self.window)
        
        # 锁定表面
        sdl2.SDL_LockSurface(self._window_surface)
        
        # 获取像素指针
        pixels_ptr = self._window_surface.contents.pixels
        
        # 优化：直接从 memoryview 获取底层指针，避免 tobytes() 拷贝
        # 计算数据大小
        pitch = self._window_surface.contents.pitch
        data_size = pitch * self.size[1]  # self.size[1] 是高度
        
        # 关键：将 memoryview 转换为 ctypes 指针，零拷贝
        cairo_ptr = ctypes.cast(
            (ctypes.c_char * data_size).from_buffer(cairo_data),
            ctypes.c_void_p
        )
        
        # 复制数据
        ctypes.memmove(pixels_ptr, cairo_ptr, data_size)
        
        # 解锁表面
        sdl2.SDL_UnlockSurface(self._window_surface)
        
        # 更新窗口显示
        sdl2.SDL_UpdateWindowSurface(self.window)

        # 处理事件
        for event in sdl2.ext.get_events():
            match event.type:
                case sdl2.SDL_QUIT:
                    sys.exit(0)
                    NotImplemented

    def draw_frame(self) -> None:
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
class ShapeSupportState(template.ShapeSupportState):
    polyline         = True
    round_rect       = True
    polygon          = True
    round_rect       = True
    arc              = True
    oval             = True
    sector           = True
    beizer_curve     = True
    svg              = True
    func_shape       = False
    paths_defined    = True

class Shape(template.Shape):
    """Represent a shape in the Genesis backend that can be drawn."""
    def __init__(self, 
                 shape_type: str, 
                 shape_params: dict[str, typing.Any], 
                 pos: tuple[int, int] = (0, 0), 
                 texture: Texture | str | tuple[int, int, int] = "#00ff00", 
                 ):
        """To create a shape in backend.
        
        Args:
            type: Any of `polygon`, `round_rect`, `oval`, `beizer_curve`
            shape_param:
                - For polyline: `{"points": list[tuple[int, int]]}`
                - For rect: `{"points": list[tuple[int, int]]}`
                - For polygon: `{"points": list[tuple[int, int]]}`
                - For round rect: `{"width": int, "height": int, "radius": int}`
                - For arc: `{"radius": int, "start_orient": int | float, "end_orient": int | float}`
                - For oval: `{"l_radius": int, "s_radius": int, "orientation": int | float}`
                - For sector: `{"radius": int, "start_orient": int | float, "end_orient": int | float}`
                - For beizer curve: `{"points": list[tuple[int, int]]}`
                - For svg: `{"svg_data": str}`
        """
        super().__init__(shape_type, shape_params, pos, texture)
    
    def draw(self, window: WindowBase):
        match self.type:
            case "polygon":
                points = self.shape_params["points"]
                for i, (x, y) in enumerate(points):
                    if i == 0:
                        window.cairo_context.move_to(x, y)
                    else:
                        window.cairo_context.line_to(x, y)
                window.cairo_context.fill()
            case _:
                template.placeholder_function("")