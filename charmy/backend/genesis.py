# The Genesis Backend
# 2026 by rgzz666 & XiangQinXi & CodeCrafter

# This is a backend for early development only! 
# It is also used as an example of developing a Charmy backend.

# Under dev

from __future__ import annotations as _

import typing

from dataclasses import dataclass
import sdl2
import sdl2.ext
import cairo
import sys
import ctypes
import math

from . import template

import charmy.backend.utils as charmy_stuff

# if typing.TYPE_CHECKING:
#     import charmy_stuff.styles.shape as charmy_stuff.shape
#     import charmy_stuff.styles.texture as cm_texture


# region Backend class

class Backend(template.Backend):
    """The Genesis backend."""

    name: typing.ClassVar[str] =            "genesis"
    friendly_name: typing.ClassVar[str] =   "Genesis (early development)"
    version: typing.ClassVar[str] =         "0.1.0"
    author: typing.ClassVar[list[str]] =    ["rgzz666", "XiangQinXi", "CodeCrafter"]

    WindowBase: type[WindowBase]
    LineBase: type[LineBase]
    ShapeBase: type[ShapeBase]
    TextureBase: type[TextureBase]

    def __init__(self):
        """APIs are aliased here."""
        super().__init__()
    
    def backend_init(self, **kwargs) -> None:
        # sdl2.ext.init()
        return


# region Window

class WindowBackdropSupportState(template.WindowBackdropSupportState):
    """Represents support states of backdrop effects of windows held by this backend."""
    color                   : bool = True
    gradient                : bool = False
    image                   : bool = False
    transparent             : bool = False
    alpha                   : bool = False
    blur                    : bool = False
    transformation          : bool = False
    any_filter              : bool = False

class WindowSupportState(template.WindowSupportState):
    """Flags all supported window features."""
    set_title               : bool = True
    set_icon                : bool = True
    resize                  : bool = True
    set_scale_mode          : bool = True
    set_background          : bool = True
    translucent             : bool = True
    backdrop                : type[WindowBackdropSupportState] = WindowBackdropSupportState
    set_state               : bool = True
    fullscreen              : bool = True
    customize_titlebar      : bool = True

class WindowBase(template.WindowBase):
    """Window APIs in Genesis backend."""
    supports = WindowSupportState()
    Backend = Backend

    def __init__(self, backend: template.Backend):
        """Creates a window.
        
        :param backend: The backend that this window uses (can be get from CharmyManager)
        """
        super().__init__(backend)

        self.title: str = "Charmy SDL2 Window"
        self.size: tuple[int, int] = (540, 480)


        # create window
        self.window: typing.Any = sdl2.SDL_CreateWindow(
            self.title.encode('utf-8'),
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            self.size[0], self.size[1],
            sdl2.SDL_WINDOW_SHOWN,
        )

        if not self.window:
            raise RuntimeError("Can't create window")
        self._window_surface = sdl2.SDL_GetWindowSurface(self.window)

        # sdl2.SDL_SetWindowSize(self.window, self.size[0], self.size[1])

        # Initialize Cairo canvas
        self.surface: cairo.ImageSurface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self.size[0], self.size[1])
        self.cairo_context: cairo.Context = cairo.Context(self.surface)
        self.cairo_context.set_line_join(cairo.LINE_JOIN_ROUND)
        self.cairo_context.set_line_cap(cairo.LINE_CAP_ROUND)
        self.cairo_context.set_source_rgba(0, 0, 0, 0)  # Transparent back
        self.cairo_context.paint()

    def show(self) -> typing.Self:
        """Show the window.

        :return self: The WindowBase itself
        """
        # self.window.show()
        return self

    def set_title(self, new: str) -> typing.Self:
        """Set window title."""
        self.title = new
        sdl2.SDL_SetWindowTitle(self.window, self.title.encode("utf-8"))
        return self
    
    def update(self):
        """Update the window.
        
        :return self: The WindowBase itself
        """
        self.draw_frame(self.drawing_list)

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

    def draw_frame(self, 
                   drawing_list: list[charmy_stuff.draw.DrawnShape | charmy_stuff.draw.DrawnLine]) -> None:
        """Draw a frame for the window.
        
        :param drawing_list: The list of the objects to draw
        """
        for drawing_obj in drawing_list:
            if isinstance(drawing_obj, charmy_stuff.draw.DrawnLine):
                LineBase.draw_line(drawing_obj, self)
            elif isinstance(drawing_obj, charmy_stuff.draw.DrawnShape):
                ShapeBase.draw_shape(drawing_obj, self)
            else:
                template.not_implemented_func(
                    Backend.friendly_name, f"Drawing object type {drawing_obj.__class__.__name__}"
                    )
    
    def mainloop(self):
        while True:
            self.update()


# region Lines

class LineSupportState(template.LineSupportState):
    """Flags all supported line types."""
    line                : bool = True
    polyline            : bool = True
    circle_arc          : bool = True
    ellipse_arc         : bool = False
    quadratic_bezier    : bool = False
    cubic_bezier        : bool = True

class LineBase(template.LineBase):
    """Line-related APIs in Genesis backend."""
    supports: LineSupportState = LineSupportState()

    @staticmethod
    def draw_line(drawn_line: charmy_stuff.draw.DrawnLine, window: WindowBase, stroke: bool = True):
        """To draw a line on a specific window.

        Args:
            line: The line to be drawn
            window: The WindowBase to draw line
        """
        # Unpack the DrawnLine
        line = drawn_line.line
        texture = drawn_line.texture
        line_width = drawn_line.width
        # Detect wrong backend
        if window.Backend != Backend:
            raise RuntimeError(
                "Wrong backend for draw_line()! Asked to draw on a window held by "
                f"{window.backend.friendly_name} but I serve backend {Backend.friendly_name}!"
                )
        # Set texture & line width
        if not TextureBase.cairo_set_context_texture(window.cairo_context, texture):
            return
        window.cairo_context.set_line_width(line_width)
        # Draw line
        if isinstance(line, charmy_stuff.shape.Line):
            painting_pos = tuple([int(v) for v in window.cairo_context.get_current_point()])
            if painting_pos != line.points[0]: # Avoid unnecessary move_to() when drawing shapes
                window.cairo_context.move_to(*line.points[0])
            window.cairo_context.line_to(*line.points[1])
        elif isinstance(line, charmy_stuff.shape.PolyLine):
            window.cairo_context.move_to(*line.points[0])
            for index, point in enumerate(line.points):
                if index == 0:
                    continue
                window.cairo_context.line_to(*point)
        elif isinstance(line, charmy_stuff.shape.CircleArc):
            # window.cairo_context.move_to(*line.center)
            start_orient_rad = (line.start_orient - 90) * (math.pi / 180)
            end_orient_rad = (line.end_orient - 90) * (math.pi / 180)
            window.cairo_context.arc(line.center[0], line.center[1], line.radius, 
                                     start_orient_rad, end_orient_rad)
        elif isinstance(line, charmy_stuff.shape.CubicBezier):
            window.cairo_context.move_to(*line.points[0])
            window.cairo_context.curve_to(
                *line.points[1], *line.points[2], *line.points[3]
                )
        else:
            template.not_implemented_func(Backend.friendly_name, f"Drawing line type {line.type}")
        if stroke:
            window.cairo_context.stroke()


# region Shapes

class ShapeSupportState(template.ShapeSupportState):
    """Flags support state of shape types of this backend."""
    any_shape       : bool = True
    rect            : bool = False
    round_rect      : bool = False
    polygon         : bool = False
    oval            : bool = False
    sector          : bool = False

class ShapeBase(template.ShapeBase):
    """Shape-related APIs in Genesis backend."""
    supports: ShapeSupportState = ShapeSupportState()

    @staticmethod
    def draw_any_shape(drawn_shape: charmy_stuff.draw.DrawnShape, window: WindowBase):
        """Draw shape by lines."""
        for line in drawn_shape.shape.lines:
            # Border drawn at this time will be covered by shape itself
            # These lines are for drawing the shape itself, not for border
            drawn_line = charmy_stuff.draw.DrawnLine(line, drawn_shape.texture, 1)
            LineBase.draw_line(drawn_line, window, stroke=False)
        window.cairo_context.close_path()
        if TextureBase.cairo_set_context_texture(window.cairo_context, drawn_shape.texture):
            window.cairo_context.fill()
        window.cairo_context.stroke()
        if TextureBase.cairo_set_context_texture(window.cairo_context, drawn_shape.border_texture) \
            and drawn_shape.border_width != 0:
            # If still need visible border, then draw again
            for line in drawn_shape.shape.lines:
                drawn_line = charmy_stuff.draw.DrawnLine(
                    line, drawn_shape.border_texture, drawn_shape.border_width)
                LineBase.draw_line(drawn_line, window)

    @staticmethod
    def draw_shape(shape: charmy_stuff.draw.DrawnShape, window: WindowBase):
        if isinstance(shape.shape, charmy_stuff.shape.AnyShape):
            ShapeBase.draw_any_shape(shape, window)
        else:
            template.not_implemented_func(Backend.friendly_name, 
                    f"Drawing an shae that is not a subclass of AnyShape")


# region Textures

class TextureSupportState(template.TextureSupportState):
    color           : bool = False
    linear_gradient : bool = False
    radial_gradient : bool = False
    filter          : bool = False
    image           : bool = False
    func_shader     : bool = False

class TextureBase(template.TextureBase):
    """Texture-related APIs in Genesis backend."""

    @staticmethod
    def cairo_set_context_texture(context: cairo.Context, 
                                  texture: charmy_stuff.texture.Texture) -> bool:
        """Set texture of a Cairo context, and returns if following drawing still needs to be done. 
        
        function only available in Genesis backend.

        :param context: The Cairo context to set texture
        :param texture: The texture to set
        :return bool: If the object needs to be drawn
        """
        cmtx = charmy_stuff.texture
        if isinstance(texture, cmtx.Transparent):
            context.set_source_rgba(0, 0, 0, 0)
            return False
        if isinstance(texture, cmtx.Color):
            context.set_source_rgba(*[v / 255 for v in texture])
        else:
            template.not_implemented_func(
                Backend.friendly_name, f"Drawing texture type {texture.__class__.__name__}"
                )
        return True


# region Texts
class TextBase(template.TextBase):
    """Text-related APIs in Genesis backend."""

    @staticmethod
    def draw_text(text):
        # TODO: Implement this fucking text-drawing func
        pass

# region: Alias WhateverBase classes

Backend.WindowBase = WindowBase
Backend.LineBase = LineBase
Backend.ShapeBase = ShapeBase
Backend.TextureBase = TextureBase

# endregion