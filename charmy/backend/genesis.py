# The Genesis Backend
# 2026 by rgzz666 & XiangQinXi & CodeCrafter

# This is a backend for early development only! 
# It is also used as an example of developing a Charmy backend.

# Under dev

from __future__ import annotations as _

import typing

# import sdl2
import sdl2.ext
import cairo
import sys
import os
import tempfile
import ctypes
import math
import warnings
import time

from charmy.backend import template

import charmy.backend.utils as charmy_stuff

if typing.TYPE_CHECKING:
    from charmy.widgets import window

__all__ = ["Backend", "DEBUG_FLAGS"]


class DEBUG_FLAGS:
    DRAW_CAIRO_STOCK_TEXT_BOUND : bool = False
    FORCE_CLOSE_SHAPE           : bool = False
    OBSERVE_SHAPE_DRAWING       : bool = False
    WARN_UNCLOSED_SHAPES        : bool = False


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
    gradient                : bool = True
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
    set_pos                 : bool = True
    set_size                : bool = True
    set_scale_mode          : bool = True
    set_background          : bool = True
    translucent             : bool = True
    backdrop                : type[WindowBackdropSupportState] = WindowBackdropSupportState
    set_state               : bool = True
    fullscreen              : bool = True
    customize_titlebar      : bool = False

class WindowBase(template.WindowBase):
    """Window APIs in Genesis backend."""
    supports = WindowSupportState()
    Backend = Backend

    def __init__(self, backend: template.Backend, charmy_window: window.WindowEntity):
        """Creates a window.

        :param backend: The backend that this window uses (can be get from CharmyManager)
        """
        super().__init__(backend, charmy_window)

        self.title: str = "Charmy SDL2 Window"
        self.size: tuple[int, int] = (540, 480)

        # Create window
        self.window: typing.Any = sdl2.SDL_CreateWindow(
            self.title.encode('utf-8'),
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            self.size[0], self.size[1],
            sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_RESIZABLE, 
        )

        # Sync window pos to higher level stuff
        x, y = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GetWindowPosition(self.window, x, y)
        self.charmy_window._pos = (x.value, y.value)

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
        self.cairo_context.set_source_rgba(0, 0, 0, 255)  # Black back
        self.cairo_context.paint()

    def show(self) -> typing.Self:
        """Show the window.

        :return self: The WindowBase itself
        """
        # self.window.show()
        return self

    def cairo_reinit_surface(self):
        """Re-init Cairo surface and canvas, only avail in Genesis backend."""
        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self.size[0], self.size[1])
        self.cairo_context = cairo.Context(self.surface)

    def set_pos(self, new: charmy_stuff.styles.shape.Point) -> typing.Self:
        """Set window position.

        :param new: New window pos
        """
        if new == self.pos:
            return self
        self.pos = new
        sdl2.SDL_SetWindowPosition(self.window, new[0], new[1])
        return self

    def set_size(self, new: charmy_stuff.styles.shape.Size, _passive: bool = False) -> typing.Self:
        """Set window size.

        :param new: The new window size in tuple of `(width, height)`
        :param _passive: Whether the resize is triggered by dragging window etc., internal use only
        """
        if new == self.size:
            return self
        self.size = new
        if not _passive:
            sdl2.SDL_SetWindowSize(self.window, new[0], new[1])
        self.cairo_reinit_surface()
        # print(f"Set size to {self.size}")
        return self

    def set_title(self, new: str) -> typing.Self:
        """Set window title.

        :param new: The new window size in string
        """
        self.title = new
        sdl2.SDL_SetWindowTitle(self.window, self.title.encode("utf-8"))
        return self

    def set_icon(self, new: bytes) -> typing.Self:
        """Set window icon from image bytes.

        :param new: New icon in bytes data
        """
        icon_f = tempfile.NamedTemporaryFile(delete=False)
        icon_f.write(new)
        temp_path = icon_f.name
        icon_f.close()
        surface = sdl2.ext.image.load_img(temp_path)
        sdl2.SDL_SetWindowIcon(self.window, surface)
        sdl2.SDL_FreeSurface(surface)
        os.unlink(temp_path)
        return self

    def sdl2_handle_event(self, event: sdl2.SDL_Event) -> None:
        """Handle SDL2 events and trigger upper level Charmy events"""
        cme = charmy_stuff.event_types # Alias Charmy events
        match event.type:
            case sdl2.SDL_WINDOWEVENT:
                match event.window.event:
                    case sdl2.SDL_WINDOWEVENT_RESIZED:
                        self.charmy_window.trigger(cme.ConfigureEvent(
                            self.charmy_window, 
                            {"size": (event.window.data1, event.window.data2)}
                            ))
                        # self.charmy_window.trigger(cme.ResizeEvent(
                        #     self.charmy_window, 
                        #     (event.window.data1, event.window.data2)
                        #     ))
                    case sdl2.SDL_WINDOWEVENT_MOVED:
                        self.charmy_window.trigger(cme.ConfigureEvent(
                            self.charmy_window, 
                            {"pos": (event.window.data1, event.window.data2)}
                            ))
                    case sdl2.SDL_WINDOWEVENT_FOCUS_GAINED:
                        self.charmy_window.trigger(cme.FocusGain(self.charmy_window))
                    case sdl2.SDL_WINDOWEVENT_FOCUS_LOST:
                        self.charmy_window.trigger(cme.FocusLoss(self.charmy_window))
            case sdl2.SDL_MOUSEMOTION:
                self.charmy_window.trigger(cme.MouseMove(
                    self.charmy_window, 
                    (event.motion.x, event.motion.y)
                    ))
            case sdl2.SDL_MOUSEBUTTONDOWN:
                self.charmy_window.trigger(cme.MousePress(
                    self.charmy_window, 
                    (event.button.x, event.button.y), 
                    event.button.button - 1
                    ))
            case sdl2.SDL_MOUSEBUTTONUP:
                self.charmy_window.trigger(cme.MouseRelease(
                    self.charmy_window, 
                    (event.button.x, event.button.y), 
                    event.button.button - 1
                    ))
            case sdl2.SDL_QUIT:
                self.charmy_window.trigger(NotImplemented)

    def update(self, redraw: bool = True) -> typing.Self:
        """Update the window.

        :return self: The WindowBase itself
        """
        if redraw:
            self.draw_frame(self.drawing_list)


        if self.surface.get_width() == self.size[0] and self.surface.get_height() == self.size[1]:
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
            self.sdl2_handle_event(event)
            match event.type:
                case sdl2.SDL_WINDOWEVENT:
                    if event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                        w = ctypes.c_int()
                        h = ctypes.c_int()
                        sdl2.SDL_GetWindowSize(self.window, w, h)
                        self.set_size((w.value, h.value), _passive = True)
        return self


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
    def draw_line(drawn_line: charmy_stuff.graphics.DrawnLine, 
                  window: WindowBase, stroke: bool = True, noskip: bool = False, 
                  *args, **kwargs):
        """To draw a line on a specific window.

        Args:
            line: The line to be drawn
            window: The WindowBase to draw line
        """
        # Unpack the DrawnLine
        line = drawn_line.line
        texture = drawn_line.texture
        line_width = drawn_line.width
        anchor = drawn_line.anchor
        offset = drawn_line.offset

        def calc_point_actual_pos(
                line_point: charmy_stuff.styles.shape.Point, 
                anchor: charmy_stuff.styles.shape.Point, 
                offset: charmy_stuff.styles.shape.Point, 
                ) -> charmy_stuff.styles.shape.Point:
            return (
                line_point[0] - anchor[0] + offset[0], 
                line_point[1] - anchor[1] + offset[1]
                )

        # Detect wrong backend
        if window.Backend != Backend:
            raise RuntimeError(
                "Wrong backend for draw_line()! Asked to draw on a window held by "
                f"{window.Backend.friendly_name} but I serve backend {Backend.friendly_name}!"
                )
        # Set texture & line width
        if not TextureBase.cairo_set_context_texture(window.cairo_context, texture, noskip):
            return
        window.cairo_context.set_line_width(line_width)
        painting_pos = tuple([int(v) for v in window.cairo_context.get_current_point()])
        # Draw line
        if isinstance(line, charmy_stuff.styles.shape.Line):
            # Straight line
            if painting_pos != calc_point_actual_pos(line.points[0], anchor, offset):
                # Avoid unnecessary move_to() when drawing shapes
                window.cairo_context.move_to(
                    *calc_point_actual_pos(line.points[0], anchor, offset)
                    )
            window.cairo_context.line_to(
                *calc_point_actual_pos(line.points[1], anchor, offset)
                )
        elif isinstance(line, charmy_stuff.styles.shape.PolyLine):
            # Polyline
            if painting_pos != calc_point_actual_pos(line.points[0], anchor, offset):
                # Avoid unnecessary move_to() when drawing shapes
                window.cairo_context.move_to(
                    *calc_point_actual_pos(line.points[0], anchor, offset)
                    )
            for index, point in enumerate(line.points):
                if index == 0:
                    continue
                window.cairo_context.line_to(
                    *calc_point_actual_pos(point, anchor, offset)
                    )
        elif isinstance(line, charmy_stuff.styles.shape.CircleArc):
            # Circle arc
            start_orient_rad = (line.start_orient - 90) * (math.pi / 180)
            end_orient_rad = (line.end_orient - 90) * (math.pi / 180)
            window.cairo_context.arc(
                *calc_point_actual_pos(line.center, anchor, offset), 
                line.radius, 
                start_orient_rad, end_orient_rad)
        elif isinstance(line, charmy_stuff.styles.shape.CubicBezier):
            if painting_pos != calc_point_actual_pos(line.points[0], anchor, offset):
                # Avoid unnecessary move_to() when drawing shapes
                window.cairo_context.move_to(
                    *calc_point_actual_pos(line.points[0], anchor, offset)
                    )
            window.cairo_context.curve_to(
                *calc_point_actual_pos(line.points[1], anchor, offset), 
                *calc_point_actual_pos(line.points[2], anchor, offset), 
                *calc_point_actual_pos(line.points[3], anchor, offset), 
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
    def draw_any_shape(drawn_shape: charmy_stuff.graphics.DrawnShape, 
                       window: WindowBase, stroke: bool = True, noskip: bool = False, 
                       *args, **kwargs) -> None:
        """Draw shape by lines."""
        if not isinstance(drawn_shape.shape, charmy_stuff.styles.shape.AnyShape):
            warnings.warn("draw_any_shape() is only for drawing AnyShape")
            return
        if DEBUG_FLAGS.WARN_UNCLOSED_SHAPES:
            last_line_end = drawn_shape.shape.lines[-1].end_point
        for line in drawn_shape.shape.lines:
            # Border drawn at this time will be covered by shape itself
            # These lines are for drawing the shape itself, not for border
            if DEBUG_FLAGS.FORCE_CLOSE_SHAPE:
                # Dirty fix of closing shape: connect the path manually after drawing each line
                window.cairo_context.line_to(
                    line.start_point[0] + drawn_shape.offset[0] - drawn_shape.anchor[0], 
                    line.start_point[1] + drawn_shape.offset[1] - drawn_shape.anchor[1], 
                )
            drawn_line = charmy_stuff.graphics.DrawnLine(
                line, 
                (255, 0, 0, 255 if DEBUG_FLAGS.OBSERVE_SHAPE_DRAWING else 0), 
                1, 
                offset=drawn_shape.offset, 
                anchor=drawn_shape.anchor, 
                )
            # drawn_line.anchor = drawn_shape.shape.boundary[0]
            LineBase.draw_line(drawn_line, window, stroke=False, noskip=True)
            if DEBUG_FLAGS.OBSERVE_SHAPE_DRAWING:
                window.cairo_context.stroke_preserve()
                window.update(redraw=False)
                time.sleep(0.5)
            if DEBUG_FLAGS.WARN_UNCLOSED_SHAPES:
                if line.start_point != last_line_end:
                    print(
                        f"Shape not closed: {last_line_end} -> {line.start_point}"
                        f" | {DEBUG_FLAGS.FORCE_CLOSE_SHAPE=}"
                        )
                last_line_end = line.end_point
        window.cairo_context.close_path()
        if DEBUG_FLAGS.OBSERVE_SHAPE_DRAWING:
            window.cairo_context.stroke_preserve()
            window.update(redraw=False)
            time.sleep(0.5)
        if not stroke:
            return
        if TextureBase.cairo_set_context_texture(window.cairo_context, drawn_shape.texture, noskip):
            window.cairo_context.set_fill_rule(cairo.FILL_RULE_WINDING)
            window.cairo_context.fill()
        window.cairo_context.stroke()
        if TextureBase.cairo_set_context_texture(
            window.cairo_context, drawn_shape.border_texture, noskip) \
            and drawn_shape.border_width != 0:
            # If still need visible border, then draw again
            for line in drawn_shape.shape.lines:
                drawn_line = charmy_stuff.graphics.DrawnLine(
                    line, drawn_shape.border_texture, drawn_shape.border_width, 
                    offset=drawn_shape.offset, anchor=drawn_shape.anchor)
                LineBase.draw_line(drawn_line, window)

    @staticmethod
    def draw_shape_group(drawn_shape: charmy_stuff.graphics.DrawnShape, 
                         window: WindowBase, stroke: bool = True, noskip: bool = False, 
                         *args, **kwargs) -> None:
        if not isinstance(drawn_shape.shape, charmy_stuff.styles.shape.ShapeGroup):
            raise TypeError("draw_shape_group() is only designed for shape group")
        for index, subshape in enumerate(drawn_shape.shape.shapes):
            host = drawn_shape.copy()
            host.shape = subshape
            ShapeBase.draw_shape(
                host, 
                window, 
                index == len(drawn_shape.shape.shapes) - 1 and not stroke, 
                noskip, 
                *args, **kwargs, 
                )

    @staticmethod
    def draw_shape(drawn_shape: charmy_stuff.graphics.DrawnShape, 
                   window: WindowBase, stroke: bool = True, noskip: bool = False, 
                   *args, **kwargs) -> None:
        if isinstance(drawn_shape.shape, charmy_stuff.styles.shape.AnyShape):
            ShapeBase.draw_any_shape(drawn_shape, window, stroke, noskip, *args, **kwargs)
        elif isinstance(drawn_shape.shape, charmy_stuff.styles.shape.ShapeGroup):
            ShapeBase.draw_shape_group(drawn_shape, window, stroke, noskip, *args, **kwargs)
        else:
            template.not_implemented_func(Backend.friendly_name, 
                    f"Drawing a shape that is not a subclass of AnyShape")


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
                                  texture: charmy_stuff.styles.texture.Texture, 
                                  noskip: bool = False
                                  ) -> bool:
        """Set texture of a Cairo context, and returns if following drawing still needs to be done. 
        
        function only available in Genesis backend.

        :param context: The Cairo context to set texture
        :param texture: The texture to set
        :return bool: If the object needs to be drawn
        """
        cmtx = charmy_stuff.styles.texture # CMTX = abbr. CharMy TeXture
        if isinstance(texture, cmtx.Transparent):
            context.set_source_rgba(0, 0, 0, 0)
            return noskip
        if isinstance(texture, cmtx.Color):
            context.set_source_rgba(*[v / 255 for v in texture])
        else:
            template.not_implemented_func(
                Backend.friendly_name, f"Drawing texture type {texture.__class__.__name__}"
                )
        return True


class TextSupportState(template.TextSupportState):
    """Flags support state of text features of this backend."""
    direct_render           : bool = True
    stock_filter            : bool = False
    custom_strikethrough    : bool = True
    custom_underline        : bool = True
    any_fontweight          : bool = False
    fontweights             : list[int] = [
                                charmy_stuff.styles.text_style.WEIGHT.REGULAR, 
                                charmy_stuff.styles.text_style.WEIGHT.BOLD, 
                                ]
    prefer_conversion       : bool = True

# region Texts
class TextBase(template.TextBase):
    """Text-related APIs in Genesis backend."""
    supports: TextSupportState = TextSupportState()

    @staticmethod
    def draw_text(drawn_text: charmy_stuff.graphics.DrawnText, window: WindowBase):
        """To draw text on GUI or canvas."""
        ## Set Cairo font
        TextBase.cairo_set_font(drawn_text, window)
        # Text size
        text_size = TextBase.get_text_bound(drawn_text, window.cairo_context) [1]
        drawn_text._backend_reported_boundary = (drawn_text.offset, text_size)
        if DEBUG_FLAGS.DRAW_CAIRO_STOCK_TEXT_BOUND:
            text_bound = charmy_stuff.graphics.DrawnShape(
                charmy_stuff.styles.shape.Rect(drawn_text.offset, text_size), 
                (255, 0, 0, 50), 
                2, (255, 0, 0)
                )
            window.drawing_list.insert(window.drawing_list.index(drawn_text) + 1, text_bound)
        ## Draw text itself
        window.cairo_context.move_to(drawn_text.offset[0], drawn_text.offset[1] + text_size[1])
        # 👆 Cairo use bottom-left as anchor, while Charmy uses top-left, so needs conversion on y
        window.cairo_context.show_text(drawn_text.text)
        ## Underline & strikethrough
        offset = int(drawn_text.style.size // 5)
        if drawn_text.style.underlined != False:
            # Underline
            underline: charmy_stuff.graphics.DrawnLine
            if isinstance(drawn_text.style.underlined, bool):
                underline = charmy_stuff.graphics.DrawnLine(charmy_stuff.styles.shape.Line([
                    (drawn_text.offset[0] - 2, drawn_text.offset[1] + text_size[1] + offset), 
                    (drawn_text.offset[0] + text_size[0] + 2, 
                     drawn_text.offset[1] + text_size[1] + offset)
                    ]), 
                    drawn_text.texture, max(1, int(drawn_text.style.size) // 15))
            else:
                underline = drawn_text.style.underlined
            # Insert the underline right after the text
            window.drawing_list.insert(window.drawing_list.index(drawn_text) + 1, underline)
        if drawn_text.style.strikethrough != False:
            # Strikethrough
            strikethrough: charmy_stuff.graphics.DrawnLine
            if isinstance(drawn_text.style.strikethrough, bool):
                strikethrough = charmy_stuff.graphics.DrawnLine(charmy_stuff.styles.shape.Line([
                    (drawn_text.offset[0] - 2, drawn_text.offset[1] + text_size[1] // 2 + offset), 
                    (drawn_text.offset[0] + text_size[0] + 2, 
                     drawn_text.offset[1] + text_size[1]//2 + offset)
                    ]), 
                    drawn_text.texture, max(1, int(drawn_text.style.size) // 15))
            else:
                strikethrough = drawn_text.style.strikethrough
            # Insert the underline right after the text
            window.drawing_list.insert(window.drawing_list.index(drawn_text) + 1, strikethrough)

    @staticmethod
    def cairo_set_font(drawn_text: charmy_stuff.graphics.DrawnText, window: WindowBase):
        """To draw text on GUI or canvas."""
        ## Set Cairo font
        if not TextureBase.cairo_set_context_texture(window.cairo_context, drawn_text.texture):
            # Set text texture and skip drawing if not necessary to draw
            return
        window.cairo_context.select_font_face(
            drawn_text.style.font, 
            cairo.FontSlant.NORMAL if not drawn_text.style.italic else cairo.FontSlant.ITALIC, 
            cairo.FontWeight.BOLD if drawn_text.style.weight >= \
                charmy_stuff.styles.text_style.WEIGHT.BOLD else cairo.FontWeight.NORMAL
            )
        window.cairo_context.set_font_size(drawn_text.style.size)

    @staticmethod
    def get_text_bound(drawn_text: charmy_stuff.graphics.DrawnText, 
                      ctx: typing.Optional[cairo.Context] = None):
        ## Calc text size
        if ctx is None:
            # If not given a context, then make one
            surface: cairo.ImageSurface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, 10, 10)
            ctx = cairo.Context(surface)
            make_ctx = True
        else:
            make_ctx = False
        extents = ctx.text_extents(drawn_text.text)
        text_size = (int(round(extents.width, 0)), int(round(extents.height, 0)))
        if make_ctx:
            # If made context before, destroy it immediately
            del surface
            del ctx
        return drawn_text.offset, text_size

# region: Alias WhateverBase classes

Backend.WindowBase = WindowBase
Backend.LineBase = LineBase
Backend.ShapeBase = ShapeBase
Backend.TextureBase = TextureBase
Backend.TextBase = TextBase

# endregion