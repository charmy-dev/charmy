from __future__ import annotations as _

import typing as _typing

import time as _time

from .backend import loader as _backend_loader
# from .const import MANAGER_ID
# from .event import WorkingThread
# from .frameworks import Frameworks
from .cm_object import CharmyObject as _CharmyObject, CharmyRegisteredObject as _CharmyRegisteredObject
from .event import EventHandling as _EventHandling, event_types as _event_types
from .const import DEBUG_FLAGS as _DEBUG_FLAGS

if _typing.TYPE_CHECKING:
    from .backend.template import Backend
    from . import window


__all__ = ["CharmyManager", "mainloop", "quit"]


class CharmyManager(_CharmyRegisteredObject, _EventHandling):
    """Charmy windows manager. Used to manage windows created with one backend."""

    def __init__(self, backend: str | Backend, **kwargs):
        """Create a Charmy windows manager.

        :param backend: The backend this manager uses
        """
        super().__init__(**kwargs)
        _EventHandling.__init__(self)

        if isinstance(backend, str):
            self.backend: Backend = _backend_loader.load_backend(backend)()
        else:
            self.backend: Backend = backend
        
        self.backend.backend_init()

        self.windows: list[window.WindowEntity] = [] 
        # 👆 Stores all windows this CharmyManager manages
        self._alive = True # This var stores if the manager is still alive

    def update(self) -> _typing.Self:
        """Update all windows under this manager,

        :return self: The manager itself
        """
        if not self._alive:
            return self
        none_alive = True
        for window in self.windows:
            if window.visible and window._alive:
                none_alive = False
                window.update()
        self.trigger(_event_types.WidgetUpdate(self))
        if none_alive:
            self.destroy() # destroy self if no window alive
        return self

    def destroy(self) -> None:
        """Destroy the manager."""
        self._alive = False
        self.trigger(_event_types.WidgetDestroy(self))
        del self
        return


def mainloop(interval: float = .01) -> None:
    """Start main loop.

    :param interval: Time to wait between each loop, in integer seconds
    """
    none_alive = False
    if _DEBUG_FLAGS.WAIT_AFTER_EACH_FRAME != False:
        if _DEBUG_FLAGS.WAIT_AFTER_EACH_FRAME == True:
            interval = 0.5
        else:
            interval = _DEBUG_FLAGS.WAIT_AFTER_EACH_FRAME
    while not none_alive:
        none_alive = True
        for manager_ref in CharmyManager.instances:
            manager = manager_ref
            if manager is not None:
                if manager._alive:
                    none_alive = False
                    manager.update()
        if interval > 0:
            _time.sleep(interval)


def quit():  # NOQA
    """Quit Charmy."""
    for manager_ref in CharmyManager.instances:
        manager = manager_ref
        if manager != None:
            manager.destroy()
