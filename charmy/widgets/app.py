import typing
import importlib
import warnings

from ..const import BackendFrame, DrawingFrame, UIFrame
from ..event import WorkingThread
from ..object import CharmyObject


class App(CharmyObject):
    """The base of CApp Class.

    Args:
        ui.framework: What UI Framework will be used.
        ui.is_vsync: Is vsync enabled.
        ui.samples: UI Samples.
    """

    def __init__(
        self,
        ui: UIFrame = UIFrame.GLFW,
        drawing: DrawingFrame = DrawingFrame.SKIA,
        backend: BackendFrame = BackendFrame.OPENGL,
        vsync: bool = True,
        samples: int = 4,
    ):
        super().__init__()

        if self.instance_count >= 1:
            warnings.warn("There should be only one instance of CApp.")

        self.new("event.thread", WorkingThread())

        self.new("ui.framework", ui)
        self["ui.framework"]: UIFrame
        self.new("ui.is_vsync", vsync)
        self.new("ui.samples", samples)

        match self["ui.framework"]:
            case UIFrame.GLFW:
                self.glfw = importlib.import_module("glfw")
            case UIFrame.SDL:
                self.sdl3 = importlib.import_module("sdl3")
            case _:
                raise ValueError(f"Unknown UI Framework: {self['ui.framework']}")

        self.new("drawing.framework", drawing)

        match self["drawing.framework"]:
            case DrawingFrame.SKIA:
                self.skia = importlib.import_module("skia")
            case _:
                raise ValueError(f"Unknown Drawing Framework: {self['drawing.framework']}")

        self.new("backend.framework", backend)

        match self["backend.framework"]:
            case BackendFrame.OPENGL:
                self.opengl = importlib.import_module("OpenGL")
                self.opengl_GL = importlib.import_module("OpenGL.GL")
            case _:
                raise ValueError(f"Unknown Backend Framework: {self['backend.framework']}")

        self.windows = []
        self.is_alive: bool = False

        self._init_ui_framework()

    def _init_ui_framework(self):
        """According to attribute `ui.framework` to init ui framework"""
        match self.get("ui.framework"):
            case UIFrame.GLFW:
                if not self.glfw.init():
                    raise self.glfw.GLFWError("Init failed")

                self.glfw.window_hint(self.glfw.STENCIL_BITS, 8)
                self.glfw.window_hint(self.glfw.TRANSPARENT_FRAMEBUFFER, True)
                self.glfw.window_hint(self.glfw.WIN32_KEYBOARD_MENU, True)
                self.glfw.window_hint(self.glfw.COCOA_RETINA_FRAMEBUFFER, True)
                self.glfw.window_hint(self.glfw.SAMPLES, self.get("ui.samples"))
                self.glfw.set_error_callback(self.error)

    def update(self):
        """Update the CWindows' UI and events"""

        input_mode: bool = True

        # poll_events()
        windows = self.windows

        for window in windows:
            if window.is_visible and window.is_alive:
                window.update()
                if self.glfw.get_current_context():
                    self.glfw.swap_interval(1 if self.get("ui.is_vsync") else 0)  # 是否启用垂直同步

        if input_mode:
            self.glfw.poll_events()
        else:
            # if self._check_delay_events()
            self.glfw.wait_events()

    def run(self):
        """Run the application.

        This method will start the application event loop. It will continue running
        as long as the `is_alive` attribute is set to `True`.

        If no windows are added to the application, a warning will be issued.
        """
        if not self.windows:
            warnings.warn(
                "At least one window is required to run application!",
            )

        self.is_alive: bool = True
        self["event.thread"].start()

        while self.is_alive:
            try:
                windows = self.windows
                if not windows:
                    self.quit()
                    break
                for window in windows:
                    if window.can_be_close():
                        window.destroy()
                self.update()
            except Exception as e:
                self.is_alive = False
                raise e

        self.cleanup()

    def add_window(self, window):
        """Add a window to the application.

        Args:
            window (CWindow): The window to be added.
        """
        self.windows.append(window)

    def destroy_window(self, window):
        """Destroy a window.

        Args:
            window (CWindow): The window to be destroyed.
        """
        windows = self.windows
        if window in windows:
            windows.remove(window)

    def cleanup(self) -> None:
        """Clean up resources."""
        match self.get("ui.framework"):
            case UIFrame.GLFW:
                for window in self.windows:
                    self.glfw.destroy_window(window.the_window)
                self.glfw.terminate()
        self.quit()

    def quit(self) -> None:
        """Quit application."""
        self.is_alive = False
        self["event.thread"].is_alive = False

    @staticmethod
    def error(error_code: typing.Any, description: bytes):
        """
        GLFW Error Callback

        :param error_code: GLFW error code
        :param description: Error description
        :return: None
        """
        raise f"GLFW Error {error_code}: {description.decode()}"
