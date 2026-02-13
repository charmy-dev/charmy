import typing
import warnings

from ..const import BackendFrame, DrawingFrame, UIFrame
from ..event import CEventThread
from ..object import CObject


class CApp(CObject):
    """The base of CApp Class

    Args:
        ui.framework: What UI Framework will be used
        ui.is_vsync: Is vsync enabled
        ui.samples: UI Samples
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

        self.new("event.thread", CEventThread())
        self["event.thread"].start()

        self.new("ui.framework", ui)
        self.new("ui.is_vsync", vsync)
        self.new("ui.samples", samples)

        self.new("drawing.framework", drawing)

        self.new("backend.framework", backend)

        self.new("windows", [])
        self.new("is_alive", False)

        self._init_ui_framework()

    def _init_ui_framework(self):
        """According to attribute `ui.framework` to init ui framework"""
        match self.get("ui.framework"):
            case UIFrame.GLFW:
                import glfw

                if not glfw.init():
                    raise glfw.GLFWError("Init failed")

                glfw.window_hint(glfw.STENCIL_BITS, 8)
                glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
                glfw.window_hint(glfw.WIN32_KEYBOARD_MENU, True)
                glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, True)
                glfw.window_hint(glfw.SAMPLES, self.get("ui.samples"))
                glfw.set_error_callback(self.error)

    def update(self):
        """Update the CWindows' UI and events"""
        from glfw import get_current_context, poll_events, swap_interval, wait_events

        input_mode: bool = True

        # poll_events()
        windows = self.get("windows")

        for window in windows:
            if window["is_visible"] and window["is_alive"]:
                window.update()
                if get_current_context():
                    swap_interval(1 if self.get("ui.is_vsync") else 0)  # 是否启用垂直同步

        if input_mode:
            poll_events()
        else:
            # if self._check_delay_events()
            wait_events()

    def run(self):
        """Run the application.

        This method will start the application event loop. It will continue running
        as long as the `is_alive` attribute is set to `True`.

        If no windows are added to the application, a warning will be issued.
        """
        if not self.get("windows"):
            warnings.warn(
                "At least one window is required to run application!",
            )

        self.set("is_alive", True)

        while self.get("is_alive"):
            windows = self.get("windows")
            if not windows:
                self.quit()
                break
            for window in windows:
                if window.can_be_close():
                    window.destroy()
            self.update()

        self.cleanup()

    def destroy_window(self, window):
        """Destroy a window.

        Args:
            window (CWindow): The window to be destroyed.
        """
        windows = self.get("windows")
        if window in windows:
            windows.remove(window)

    def cleanup(self) -> None:
        """Clean up resources."""
        match self.get("ui.framework"):
            case UIFrame.GLFW:
                import glfw

                for window in self.get("windows"):
                    glfw.destroy_window(window.the_window)
                glfw.terminate()
        self.quit()

    def quit(self) -> None:
        """Quit application."""
        self.set("is_alive", False)
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
