from __future__ import annotations as _
import typing

# from dataclasses import dataclass
import warnings

if typing.TYPE_CHECKING:
    from ..styles import shape as cm_shape
    from ..styles import texture as cm_texture
    from ..widgets import window as cm_window
    from .. import draw as cm_draw
    from .. import draw as cm_draw


# ChatGPT says that my framework is good.   —— rgzz666 @2026/04/15


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

    def __init__(self):
        """Initialize a backend"""
        return
    
    def backend_init(self) -> None:
        return None
    
    def draw_line(self, line: LineBase, window: WindowBase):
        not_implemented_func(Backend.friendly_name)
    
    def draw_shape(self, shape: ShapeBase, window: WindowBase, pos: tuple[int, int] | None) -> None:
        not_implemented_func(Backend.friendly_name)


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
    resize                  : bool = False
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

    def __init__(self, backend: Backend) -> None:
        """Initializes the dummy window.
        
        :param backend: The backend that this window uses
        """
        super().__init__(backend)

        self.backend: Backend = backend
        self.title: str = "Charmy Dummy Window"
        self.icon: bytearray | None = None
        self.size: tuple[int, int] = (0, 0)
        self.scale_mode: str = "default_scale"
        self.background: str | tuple[int, int, int] | typing.Any = "#ffffff"
        self.alpha: float = 1
        self.state: str = "normal"
        self.fullscreen: bool = False
        self.customize_titlebar = False

        self.drawing_list: list[cm_draw.DrawnLine | cm_draw.DrawnShape] = []

        # And no need to perform any action to a dummy window

    def show(self) -> typing.Self:
        """Shows the window, does nothing on dummy window."""
        return self
    
    def hide(self) -> typing.Self:
        """Hides the window, does nothing on a dummy window."""
        return self
    
    def update(self) -> None:
        """Updates the window, although not supported in nobackend and will throw an error"""
        raise NotImplementedError(
            f"{Backend.friendly_name} is not a valid backend to make Charmy work. "
            "You must install another backend that supports your system GUI.\n"
            "Hint: If you already specified another backend, this means that backend is invalid."
        )
    
    def draw_frame(self, drawing_list: list[cm_draw.DrawnLine | cm_draw.DrawnShape]) -> None:
        """Draw a frameon window, does nothing on a dummy."""
        not_implemented_func(Backend.friendly_name)
    
    def set_title(self, new: str) -> typing.Self:
        """Set title to window, does nothing on dummy"""
        not_implemented_func(Backend.friendly_name)
        return self


class LineSupportState(SupportState):
    """Flags support state of line types of this backend."""
    line                : bool = False
    polyline            : bool = False
    circle_arc          : bool = False
    ellipse_arc         : bool = False
    quadratic_bezier    : bool = False
    cubic_bezier        : bool = False

class LineBase(WhateverBase):
    """Set of lines-related APIs"""

    supports: LineSupportState = LineSupportState()

    def __init__(self, *args, **kwargs):
        """Not supposed to be instantiated."""
        raise RuntimeError("LineBase is used to hold APIs, but not supposed to be instantiated.")

    @staticmethod
    def draw_line(line: cm_shape.LinePath, window: cm_window.Window, texture: cm_texture.Texture):
        """To draw a line on a specific window.

        Args:
            line: The line to be drawn
            window: The WindowBase to draw line
        """
        not_implemented_func(Backend.friendly_name)


class ShapeSupportState(SupportState):
    """Flags support state of shape types of this backend."""
    any_shape       : bool = False
    rect            : bool = False
    round_rect      : bool = False
    polygon         : bool = False
    oval            : bool = False
    sector          : bool = False

class ShapeBase():
    """Set of shape-related APIs"""

    supports: ShapeSupportState = ShapeSupportState()

    def __init__(self, *args, **kwargs):
        """Not supposed to be instantiated."""
        raise RuntimeError("ShapeBase is used to hold APIs, but not supposed to be instantiated.")

    @staticmethod
    def draw_shape(shape: cm_shape.AnyShape, window: WindowBase, fill: TextureBase, border: TextureBase):
        """To draw a shape on a specific window.

        :param shape: The shape to be drawn
        :param window: The WindowBase to draw shape
        :param fill: Texture to fill the shape
        :param border: Texture to fill the shape border
        """
        not_implemented_func(Backend.friendly_name)


class TextureSupportState(SupportState):
    color           : bool = False
    linear_gradient : bool = False
    radial_gradient : bool = False
    filter          : bool = False
    image           : bool = False
    func_shader     : bool = False

class TextureBase():
    def __init__(self, *args, **kwargs):
        """Not supposed to be instantiated."""
        raise RuntimeError("TextureBase is used to hold APIs, but not supposed to be instantiated.")


# region: Alias WhateverBase classes

Backend.WindowBase = WindowBase
Backend.LineBase = LineBase
Backend.ShapeBase = ShapeBase
Backend.TextureBase = TextureBase

# endregion