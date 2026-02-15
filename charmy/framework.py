import importlib.util
import sys
import typing

from .const import DrawingFrame, UIFrame
from .event import Event
from .pos import Pos
from .size import Size


# region Window
class WindowFramework:
    """The base class of WindowFramework."""

    def init(self, **kwargs) -> None:
        """Init the window framework

        Args:
            **kwargs: Keyword arguments.

        Returns:
            None
        """
        ...

    def create(self, size, title, **kwargs) -> dict[str, typing.Any]:
        """Create a window

        Args:
            size: Size of the window
            title: Title of the window
            **kwargs: Keyword arguments. GLFW:
                samples: Number of samples for multisampling. Default is 4.
                error_callback: Error callback function. Default is None.

        Returns:
            dict[str, typing.Any]: A dictionary containing the created window including 'window' and 'pos'
        """
        ...

    def create_event_bounds(self, the_window, window_class, **kwargs):
        """Create event bounds for the window

        Args:
            the_window: The window to create event bounds for
            window_class: The window class to create event bounds for
            **kwargs: Keyword arguments.

        Returns:
            None
        """
        ...

    def destroy(self, the_window) -> None:
        """Destroy the window

        Args:
            the_window: The window to destroy with

        Returns:
            None
        """

    def set_size(self, the_window, size: Size) -> None:
        """Set the size of the window

        Args:
            the_window: The window to set size for
            size: Size to set

        Returns:
            None
        """
        ...

    def set_pos(self, the_window, pos: Pos | tuple[int, int]) -> None:
        """Set the position of the window

        Args:
            the_window: The window to set position for
            pos: Position to set

        Returns:
            None
        """
        ...

    def set_title(self, the_window, title: str) -> None:
        """Set the title of the window

        Args:
            the_window: The window to set title for
            title: Title to set (Default value = 'Charmy GUI')

        Returns:
            None
        """
        ...

    def make_context_current(self, the_window, **kwargs) -> dict[str, typing.Any]:
        """Make the context current for the window

        Args:
            the_window: The window to make context current for

        Returns:
            None
        """
        ...

    def swap_buffers(self, the_window) -> None:
        """Swap the buffers of the window

        Args:
            the_window: The window to swap buffers for

        Returns:
            None
        """
        ...


window_framework_map: dict[UIFrame, WindowFramework] = {}


class GLFW(WindowFramework):
    def __init__(self):
        self.glfw = importlib.import_module("glfw")

    def init(self, **kwargs) -> None:
        if not self.glfw.init():
            raise self.glfw.GLFWError("Init failed")

        self.glfw.window_hint(self.glfw.STENCIL_BITS, 8)
        self.glfw.window_hint(self.glfw.TRANSPARENT_FRAMEBUFFER, True)
        self.glfw.window_hint(self.glfw.WIN32_KEYBOARD_MENU, True)
        self.glfw.window_hint(self.glfw.COCOA_RETINA_FRAMEBUFFER, True)
        self.glfw.window_hint(self.glfw.SAMPLES, kwargs.get("samples", 4))
        if kwargs.get("error_callback", None):
            self.glfw.set_error_callback(kwargs["error_callback"])
        ...

    def create(self, size, title, **kwargs) -> dict[str, typing.Any]:
        self.glfw.window_hint(
            self.glfw.CONTEXT_RELEASE_BEHAVIOR, self.glfw.RELEASE_BEHAVIOR_NONE
        )  # mystery optimize
        self.glfw.window_hint(self.glfw.STENCIL_BITS, 8)
        self.glfw.window_hint(self.glfw.COCOA_RETINA_FRAMEBUFFER, self.glfw.TRUE)  # macOS
        self.glfw.window_hint(self.glfw.SCALE_TO_MONITOR, self.glfw.TRUE)  # Windows/Linux

        # see https://www.glfw.org/faq#macos
        if sys.platform.startswith("darwin"):
            self.glfw.window_hint(self.glfw.CONTEXT_VERSION_MAJOR, 3)
            self.glfw.window_hint(self.glfw.CONTEXT_VERSION_MINOR, 2)
            self.glfw.window_hint(self.glfw.OPENGL_FORWARD_COMPAT, True)
            self.glfw.window_hint(self.glfw.OPENGL_PROFILE, self.glfw.OPENGL_CORE_PROFILE)
        else:
            if kwargs.get("fha", True):
                self.glfw.window_hint(self.glfw.OPENGL_FORWARD_COMPAT, True)
                self.glfw.window_hint(self.glfw.CLIENT_API, self.glfw.OPENGL_API)
                self.glfw.window_hint(self.glfw.CONTEXT_VERSION_MAJOR, 3)
                self.glfw.window_hint(self.glfw.CONTEXT_VERSION_MINOR, 3)
                self.glfw.window_hint(self.glfw.OPENGL_PROFILE, self.glfw.OPENGL_CORE_PROFILE)

        window = self.glfw.create_window(size["width"], size["height"], title, None, None)
        if not window:
            raise RuntimeError("Can't create window")

        return {"pos": self.glfw.get_window_pos(window), "window": window}

    def create_event_bounds(self, the_window, window_class, **kwargs) -> None:
        self.glfw.set_window_size_callback(
            the_window,
            lambda w, width, height: window_class.trigger(
                Event(window_class, "resize", width=width, height=height)
            ),
        )
        self.glfw.set_window_pos_callback(
            the_window,
            lambda w, root_x, root_y: window_class.trigger(
                Event(window_class, "move", x_root=root_x, y_root=root_y)
            ),
        )

    def destroy(self, the_window) -> None:
        self.glfw.destroy_window(the_window)

    def set_size(self, the_window, size: Size | tuple[int, int]) -> None:
        if isinstance(size, tuple):
            self.glfw.set_window_size(the_window, size[0], size[1])
        else:
            self.glfw.set_window_size(the_window, size["width"], size["height"])

    def set_pos(self, the_window, pos: Pos | tuple[int, int]) -> None:
        if isinstance(pos, tuple):
            self.glfw.set_window_pos(the_window, pos[0], pos[1])
        else:
            self.glfw.set_window_pos(the_window, pos["x"], pos["y"])

    def set_title(self, the_window, title: str) -> None:
        self.glfw.set_title(the_window, title)

    def make_context_current(self, the_window, **kwargs) -> None:
        self.glfw.make_context_current(the_window)

    def swap_buffers(self, the_window) -> None:
        self.glfw.swap_buffers(the_window)

    def can_be_closed(self, the_window) -> bool:
        return self.glfw.window_should_close(the_window)


if importlib.util.find_spec("glfw") is not None:
    window_framework_map[UIFrame.GLFW] = GLFW  # NOQA
# endregion


# region Drawing
class DrawingFramework:
    """The base class of DrawingFramework."""


drawing_framework_map: dict[DrawingFrame, DrawingFramework] = {}
# endregion
