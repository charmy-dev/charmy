import importlib
import typing
import warnings
from os import environ

from ..const import MANAGER_ID, Backends
from ..event import WorkingThread
from ..framework import Framework
from ..object import CharmyObject


class CharmyManager(CharmyObject):
    """The manager of the charmy windows.

    Args:
        is_vsync: Is vsync enabled.
        samples: UI Samples.
    """

    def __init__(
        self,
        vsync: bool = True,
        samples: int = 4,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if self.instance_count >= 1:
            warnings.warn("There should be only one instance of CApp.")

        self.new("event.thread", WorkingThread())

        self.new("framework", Framework)
        self.new("ui.framework", self["framework"].ui)
        self.new("drawing.framework", self["framework"].drawing)
        self.new("backend.framework", self["framework"].backend)

        self.new("ui.is_vsync", vsync)
        self.new("ui.samples", samples)

        self.windows = []
        self.is_alive: bool = False  # Is the manager running

        self._init_ui_framework()

    def _init_ui_framework(self):
        """According to attribute `ui.framework` to init ui framework"""
        self["framework"].ui.init(error_callback=self.error, samples=self.get("ui.samples"))

    def update(self):
        """Update the Windows' UI and events"""

        input_mode: bool = True

        self.glfw = self["framework"].ui.glfw
        self.glfw.wait_events()
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

    def mainloop(self):
        """Start mainloop.

        This method will start the manager event loop. It will continue running
        as long as the `is_alive` attribute is set to `True`.

        If no windows are added to the manager, a warning will be issued.
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

    launch = run = mainloop

    def add_window(self, window):
        """Add a window to the manager.

        Args:
            window (charmy.widgets.WindowBase): The window to be added.
        """
        self.windows.append(window)

    def destroy_window(self, window):
        """Destroy a window from the manager.

        Args:
            window (charmy.widgets.WindowBase): The window to be destroyed.
        """
        windows = self.windows
        if window in windows:
            windows.remove(window)

    def cleanup(self) -> None:
        """Clean up resources."""
        match self["framework"].ui_name:
            case "GLFW":
                for window in self.windows:
                    self.glfw.destroy_window(window.the_window)
                self.glfw.terminate()
        self.quit()

    def quit(self) -> None:
        """Quit the mainloop."""
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


# Auto create Manager Object

manager: CharmyManager = CharmyManager(id_=MANAGER_ID)


def mainloop() -> None:
    """Start main loop."""
    try:
        manager.run()
    except Exception as e:
        raise e


def cquit():  # NOQA
    """Quit the main loop"""
    manager.quit()
