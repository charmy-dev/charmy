"""Template backend, identified as `nobackend` in Charmy runtime.

This is a template of all backends, providing basic fallback for functions that might be used but 
not implemented by actual backends. This template backend shall not be used in actual development.

This backend is identified as `nobackend` in Charmy, and will throw an error when trying to create 
window with it.
"""

from __future__ import annotations as _
import typing

import warnings

from . import utils as charmy_stuff

if typing.TYPE_CHECKING:
    from charmy.widgets import window

__all__ = ["Backend", "not_implemented_func"]


# ChatGPT says that my framework is good.   —— rgzz666 @2026/04/15


# region Placeholder function

def not_implemented_func(
        backend_name: str = "currently used", 
        operation_desc: str = "This operation", 
        **kwargs) -> bool:
    """To throw a warning to tell that a specific function is not implemented by the backend.

    The parameters only affects the warning message.

    :param backend_name: Friendly name of the backend
    :param operation_desc: Description of the operation
    """
    warnings.warn(f"{operation_desc} is not implemented in backend {backend_name}.", stacklevel=2)
    return False


# region Backend class

class Backend():
    """This is a template of Backend, does not have any actual function."""

    name: str =             "nobackend"
    friendly_name: str =    "No available backend"
    version: str =          "0.0.0"
    author: list[str] =     ["Charmy dev team"]

    WindowBase: type[WindowBase]
    LineBase: type[LineBase]
    ShapeBase: type[ShapeBase]
    TextureBase: type[TextureBase]
    TextBase: type[TextBase]

    def __init__(self):
        """Initialize a backend"""
        return
    
    def backend_init(self) -> None:
        return None


# region Base classes

class WhateverBase():
    """Base class of all... WhateverBase classes?"""

    supports: SupportState
    Backend: type[Backend] = Backend

    def __init__(self, backend):
        # Check if using wrong backend
        if not isinstance(backend, self.Backend):
            raise TypeError(
                "Wrong backend instance specified for WindowBase. "
                f"Should be [{self.Backend.friendly_name}] but got [{backend.friendly_name}]. "
                )


class SupportState():
    """To flag which features this backend supports."""

    def __contains__(self, item: str) -> bool:
        if hasattr(self, item):
            return getattr(self, item)
        else:
            return False

    pass


# region Window-relating

class WindowBackdropSupportState(SupportState):
    """Represents support states of backdrop effects of windows held by this backend.

    Notes
    -----
    - `any_filter` basically means that Charmy will be freely able to process the pixels behind 
      the window and hence can implement any kind of filter effect on window's backdrop.
    - Charmy may use a virtual background layer for some texture-type backdrop effects if they 
      are not supported by the backend. [PLANNED]
    """
    color                   : bool = False
    gradient                : bool = False
    image                   : bool = False
    # any_texture             : bool = False
    transparent             : bool = False
    alpha                   : bool = False
    blur                    : bool = False
    transformation          : bool = False
    any_filter              : bool = False
    # Notes:
    # - any_texture may be used in the future and maybe not, so I just commented it here.
    #   Actually I cannot think of any other kinds of textures, but, who knows?
    # - any_filter basically means that Charmy will be freely able to process the pixels behind the 
    #   window and hence can implement any kind of filter effect on window's backdrop.
    # - Charmy may use a virtual background layer for some texture-type backdrop effects if they 
    #   are not supported by the backend

class WindowSupportState(SupportState):
    """Represents support states of windows held by this backend."""
    set_title               : bool = False
    set_icon                : bool = False
    set_pos                 : bool = False
    set_size                : bool = False
    set_scale_mode          : bool = False
    set_background          : bool = False
    translucent             : bool = False
    backdrop                : WindowBackdropSupportState = WindowBackdropSupportState()
    set_state               : bool = False
    fullscreen              : bool = False
    customize_titlebar      : bool = False

class WindowBase(WhateverBase):
    """Base of the windows, abstracts window-level operations from the base UI lib."""

    supports: WindowSupportState = WindowSupportState()

    def __init__(self, backend: Backend, charmy_window: window.WindowEntity) -> None:
        """Initializes the dummy window.
        
        :param backend: The backend that this window uses
        """
        super().__init__(backend)

        self.title: str = "Charmy Dummy Window"
        self.icon: bytearray | None = None
        self.pos: charmy_stuff.styles.shape.Size = (0, 0)
        self.size: charmy_stuff.styles.shape.Size = (0, 0)
        self.scale_mode: str = "default_scale"
        self.background: charmy_stuff.styles.texture.Texture | charmy_stuff.styles.texture.TextureLike = \
                        (150, 150, 150)
        self.alpha: float = 1
        self.state: str = "normal"
        self.fullscreen: bool = False
        self.customize_titlebar = False

        self.charmy_window: window.WindowEntity = charmy_window

        # And no need to perform any action to a dummy window

    def show(self) -> typing.Self:
        """Shows the window, does nothing on dummy window."""
        not_implemented_func(operation_desc="Showing window")
        return self
    
    def hide(self) -> typing.Self:
        """Hides the window, does nothing on a dummy window."""
        not_implemented_func(operation_desc="Hiding window")
        return self

    def draw_background(self) -> typing.Self:
        """Draw the background of the window.

        This is a fallback of such function, draws a rect that fills the window.

        :return self: The WindowBase itself
        """
        # not_implemented_func(operation_desc="Drawing window background")
        self.Backend.ShapeBase.draw_shape(
            charmy_stuff.graphics.DrawnShape(
                charmy_stuff.styles.shape.Rect((0, 0), self.size), 
                self.background
                ), 
            self
            )
        return self

    def update(self, redraw: bool | charmy_stuff.styles.shape.ShapeRange = True) -> typing.Self:
        """Updates the window, although not supported in nobackend and will throw an error"""
        raise NotImplementedError(
            f"{self.Backend.friendly_name} is not a valid backend to make Charmy work. "
            "You must install another backend that supports your system GUI.\n"
        )

    def draw_frame(self, drawing_list: list[charmy_stuff.graphics.DrawnObject]) -> typing.Self:
        """Draw a frame for the window.
        
        :param drawing_list: The list of the objects to draw
        """
        self.draw_background()
        for drawing_obj in drawing_list:
            if isinstance(drawing_obj, charmy_stuff.graphics.DrawnLine):
                self.Backend.LineBase.draw_line(drawing_obj, self)
            elif isinstance(drawing_obj, charmy_stuff.graphics.DrawnShape):
                self.Backend.ShapeBase.draw_shape(drawing_obj, self)
            elif isinstance(drawing_obj, charmy_stuff.graphics.DrawnText):
                self.Backend.TextBase.draw_text(drawing_obj, self)
            else:
                not_implemented_func(
                    f"most backends (including current {self.Backend.friendly_name})", 
                    f"Drawing object type {drawing_obj.__class__.__name__}"
                    )
        return self

    def clear_screen(self) -> typing.Self:
        """To clear all content from a window"""
        self.charmy_window._drawing_list = []
        return self

    def set_pos(self, new: charmy_stuff.styles.shape.Point) -> typing.Self:
        """Set window size, does nothing on dummy."""
        not_implemented_func(operation_desc="Setting window position on screen")
        return self

    def set_size(self, new: charmy_stuff.styles.shape.Size) -> typing.Self:
        """Set window size, does nothing on dummy."""
        not_implemented_func(operation_desc="Setting window size")
        return self

    def set_title(self, new: str) -> typing.Self:
        """Set title to window, does nothing on dummy."""
        not_implemented_func(operation_desc="Setting window title")
        return self

    def set_icon(self, new: bytes) -> typing.Self:
        """Set title to window, does nothing on dummy."""
        not_implemented_func(operation_desc="Setting window title")
        return self

    def close(self) -> typing.Self:
        return self


# region Line-relating

class LineSupportState(SupportState):
    """Flags support state of line types of this backend."""
    line                : bool = False
    polyline            : bool = False
    circle_arc          : bool = False
    ellipse_arc         : bool = False
    quadratic_bezier    : bool = False
    cubic_bezier        : bool = False

class LineBase(WhateverBase):
    """Set of lines-relating APIs"""

    supports: LineSupportState = LineSupportState()

    def __init__(self, *args, **kwargs):
        """Not supposed to be instantiated."""
        raise RuntimeError("LineBase is used to hold APIs, but not supposed to be instantiated.")

    @staticmethod
    def draw_line(line: charmy_stuff.graphics.DrawnLine, window: WindowBase, *args, **kwargs):
        """To draw a line on a specific GUI or canvas.

        Args:
            line: The line to be drawn
            window: The WindowBase to draw line
        """
        not_implemented_func(operation_desc="Drawing lines")


# region Shape-relating

class ShapeSupportState(SupportState):
    """Flags support state of shape types of this backend."""
    any_shape       : bool = False
    rect            : bool = False
    round_rect      : bool = False
    polygon         : bool = False
    oval            : bool = False
    sector          : bool = False

class ShapeBase():
    """Set of shape-relating APIs"""

    supports: ShapeSupportState = ShapeSupportState()

    def __init__(self, *args, **kwargs):
        """Not supposed to be instantiated."""
        raise RuntimeError("ShapeBase is used to hold APIs, but not supposed to be instantiated.")

    @staticmethod
    def draw_shape(shape: charmy_stuff.graphics.DrawnShape, window: WindowBase, *args, **kwargs):
        """To draw a shape on a specific GUI or canvas.

        :param shape: The shape to be drawn
        :param window: The WindowBase to draw shape
        """
        not_implemented_func(operation_desc="Drawing shapes")


# region Texture-relating

class TextureSupportState(SupportState):
    """Flags support state of texture types of this backend."""
    color               : bool = False
    linear_gradient     : bool = False
    radial_gradient     : bool = False
    filter              : bool = False
    image               : bool = False
    func_shader         : bool = False

class TextureBase():
    """Set of texture-relating APIs"""

    supports: TextureSupportState = TextureSupportState()

    def __init__(self):
        """Not supposed to be instantiated."""
        raise RuntimeError("TextureBase is used to hold APIs, but not supposed to be instantiated.")


# region Text-relating

class TextSupportState(SupportState):
    """Flags support state of text features of this backend."""
    direct_render           : bool = False
    stock_filter            : bool = False
    custom_strikethrough    : bool = False
    custom_underline        : bool = False
    any_fontweight          : bool = False
    fontweight              : list[int] = []
    prefer_conversion       : bool = False

class TextBase():
    """Set of text-relating APIs."""
    supports: TextSupportState = TextSupportState()

    def __init__(self):
        """Not supported to be instantiated."""
        raise RuntimeError("TextBase is used to hold APIs, but not supposed to be instantiated.")

    @staticmethod
    def draw_text(drawn_text: charmy_stuff.graphics.DrawnText, window: WindowBase, *args, **kwargs):
        """To draw a line or paragraph of text on a specific GUI or canvas."""
        not_implemented_func(operation_desc="Drawing text")

    @staticmethod
    def get_text_bound(drawn_text: charmy_stuff.graphics.DrawnText, *args, **kwargs):
        """To get the text's boundary when it is rendered by a specific backend."""
        not_implemented_func(operation_desc="Getting text boundary.")


# region: Alias WhateverBase classes

Backend.WindowBase = WindowBase
Backend.LineBase = LineBase
Backend.ShapeBase = ShapeBase
Backend.TextureBase = TextureBase
Backend.TextBase = TextBase

# endregion