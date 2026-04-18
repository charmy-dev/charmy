import typing

from ..rect import Rect
from .container import Container
from .. import const
from ..cmm import CharmyManager

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
            self.parent = parent
        elif len(CharmyManager.objects.values()) == 1: # Only one manager present
            self.parent = list(CharmyManager.objects.values())[0]
        else:
            if len(const.Common.managers_instances) == 0:
                # If no manager present, create a default
                from ..backend import loader
                self.parent = CharmyManager(const.Configs.default_backend)
            else:
                raise RuntimeError(
                    "No manager specified for window, while multiple managers present."
                    )
        # Handle size
        self.size = size
        if type(self.size[0]) is float or type(self.size[1]) is float:
            self.size = (int(self.size[0]), int(self.size[1]))
        # Window title
        self._title = title
        # Initialize the WindowBase
        self.backend_base = self.parent.backend.WindowBase()
        self.show()

    def show(self) -> Window:
        """Show the window.
        
        Returns:
            self: The window itself
        """
        self.backend_base.show()
        return self

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, new: str) -> Window:
        """Set title of the window.
        
        Returns:
            self: The window itself
        """
        self.backend_base.title = new
        self._title = new
        return self