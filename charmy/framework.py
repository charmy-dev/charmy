import importlib.util
import sys
import typing

from .const import Backends
from .event import Event
from .pos import Pos
from .size import Size

from abc import ABC, abstractmethod


# region Window
class WindowFramework(ABC):
    """The base class of WindowFramework."""

    @abstractmethod
    def init(self, **kwargs) -> None:
        """Init the window framework

        Args:
            **kwargs: Keyword arguments.

        Returns:
            None
        """
        ...

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def destroy(self, the_window) -> None:
        """Destroy the window

        Args:
            the_window: The window to destroy with

        Returns:
            None
        """
        ...

    @abstractmethod
    def set_size(self, the_window, size: Size) -> None:
        """Set the size of the window

        Args:
            the_window: The window to set size for
            size: Size to set

        Returns:
            None
        """
        ...

    @abstractmethod
    def set_pos(self, the_window, pos: Pos | tuple[int, int]) -> None:
        """Set the position of the window

        Args:
            the_window: The window to set position for
            pos: Position to set

        Returns:
            None
        """
        ...

    @abstractmethod
    def set_title(self, the_window, title: str) -> None:
        """Set the title of the window

        Args:
            the_window: The window to set title for
            title: Title to set (Default value = 'Charmy GUI')

        Returns:
            None
        """
        ...

    @abstractmethod
    def get_mouse_pos(self, the_window) -> tuple[int, int]:
        """Get the mouse position of the window

        Args:
            the_window: The window to get mouse position for

        Returns:
            tuple[int, int]: The mouse position of the window
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

    @abstractmethod
    def swap_buffers(self, the_window) -> None:
        """Swap the buffers of the window

        Args:
            the_window: The window to swap buffers for

        Returns:
            None
        """
        ...


window_framework_map: dict[Backends, WindowFramework] = {}


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

        def _enter(w, entered: int):
            if entered:
                event_type = "mouse_enter"
            else:
                event_type = "mouse_leave"
            window_class.trigger(Event(window_class, event_type, the_window=w))

        self.glfw.set_cursor_enter_callback(
            the_window,
            _enter,
        )
        self.glfw.set_cursor_pos_callback(
            the_window,
            lambda w, x, y: window_class.trigger(
                Event(window_class, "mouse_move", x=x, canvas_x=x, y=y, canvas_y=y)
            ),
        )

        def _mouse(w, button, action, mods):  # NOQA
            if action == self.glfw.PRESS:
                event_type = "mouse_press"
            elif action == self.glfw.RELEASE:
                event_type = "mouse_release"
            else:
                return
            button_map = {
                self.glfw.MOUSE_BUTTON_LEFT: "left",
                self.glfw.MOUSE_BUTTON_RIGHT: "right",
                self.glfw.MOUSE_BUTTON_MIDDLE: "middle",
            }
            mods_map = {
                self.glfw.MOD_SHIFT: "shift",
                self.glfw.MOD_CONTROL: "control",
                self.glfw.MOD_ALT: "alt",
                self.glfw.MOD_SUPER: "super",
                self.glfw.MOD_NUM_LOCK: "num_lock",
                self.glfw.MOD_CAPS_LOCK: "caps_lock",
            }
            window_class.trigger(
                Event(
                    window_class,
                    event_type,
                    button=button_map.get(button, None),
                    mods=mods_map.get(mods, None),
                )
            )

        self.glfw.set_mouse_button_callback(the_window, _mouse)

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

    def get_mouse_pos(self, the_window) -> tuple[int, int]:
        return self.glfw.get_cursor_pos(the_window)

    def make_context_current(self, the_window, **kwargs) -> None:
        self.glfw.make_context_current(the_window)

    def swap_buffers(self, the_window) -> None:
        self.glfw.swap_buffers(the_window)

    def can_be_closed(self, the_window) -> bool:
        return self.glfw.window_should_close(the_window)


if importlib.util.find_spec("glfw") is not None:
    window_framework_map[Backends.GLFW] = GLFW  # NOQA
# endregion

from .rect import Rect


# region Drawing
class DrawingFramework:
    """The base class of DrawingFramework."""

    def draw_rect(self, canvas, rect: Rect, radius: int = 0, bg=None, bd=None):
        """Draw a rectangle

        Args:
            canvas (Canvas): The canvas to draw
            rect (Rect): The rect area to draw
            radius (int, optional): The radius of the rectangle. Defaults to 0.
            bg (charmy.styles.color.Color, optional): The background color of the rectangle. Defaults to None.
            bd (charmy.styles.color.Color, optional): The border color of the rectangle. Defaults to None.
        """
        ...


drawing_framework_map: dict[Backends, DrawingFramework] = {}


class SKIA:
    def __init__(self):
        self.skia = importlib.import_module("skia")

    def draw_rect(self, canvas, rect: Rect, radius: int | float = 8, bg=None, bd=None):  # noqa
        # from skia import RRect, Rect, Canvas, Paint
        # Paint()
        # canvas: Canvas

        if bg is None:
            bg = {}
        canvas.drawRoundRect(
            rect=self.skia.Rect.MakeXYWH(rect["x"], rect["y"], rect["width"], rect["height"]),
            rx=radius,
            ry=radius,
            paint=self.skia.Paint(
                Color=bg.get("color_object", self.skia.ColorBLUE),
                Style=self.skia.Paint.kFill_Style,
            ),
        )


if importlib.util.find_spec("skia") is not None:
    drawing_framework_map[Backends.SKIA] = SKIA  # NOQA

# endregion
