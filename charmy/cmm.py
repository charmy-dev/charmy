from __future__ import annotations as _
import typing
import warnings

from .backend import loader as backend_loader
from .const import MANAGER_ID
from .event import WorkingThread
# from .frameworks import Frameworks
from .object import CharmyObject

if typing.TYPE_CHECKING:
    from .backend.template import Backend
    from . import window


class GLFWError(Exception):
    """GLFW Error"""

    ...


class CharmyManager(CharmyObject):
    """Charmy windows manager. Used to manage windows created with one backend."""

    def __init__(self, backend: str | Backend, id_: str | None = None, **kwargs):
        """Create a Charmy windows manager.

        Args:
            backend: The backend this manager uses
        """
        super().__init__(**kwargs)

        if isinstance(backend, str):
            self.backend: Backend = backend_loader.load_backend(backend)()
        else:
            self.backend: Backend = backend
        
        self.backend.backend_init()

        self.windows: list[window.Window] = [] # Stores all windows this CharmyManager manages
        self.is_alive = True # This var stores if the manager is still alive

    def update(self):
        for window in self.windows:
            if window.visible and window._alive:
                window.update()


# class CharmyManagerOld(CharmyObject):
#     """The manager of the charmy windows. About to be refactored.

#     Args:
#         is_vsync: Is vsync enabled.
#         samples: UI Samples.
#     """

#     def __init__(
#         self,
#         vsync: bool = True,
#         samples: int = 4,
#         **kwargs,
#     ):
#         super().__init__(**kwargs)

#         # TODO: there should be only one manager
#         # TODO: maybe user will use it in later version?
#         # if self.instance_count >= 1:
#         #    warnings.warn("There should be only one instance of CApp.")
#         # 屎山留念 ——rgzz666

#         self.event_thread = WorkingThread()

#         self.cset("frameworks", Frameworks())
#         self.cset("ui.framework", self.cget("frameworks").ui)
#         self.cset("ui.framework.name", self.cget("frameworks").ui_name)
#         self.cset("ui.is_vsync", vsync)
#         self.cset("ui.samples", samples)
#         self.cset("ui.windows", [])
#         self.cset("drawing.framework", self.cget("frameworks").drawing)
#         self.cset("drawing.framework.name", self.cget("frameworks").drawing_name)
#         self.cset("backend.framework", self.cget("frameworks").backend)
#         self.cset("backend.framework.name", self.cget("frameworks").backend_name)

#         self.is_alive: bool = False  # Is the manager running

#         self._init_ui_framework()

#     def _init_ui_framework(self):
#         """According to attribute `ui.framework` to init ui framework"""
#         self.cget("ui.framework").init(error_callback=self.error, samples=self.cget("ui.samples"))

#    def update(self):
#        """Update the Windows' UI and events"""

#        self.glfw = self.cget("ui.framework").glfw
#        self.glfw.wait_events()

#        for window in self.cget("ui.windows"):
#            if window.is_visible and window.is_alive:
#                window.update()

#        # TODO: 能不能换个地方？比如说framework.py?
#        # TODO: CharmyManager过度耦合glfw, 没有考虑其他框架
#        #       是的我来修正这个问题了！ —— 2026/04/14 rgzz666

#        windows = self.cget("ui.windows")
#        if windows:
#            first_alive_window = next((w for w in windows if w.is_visible and w.is_alive), None)
#            if first_alive_window:
#                self.glfw.make_context_current(first_alive_window.the_window)

#            self.glfw.swap_interval(1 if self.cget("ui.is_vsync") else 0)  # 是否启用垂直同步

#        # not implemented yet
#        # input_mode: bool = True

#        # if input_mode:
#        #    self.glfw.poll_events()
#        # else:
#        #    # if self._check_delay_events()
#        #    self.glfw.wait_events()

#        self.glfw.wait_events()

#     def mainloop(self):
#         """Start mainloop.

#         This method will start the manager event loop. It will continue running
#         as long as the `is_alive` attribute is set to `True`.

#         If no windows are added to the manager, a warning will be issued.
#         """
#         if not self.cget("ui.windows"):
#             warnings.warn(
#                 "At least one window is required to run manager!",
#             )

#         self.is_alive: bool = True
#         self.event_thread.start()

#         # Main loop
#         while self.is_alive:
#             try:
#                 # quit when no window in list now
#                 if not self.cget("ui.windows"):
#                     self.quit()
#                     break

#                 for window in self.cget("ui.windows"):
#                     if window.can_be_close():
#                         self.destroy_window(window)  # remove window if closed
#                         window.destroy()

#                 self.update()
#             except Exception as e:
#                 self.is_alive = False
#                 raise e

#         self.cleanup()

#     def add_window(self, window):
#         """Add a window to the manager.

#         Args:
#             window (charmy.widgets.WindowBase): The window to be added.
#         """
#         self.cget("ui.windows").append(window)

#     def destroy_window(self, window):
#         """Destroy a window from the manager.

#         Args:
#             window (charmy.widgets.WindowBase): The window to be destroyed.
#         """
#         if window in self.cget("ui.windows"):
#             self.cget("ui.windows").remove(window)

#     def cleanup(self) -> None:
#         """Clean up resources."""
#         match self.cget("ui.framework.name"):
#             case "GLFW":
#                 for window in self.cget("ui.windows"):
#                     self.glfw.destroy_window(window.the_window)
#                 self.glfw.terminate()

#         self.quit()

#     def quit(self) -> None:
#         """Quit the mainloop."""
#         self.is_alive = False
#         self.event_thread.is_alive = False

#     @staticmethod
#     def error(error_code: typing.Any, description: bytes):
#         """
#         GLFW Error Callback

#         :param error_code: GLFW error code
#         :param description: Error description
#         :return: None
#         """
#         raise GLFWError(f"GLFW Error {error_code}: {description.decode()}")


# Auto create Manager Object

# backend = backend_loader.load_backend("genesis") # TODO: Support other backends in future dev.
# manager: CharmyManager = CharmyManager(backend, id_=MANAGER_ID)


def mainloop() -> None:
    """Start main loop."""
    while True:
        for manager in CharmyManager.instances.values():
            manager.update()


def cquit():  # NOQA
    """Quit the main loop"""
    for manager in CharmyManager.instances.values():
        manager.quit()
