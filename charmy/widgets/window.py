import typing

from ..event import EventHandling, Event
from ..object import CharmyObject
from .container import Container
from .. import const
from ..cmm import CharmyManager
from .. import styles

if typing.TYPE_CHECKING:
    from ..backend.template import WindowBase


class WindowEntity:
    """Represents abilities of window entities."""

    def __init__(self, 
                parent: CharmyManager | None = None, 
                size: styles.shape.Size = (540, 480), 
                title: str = "Charmy Window", 
                background: styles.texture.Texture | styles.texture.TextureLike = (150, 150, 150), 
                *args, **kwargs):
        """To create and initialize a window."""
        super().__init__(*args, **kwargs)
        # Store parent manager
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
        # Define internal props
        self._size: styles.shape.Size
        self._title: str
        self._background: styles.texture.Texture | styles.texture.TextureLike
        # Other flags
        self.visible = True
        self._alive = True
        # Initialize the WindowBase
        self.backend_base: WindowBase = self.parent.backend.WindowBase(self.parent.backend)
        # Set props
        self.size = size
        self.title = title
        self.background = background
        # Show window
        self.show()

    @property
    def title(self) -> str:
        """Window title"""
        return self._title

    @title.setter
    def title(self, new: str):
        """Set title of the window.
        
        Returns:
            self: The window itself
        """
        self.backend_base.set_title(new)
        self._title = new

    @property
    def background(self) -> styles.texture.Texture | styles.texture.TextureLike:
        """Window background"""
        return self._background

    @background.setter
    def background(self, new: styles.texture.Texture | styles.texture.TextureLike):
        self.backend_base.background = styles.texture.ensure_texture(new)
        self._background = new

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

    is_root_container: typing.ClassVar[bool] = True

    def __init__(self, 
                parent: CharmyManager | None = None, 
                size: styles.shape.Size = (540, 480), 
                title: str = "Charmy Window", 
                background: styles.texture.Texture | styles.texture.TextureLike = (255, 255, 255), 
                ):
        """To create a window in Charmy."""
        CharmyObject.__init__(self)
        WindowEntity.__init__(self, parent, size, title, background)
        Container.__init__(self)
        EventHandling.__init__(self)

    def update(self, force_redraw: bool = False):
        """Update the window.

        :param force_redraw: Redraw the window content regardless presence of changes
        """
        update_event = Event(self, "update")
        self.trigger(update_event)
        WindowEntity.update(self, force_redraw)