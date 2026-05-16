from __future__ import annotations as _

import typing

import time
import warnings

from .backend import loader as backend_loader
# from .const import MANAGER_ID
# from .event import WorkingThread
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

        :param backend: The backend this manager uses
        """
        super().__init__(**kwargs)

        if isinstance(backend, str):
            self.backend: Backend = backend_loader.load_backend(backend)()
        else:
            self.backend: Backend = backend
        
        self.backend.backend_init()

        self.windows: list[window.WindowEntity] = [] 
        # 👆 Stores all windows this CharmyManager manages
        self.is_alive = True # This var stores if the manager is still alive

    def update(self) -> typing.Self:
        """Update all windows under this manager,

        :return self: The manager itself
        """
        for window in self.windows:
            if window.visible and window._alive:
                window.update()
        return self

    def destroy(self) -> None:
        """Destroy the manager."""
        del self
        return


def mainloop(interval: float = 0) -> None:
    """Start main loop.

    :param interval: Time to wait between each loop, in integer seconds
    """
    while True:
        for manager_ref in CharmyManager.instances:
            manager = manager_ref()
            if manager != None:
                manager.update()
        if interval > 0:
            time.sleep(interval)


def quit():  # NOQA
    """Quit Charmy."""
    for manager_ref in CharmyManager.instances:
        manager = manager_ref()
        if manager != None:
            manager.destroy()
