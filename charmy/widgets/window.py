import typing

from ..event import EventHandling, Event
from ..object import CharmyObject
from .container import Container
from .. import const
from ..cmm import CharmyManager

if typing.TYPE_CHECKING:
    from ..backend.template import WindowBase


class WindowEntity:
    """Represents abilities of window entities."""

    def __init__(self, 
                parent: CharmyManager | None = None, 
                size: tuple[int | float, int | float] = (540, 480), 
                title: str = "Charmy Window", 
                *args, **kwargs):
        """To create and initialize a window."""
        super().__init__(*args, **kwargs)
        # Store parent maanger
        if parent is not None: # Parent manager already specified
            self.parent: CharmyManager = parent
        elif len(CharmyManager.instances) == 1: # Only one manager present
            parent = CharmyManager.instances[0]
            if parent is not None:
                self.parent: CharmyManager = parent
            else:
                self.parent: CharmyManager = CharmyManager(const.Configs.default_backend)
        else:
            if len(CharmyManager.instances) == 0:
                # If no manager present, create a default
                self.parent: CharmyManager = CharmyManager(const.Configs.default_backend)
            else:
                raise RuntimeError(
                    "No manager specified for window, while multiple managers present."
                    )
        self.parent.windows.append(self)
        # Handle size
        self.size = size
        if type(self.size[0]) is float or type(self.size[1]) is float:
            self.size = (int(self.size[0]), int(self.size[1]))
        # Window title
        self._title = title
        # Other flags
        self.visible = True
        self._alive = True
        # Initialize the WindowBase
        self.backend_base: WindowBase = self.parent.backend.WindowBase(self.parent.backend)
        self.show()

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, new: str):
        """Set title of the window.
        
        Returns:
            self: The window itself
        """
        self.backend_base.set_title(new)
        self._title = new

    def show(self) -> typing.Self:
        """Show the window.
        
        Returns:
            self: The window itself
        """
        self.backend_base.show()
        return self
    
    def update(self, force_redraw: bool = False):
        """Update the window.

        :param force_redraw: Redraw the window content regardless presence of changes
        """
        self.backend_base.update()


class Window(CharmyObject, WindowEntity, Container, EventHandling):
    """Windows in Charmy."""

    def __init__(self, 
                parent: CharmyManager | None = None, 
                size: tuple[int | float, int | float] = (540, 480), 
                title: str = "Charmy Window", 
                ):
        """To create a window in Charmy."""
        CharmyObject.__init__(self)
        WindowEntity.__init__(self, parent, size, title)
        Container.__init__(self)
        EventHandling.__init__(self)

    def update(self, force_redraw: bool = False):
        """Update the window.

        :param force_redraw: Redraw the window content regardless presence of changes
        """
        update_event = Event(self, "update")
        self.trigger(update_event)
        WindowEntity.update(self, force_redraw)