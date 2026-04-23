import typing

from ..rect import Rect
from .container import Container
from .. import const
from ..cmm import CharmyManager

if typing.TYPE_CHECKING:
    from ..backend.template import WindowBase


class Window(Container):
    """Window class."""

    def __init__(self, 
                 parent: CharmyManager | None = None, 
                 size: tuple[int | float, int | float] = (540, 480), 
                 title: str = "Charmy Window", 
                 *args, **kwargs):
        """To create and initialize a window."""
        super().__init__(*args, **kwargs)
        # Store parent maanger
        if parent != None: # Parent manager already specified
            self.parent: CharmyManager = parent
        elif len(CharmyManager.instances.values()) == 1: # Only one manager present
            self.parent: CharmyManager = list(CharmyManager.instances.values())[0]
        else:
            if len(CharmyManager.instances) == 0:
                # If no manager present, create a default
                from ..backend import loader
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
    def title(self, new: str) -> Window:
        """Set title of the window.
        
        Returns:
            self: The window itself
        """
        self.backend_base.set_title(new)
        self._title = new
        return self

    def show(self) -> Window:
        """Show the window.
        
        Returns:
            self: The window itself
        """
        self.backend_base.show()
        return self
    
    def update(self):
        self.backend_base.update()