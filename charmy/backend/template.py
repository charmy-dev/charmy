import typing

from dataclasses import dataclass
import warnings


# ChatGPT says that my framework is good.   —— rgzz666 @2026/04/15


def placeholder_function(*args, backend_name: str = "currently used", **kwargs) -> bool:
    warnings.warn(f"This function is not implemented in backend {backend_name}.")
    return False


class Backend():
    """This is a template of Backend, does not have any actual function."""

    name: str =             "nobackend"
    friendly_name: str =    "No available backend"
    version: str =          "0.0.0"
    author: list[str] =     ["Charmy dev team"]

    def __init__(self):
        """APIs are aliased here."""
        # Make alias for WhateverBase classes
        self.WindowBase = WindowBase
        self.Shape = Shape
        self.Texture = Texture
    
    def backend_init(self) -> None:
        return None
    
    def draw_shape(self, shape: Shape, window: WindowBase, pos: tuple[int, int] | None) -> None:
        placeholder_function(Backend.friendly_name)


@dataclass
class SupportState():
    """To flag which features this backend supports."""

    def __contains__(self, item):
        return item in self.__dict__

    pass


@dataclass
class WindowSupportState(SupportState):
    """Represents support states of windows held by this backend."""
    set_title              : bool = False
    set_icon               : bool = False
    resize                 : bool = False
    set_scale_mode         : bool = False
    set_background         : bool = False
    translucent            : bool = False
    set_state              : bool = False
    fullscreen             : bool = False
    customize_titlebar     : bool = False

class WindowBase():
    """Base of the windows, abstracts window-level operations from the base UI lib."""
    
    def __init__(self):
        """Initializes the dummy window"""
        self.supports: WindowSupportState = WindowSupportState()

        self.title: str = "Charmy Dummy Window"
        self.icon: bytearray | None = None
        self.size: tuple[int, int] = (0, 0)
        self.scale_mode: str = "default_scale"
        self.background: str | tuple[int, int, int] | typing.Any = "#ffffff"
        self.alpha: float = 1
        self.state: str = "normal"
        self.fullscreen: bool = False
        self.customize_titlebar = False

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
            "nobackend is not a valid backend to make Charmy works. "
            "You must install another backend that supports your system GUI.\n"
            "Hint: If you already specified another backend, this means that backend is invalid."
        )
    
    def draw_frame(self) -> None:
        """Draw a frameon window, does nothing on a dummy."""
        placeholder_function(Backend.friendly_name)
    
    def set_title(self, new: str) -> typing.Self:
        """Set title to window, does nothing on dummy"""
        placeholder_function(Backend.friendly_name)
        return self


@dataclass
class ShapeSupportState(SupportState):
    """Represents support states of shapes of this backend."""
    polygon         : bool = False
    round_rect      : bool = False
    oval            : bool = False
    beizer_curve    : bool = False
    svg             : bool = False
    func_shape      : bool = False

class Shape():
    """Represent a shape in backend layer that can be drawn on window."""

    def __init__(self, 
                 shape_type: str, 
                 shape_params: dict[str, typing.Any], 
                 pos: tuple[int, int] = (0, 0), 
                 texture: Texture | str | tuple[int, int, int] = "#00ff00", 
                 ):
        self.supports: ShapeSupportState = ShapeSupportState()

        self.type: str = shape_type
        self.shape_params: dict[str, typing.Any] = shape_params
        self.pos: tuple[int, int] = pos
        self.texture: Texture | str | tuple[int, int, int] = texture


@dataclass
class TextureSupportState(SupportState):
    color           : bool = False
    filter          : bool = False
    image           : bool = False
    func_shader     : bool = False

class Texture():
    pass