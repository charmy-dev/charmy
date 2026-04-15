import typing

from dataclasses import dataclass
import warnings


class Backend():
    """This is a template of Backend, does not have any actual function."""

    def __init__(self):
        """Here goes the backend's metadata. In nobackend, APIs are also aliased here."""
        self.name = "nobackend"
        self.friendly_name = "No available backend"
        self.version = "0.0.0"
        self.author = []

        # Make placeholders for APIs
        func = self.placeholder_function # Just for aliasing

        self.init=func                          # Initialize this backend

    def placeholder_function(self, *args, **kwargs):
        warnings.warn(f"This function is not implemented in backend {self.friendly_name}.")


@dataclass
class SupportState():
    """To flag which features this backend supports."""
    pass


@dataclass
class WindowSupportState(SupportState):
    """Represents support states of windows held by this backend."""
    set_title           : bool = False
    set_icon            : bool = False
    resize              : bool = False
    set_scale_mode      : bool = False
    set_background      : bool = False
    translucent         : bool = False
    set_state           : bool = False
    fullscreen          : bool = False
    customize_titlebar  : bool = False

class WindowBase():
    """Base of the windows, abstracts window-level operations from the base UI lib."""
    
    def __init__(self):
        self.supports: SupportState = WindowSupportState()

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
    
    def show(self):
        """Shows the window, although not supported in nobackend so will raise an error."""
        raise NotImplementedError(
            "nobackend is not a valid backend to make Charmy works. "
            "You must install another backend that supports your system GUI. "
        )