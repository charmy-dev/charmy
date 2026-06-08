"""Charmy windows."""

import typing

import pathlib

import io

from ..event import EventHandling as _EventHandling, event_types as _event_types
from ..cm_object import CharmyObject as _CharmyObject
from .container import Container as _Container
from .. import const as _const
from ..cmm import CharmyManager as _CharmyManager
from .. import styles as _styles
from ..utils import type_checking as _type_checking

if typing.TYPE_CHECKING:
    from ..backend.template import WindowBase as _WindowBase
    from .widget import Widget as _Widget
    from ..graphics import DrawnObject as _DrawnObject


__all__ = ["WindowEntity", "Window"]


class WindowEntity(_CharmyObject, _EventHandling):
    """Contains abilities of window entities."""

    def __init__(self, 
                parent: _CharmyManager | None = None, 
                size: _styles.shape.Size = (150, 150), 
                title: str = "Charmy Window", 
                background: _styles.texture.Texture | _styles.texture.TextureLike = (150, 150, 150), 
                *args, **kwargs):
        """To create and initialize a window."""
        super().__init__(*args, **kwargs)
        _EventHandling.__init__(self)
        # Store parent manager
        if parent is not None: # Parent manager already specified
            self.parent: _CharmyManager = parent
        elif len(_CharmyManager.instances) == 1: # Only one manager present
            parent = _CharmyManager.instances["CharmyManager0"]
            if parent is not None:
                self.parent: _CharmyManager = parent
            else:
                self.parent: _CharmyManager = _CharmyManager(_const.Configs.default_backend)
        else:
            if len(_CharmyManager.instances) == 0:
                # If no manager present, create a default
                self.parent: _CharmyManager = _CharmyManager(_const.Configs.default_backend)
            else:
                raise RuntimeError(
                    "No manager specified for window, while multiple managers present."
                    )
        self.parent.windows.append(self)
        # Define internal props
        self._pos: _styles.shape.Point
        self._size: _styles.shape.Size
        self._title: str
        self._background: _styles.texture.Texture | _styles.texture.TextureLike
        self._icon: bytes
        # Other flags
        self.visible = True
        self._alive = True
        # Initialize the WindowBase
        self.backend_base: _WindowBase = self.parent.backend.WindowBase(self.parent.backend, self)
        # Set props
        self.size = size
        self.title = title
        self.icon = pathlib.Path(__file__).parent / ".." / "resources" / "imgs" / "window_icon.png"
        self.background = background
        # Other internal attrs
        self._mouse_hovering_on: list[_Container | _Widget] = []
        self._drawing_list: typing.List[_DrawnObject] = []
        # Bind on window close
        self.bind(_event_types.WidgetDestroy, lambda _: self.destroy(), _is_internal=True)
        # Show window
        self.show()

    @property
    def pos(self) -> _styles.shape.Point:
        """Window position on screen."""
        return self._pos

    @pos.setter
    def pos(self, new: _styles.shape.Point) -> None:
        self._pos = new
        self.backend_base.set_pos(new)

    @property
    def abs_pos(self) -> _styles.shape.Point:
        return(0, 0)

    @property
    def size(self) -> _styles.shape.Size:
        """Window size."""
        return self.size

    @size.setter
    def size(self, new: _styles.shape.Size) -> None:
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
    def background(self) -> _styles.texture.Texture | _styles.texture.TextureLike:
        """Window background"""
        return self._background

    @background.setter
    def background(self, new: _styles.texture.Texture | _styles.texture.TextureLike):
        self.backend_base.background = _styles.texture.ensure_texture(new)
        self._background = new

    @property
    def icon(self) -> bytes:
        """Window title.

        Type string, `pathlib.Path`, bytes or `Image.Image` from PIL, internally stored as bytes. 
        Getting value of this property will return current window icon, while setting value will 
        immediately change window's title.

        When setting value, values of type string or `Path` express a path to the icon file, while 
        those of type bytes or `Image` express icon image content.
        """
        return self._icon

    @icon.setter
    def icon(self, new: str | pathlib.Path | bytes | _type_checking.PILImageType) -> None:
        if isinstance(new, str) or isinstance(new, pathlib.Path):
            # Icon file path
            if isinstance(new, str):
                new = pathlib.Path(new)
            icon_f = open(new, mode="rb")
            self._icon = icon_f.read()
            icon_f.close()
        else:
            # Icon image raw content
            if isinstance(new, _type_checking.PILImageType):
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
        if self._alive:
            update_event = _event_types.WidgetUpdate(self)
            self.trigger(update_event)
            self.backend_base.update()

    def destroy(self):
        """Close the window and mark it as inactive."""
        self.backend_base.close()
        self._alive = False

class Window(WindowEntity, _Container):
    """Windows in Charmy."""

    is_root_container: typing.ClassVar[bool] = True

    def __init__(self, 
                parent: _CharmyManager | None = None, 
                size: _styles.shape.Size = (540, 360), 
                title: str = "Charmy Window", 
                background: _styles.texture.Texture | _styles.texture.TextureLike = (255, 255, 255), 
                ):
        """To create a window in Charmy."""
        WindowEntity.__init__(self, parent, size, title, background)
        _Container.__init__(self)

    def update(self, force_redraw: bool = False):
        """Update the window.

        :param force_redraw: Redraw the window content regardless presence of changes
        """
        _Container.draw_children(self)
        WindowEntity.update(self, force_redraw)

    def destroy(self):
        """Destroy the window and its children."""
        super().destroy()