"""Charmy windows."""

import typing as _typing

import pathlib as _pathlib
import io as _io

from ..event import EventHandling as _EventHandling, event_types as _event_types
from ..cm_object import CharmyObject as _CharmyObject
from .container import Container as _Container
from .. import const as _const
from ..cmm import CharmyManager as _CharmyManager
from .. import styles as _styles
from ..utils import type_checking as _type_checking
from .. import graphics as _graphics
from ..const import DEBUG_FLAGS as _DEBUG_FLAGS

if _typing.TYPE_CHECKING:
    from ..backend.template import WindowBase as _WindowBase
    from .widget import Widget as _Widget


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
        self.icon = _pathlib.Path(__file__).parent / ".." / "resources" / "imgs" / "window_icon.png"
        self.background = background
        # Other internal attrs
        self._mouse_hovering_on: list[_Container | _Widget] = []
        self._drawing_list: _typing.List[_graphics.DrawnObject] = []
        self._redraw_regions: list[_styles.shape.ShapeRange] = [((0, 0), self.size)]
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
        return self._size

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
    def icon(self, new: str | _pathlib.Path | bytes | _type_checking.PILImageType) -> None:
        if isinstance(new, str) or isinstance(new, _pathlib.Path):
            # Icon file path
            if isinstance(new, str):
                new = _pathlib.Path(new)
            icon_f = open(new, mode="rb")
            self._icon = icon_f.read()
            icon_f.close()
        else:
            # Icon image raw content
            if isinstance(new, _type_checking.PILImageType):
                buffer = _io.BytesIO()
                new.save(buffer, format="PNG")
                new = buffer.getvalue()
                buffer.close()
            self._icon = new
        # Call backend set icon
        self.backend_base.set_icon(self._icon)

    def show(self) -> _typing.Self:
        """Show the window.
        
        Returns:
            self: The window itself
        """
        self.backend_base.show()
        return self

    def draw_frame(self, drawing_list: list[_graphics.DrawnObject]) -> _typing.Self:
        """Draw a frame for the window.
        
        :param drawing_list: The list of the objects to draw
        """
        backend = self.parent.backend # Alias to avoid the path to backend getting too long
        self.backend_base.draw_background()
        for drawn_obj in drawing_list:
            if isinstance(drawn_obj, _graphics.DrawnLine):
                backend.LineBase.draw_line(drawn_obj, self.backend_base)
            elif isinstance(drawn_obj, _graphics.DrawnShape):
                backend.ShapeBase.draw_shape(drawn_obj, self.backend_base)
            elif isinstance(drawn_obj, _graphics.DrawnText):
                backend.TextBase.draw_text(drawn_obj, self.backend_base)
            else:
                raise RuntimeError(
                    f"Unsupported of drawn object type: {drawn_obj.__class__.__name__}"
                    )
        return self

    def _find_need_redraw(self) -> _typing.List[_graphics.DrawnObject]:
        """Find all components that need to be redrawn in current frame."""
        for drawn_obj in self._drawing_list:
            if drawn_obj._need_redraw:
                region = drawn_obj.boundary
                if not region in self._redraw_regions:
                    # Repeat check
                    self._redraw_regions.append(region)
                    drawn_obj._need_redraw = False
        result: _typing.List[_graphics.DrawnObject] = []
        for drawn_obj in self._drawing_list:
            boundary = drawn_obj.boundary
            for region in self._redraw_regions:
                 # Check overlap on both axes (x AND y) to determine intersection
                x1, y1 = boundary[0]
                w1, h1 = boundary[1]
                x2, y2 = region[0]
                w2, h2 = region[1]
                x_overlap = (x1 < x2 + w2) and (x1 + w1 > x2)
                y_overlap = (y1 < y2 + h2) and (y1 + h1 > y2)
                if x_overlap and y_overlap:
                    if drawn_obj not in result:
                        result.append(drawn_obj)
        return result

    def update(self, force_redraw: bool = False):
        """Update the window.

        :param force_redraw: Redraw the window content regardless presence of changes
        """
        # Handle params
        if not self._alive:
            return # Skip if window inactive
        if ((0, 0), self.size) in self._redraw_regions:
            force_redraw = True # When whole window needs redraw, it is force redraw then
        # Trigger event
        self.trigger(_event_types.WidgetUpdate(self))
        if force_redraw:
            redraw_list = self._drawing_list.copy()
        else:
            redraw_list = self._find_need_redraw()
        self.draw_frame(redraw_list)
        # print([str(obj) for obj in redraw_list])
        # Debug: Mark redraws
        if _DEBUG_FLAGS.MARK_REDRAWS:
            for region in self._redraw_regions:
                self.parent.backend.ShapeBase.draw_shape(
                    _graphics.DrawnShape(
                        _styles.shape.Rect(*region), (255, 0, 100, 50)
                        ), 
                    self.backend_base
                    )
        # Update window
        if force_redraw:
            self.backend_base.update(True)
        else:
            for redraw_region in self._redraw_regions:
                self.backend_base.update(redraw_region)
            if len(self._redraw_regions) == 0:
                # If no region to redraw, still update window for events or so
                self.backend_base.update(False)
        self._redraw_regions: list[_styles.shape.ShapeRange] = []

    def destroy(self):
        """Close the window and mark it as inactive."""
        self.backend_base.close()
        self._alive = False

class Window(WindowEntity, _Container):
    """Windows in Charmy."""

    is_root_container: _typing.ClassVar[bool] = True

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