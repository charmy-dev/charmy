"""Charmy windows."""

import typing

import pathlib

import io

from ..event import EventHandling, event_types
from ..object import CharmyObject
from .container import Container
from .. import const
from ..cmm import CharmyManager
from .. import styles
from ..utils import type_checking

if typing.TYPE_CHECKING:
    from PIL import Image as PIL_Image
    from ..backend.template import WindowBase

__all__ = ["WindowEntity"]


class WindowEntity(EventHandling):
    """Contains abilities of window entities."""

    def __init__(self, 
                parent: CharmyManager | None = None, 
                size: styles.shape.Size = (150, 150), 
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
        self._pos: styles.shape.Point
        self._size: styles.shape.Size
        self._title: str
        self._background: styles.texture.Texture | styles.texture.TextureLike
        self._icon: bytes
        # Other flags
        self.visible = True
        self._alive = True
        # Initialize the WindowBase
        self.backend_base: WindowBase = self.parent.backend.WindowBase(self.parent.backend, self)
        # Set props
        self.size = size
        self.title = title
        self.icon = pathlib.Path(__file__).parent / ".." / "resources" / "imgs" / "window_icon.png"
        self.background = background
        # Show window
        self.show()

    @property
    def pos(self) -> styles.shape.Point:
        """Window position on screen."""
        return self._pos

    @pos.setter
    def pos(self, new: styles.shape.Point) -> None:
        self._pos = new
        self.backend_base.set_pos(new)

    @property
    def size(self) -> styles.shape.Size:
        """Window size."""
        return self.size

    @size.setter
    def size(self, new: styles.shape.Size) -> None:
        self._size = new
        self.backend_base.set_size(new)

    @property
    def title(self) -> str:
        """Window title.

        Type string, internally stored as string. Getting value of this property will return 
        current window title, while setting value will immediately change window's title.
        """
        return self._title

    @title.setter
    def title(self, new: str):
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

    @property
    def icon(self) -> bytes:
        """Window title.

        Type string, `pathlib.Path`, bytes or `Image.Image` from PIL, internally stored as bytes. 
        Getting value of this property will return current window icon, while setting value will 
        immediately change window's title.

        When setting value, values of type string or `Path` express a path to the icon file, while 
        those of type bytes or `Image` express icon image content
        """
        return self._icon

    @icon.setter
    def icon(self, new: str | pathlib.Path | bytes | type_checking.PILImageType) -> None:
        if isinstance(new, str) or isinstance(new, pathlib.Path):
            # Icon file path
            if isinstance(new, str):
                new = pathlib.Path(new)
            icon_f = open(new, mode="rb")
            self._icon = icon_f.read()
            icon_f.close()
        else:
            # Icon image raw content
            if isinstance(new, type_checking.PILImageType):
                buffer = io.BytesIO()
                new.save(buffer, format="PNG")
                new = buffer.getvalue()
                buffer.close()
            self._icon = new
        # Call backend set icon
        self.backend_base.set_icon(self._icon)

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
                size: styles.shape.Size = (540, 360), 
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
        update_event = event_types.UpdateEvent(self)
        self.trigger(update_event)
        self.draw_children()
        WindowEntity.update(self, force_redraw)