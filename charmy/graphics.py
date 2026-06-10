"""A set of classes represent drawn objects on window. Part of the graphics layer of Charmy."""

from __future__ import annotations as _

import typing as _typing

from abc import abstractmethod as _abstractmethod
import copy as _copy

from . import styles as _styles
from . import cm_object as _cm_object
from .const import DEBUG_FLAGS as _DEBUG_FLAGS


if _typing.TYPE_CHECKING:
    from .widgets import window as _window


def _draw_bbox(obj: DrawnObject):
    range_rect = DrawnShape(
        obj.window, 
        _styles.shape.Rect(*obj.boundary), 
        (0, 0, 255, 20), 
        1, (0, 0, 255), 
        obj.offset, 
        obj.anchor, 
        )
    # obj.window.parent.backend.ShapeBase.draw_shape(range_rect)
    _DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY = False # Temporarily disable to avoid infinite loop
    range_rect.draw()
    _DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY = True


# region DrawnObject base class
class DrawnObject(_cm_object.CharmyObject):
    """Base class of drawn objects in Charmy."""

    def __init__(self, window: _window.WindowEntity):
        """To represent a drawn object, inherit this class."""
        self._booting: bool = True
        super().__init__()
        self._attrs: list[str] = []
        self._need_redraw: bool = True
        self._drawn: bool = False
        self._booting = False
        self.window: _window.WindowEntity = window
        self.offset: _styles.shape.Point
        self.anchor: _styles.shape.Point

    @_abstractmethod
    def draw(self, *args, **kwargs) -> _typing.Self: ...

    @property
    @_abstractmethod
    def boundary(self) -> _styles.shape.ShapeRange: ...

    @_abstractmethod
    def __contains__(self, point: _styles.shape.Point) -> bool: ...

    # def __setattr__(self, name: str, value: _typing.Any) -> None:
    #     """Set attr and mark self need redraw."""
    #     # Pass internal, and pass when object initializing
    #     if name.startswith("_"):
    #         return super().__setattr__(name, value)
    #     if self._booting:
    #         return super().__setattr__(name, value)
    #     # If is an watched attr of self, add self bbox to redraw list
    #     # If position changed, add both old and new bbox
    #     if self._drawn:
    #         old_boundary = self.boundary
    #     super().__setattr__(name, value)
    #     if name in self._attrs and self._drawn:
    #         self.window._redraw_regions.append(self.boundary)
    #         print(f"{self.id} redrawn on {name} change")
    #         if self.boundary != old_boundary:
    #             self.window._redraw_regions.append(old_boundary)

# region Line

class DrawnLine(DrawnObject):
    """A class used to represent lines drawn to GUI or canvas."""

    def __init__(self, 
                window: _window.WindowEntity, 
                line: _styles.shape.LinePath, 
                texture: _styles.texture.Texture | _styles.texture.TextureLike, 
                width: int = 5, 
                offset: _styles.shape.Point | _typing.Literal["auto"] = "auto", 
                anchor: _styles.shape.Point | _typing.Literal["auto"] = "auto", 
                ):
        """Used to express lines drawn on GUI or canvas.

        :param line: The line (to be drawn)
        :param texture: Texture of the drawn line
        :param width: Line width
        :param offset: Position offset of the drawn line
        :param anchor: Point of anchor on the original line
        """
        super().__init__(window)
        self._attrs = ["line", "texture", "width", "offset", "anchor"]

        self.line: _styles.shape.LinePath = line
        self._texture: _styles.texture.Texture = _styles.texture.ensure_texture(texture)
        self.width: int = width
        if offset == "auto":
            offset = self.line.boundary[0]
        self.offset: _styles.shape.Point = offset
        if anchor == "auto":
            anchor = self.line.boundary[0]
        self.anchor: _styles.shape.Point = anchor

    @property
    def texture(self) -> _styles.texture.Texture:
        """Texture of the drawn line."""
        return self._texture

    @texture.setter
    def texture(self, new_texture: _styles.texture.Texture | _styles.texture.TextureLike) -> None:
        if isinstance(new_texture, _styles.texture.Texture):
            self._texture = new_texture
        else:
            # Convert into texture
            self._texture = _styles.texture.ensure_texture(new_texture)

    @property
    def boundary(self) -> _styles.shape.ShapeRange:
        """Rect boundary of the drawn line"""
        return (
            self.offset[0] + self.line.boundary[0][0] - self.anchor[0], 
            self.offset[1] + self.line.boundary[0][1] - self.anchor[1]
            ), self.line.boundary[1]

    def draw(self, 
            _fallback_from: _typing.Optional[list[type[_styles.shape.LinePath]]] = None
            ) -> _typing.Self:
        """Draw the line.

        :param window: The window to draw line to
        :param _fallback_from: Internal use only, the fallback path
        """

        window = self.window

        if not _fallback_from:
            _fallback_from = []

        backend = window.parent.backend
        # 👆 Alias to avoid path to backend properties getting too long. 😅
        # Remove self from render list if already rendered
        if self in self.window._drawing_list:
            self.window._drawing_list.remove(self)
        # Rendering process
        if self.line.type == "line_path_class":
            raise TypeError("styles.shape.LinePath class is a template, cannot be drawn.")
        else:
            if self.line.type in backend.LineBase.supports:
                # If supported by the windows' backend.
                window.backend_base.charmy_window._drawing_list.append(self)
            else:
                # If not supported, enters the fallback process
                _fallback_from.append(self.line.__class__)
                for fallback_line in self.line.fallback(_from = _fallback_from):
                    drawn_host = _copy.copy(self)
                    drawn_host.line = fallback_line
                    drawn_host.draw(_fallback_from)
            if _DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY:
                _draw_bbox(self)
        self._drawn = True
        return self

    def __contains__(self, point: _styles.shape.Point) -> bool:
        return False


# region Shape

class DrawnShape(DrawnObject):
    """A Class used to represent shapes drawn to GUI or canvas."""

    def __init__(self, 
                window: _window.WindowEntity, 
                shape: _styles.shape.ShapeType, 
                texture: _styles.texture.Texture | _styles.texture.TextureLike, 
                border_width: int = 0, 
                border_texture: _styles.texture.Texture | _styles.texture.TextureLike = None, 
                offset: _styles.shape.Point | _typing.Literal["auto"] = "auto", 
                anchor: _styles.shape.Point | _typing.Literal["auto"] = "auto", 
                ):
        """Used to express shapes drawn on GUI or canvas.

        :param shape: The shape (to be drawn)
        :param texture: styles.texture.Texture inside the drawn shape
        :param border_width: Border width in px, positive for outer and negative for inner
        :param border_texture: styles.texture.Texture of the drawn border
        :param offset: Position offset of the drawn shape
        :param anchor: Point of anchor on the original shape
        """
        super().__init__(window)
        self._attrs = ["shape", "texture", "border_width", "border_texture", "offset", "anchor"]

        self.shape: _styles.shape.ShapeType = shape
        self._texture: _styles.texture.Texture = _styles.texture.ensure_texture(texture)
        self.border_width: int = border_width
        self._border_texture: _styles.texture.Texture = _styles.texture.ensure_texture(border_texture)
        if offset == "auto":
            offset = self.shape.boundary[0]
        self.offset: _styles.shape.Point = offset
        if anchor == "auto":
            anchor = self.shape.boundary[0]
        self.anchor: _styles.shape.Point = anchor

    @property
    def texture(self) -> _styles.texture.Texture:
        """Texture of the drawn shape."""
        return self._texture

    @texture.setter
    def texture(self, new_texture: _styles.texture.Texture | _styles.texture.TextureLike) -> None:
        if isinstance(new_texture, _styles.texture.Texture):
            self._texture = new_texture
        else:
            # Convert into texture
            self._texture = _styles.texture.ensure_texture(new_texture)

    @property
    def border_texture(self) -> _styles.texture.Texture:
        """Texture used on the border of the drawn shape."""
        return self._border_texture

    @border_texture.setter
    def border_texture(self, 
                       new_texture: _styles.texture.Texture | _styles.texture.TextureLike) -> None:
        if isinstance(new_texture, _styles.texture.Texture):
            self._border_texture = new_texture
        else:
            # Convert into texture
            self._border_texture = _styles.texture.ensure_texture(new_texture)

    @property
    def boundary(self) -> _styles.shape.ShapeRange:
        """Rect boundary of the drawn shape."""
        return (
            self.offset[0] + self.shape.boundary[0][0] - self.anchor[0], 
            self.offset[1] + self.shape.boundary[0][1] - self.anchor[1]
            ), self.shape.boundary[1]

    def copy(self) -> DrawnShape:
        return DrawnShape(
            self.window, 
            self.shape, 
            self.texture, 
            self.border_width, 
            self.border_texture, 
            self.offset, 
            self.anchor
            )

    def draw(self, 
            _fallback_from: list[type[_styles.shape.LinePath]] = [], 
            ) -> _typing.Self:
        """Draw the shape using backend.

        :param window: The window to draw shape to
        :param _fallback_from: Internal use only, the fallback path
        """
        backend = self.window.parent.backend
        # Remove self from render list if already rendered
        if self in self.window._drawing_list:
            self.window._drawing_list.remove(self)
        # Rendering process
        backend = self.window.parent.backend
        if self.shape.type in backend.ShapeBase.supports or \
            "any_shape" in backend.ShapeBase.supports:
            self.window.backend_base.charmy_window._drawing_list.append(self)
        if _DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY:
            _draw_bbox(self)
        self.window._redraw_regions.append(self.boundary)
        self._drawn = True
        return self

    def __contains__(self, point: _styles.shape.Point) -> bool:
        return point in self.shape


# region Text

class DrawnText(DrawnObject):
    """A class used to represent texts drawn to GUI or canvas.

    Notes For Getting Boundary
    --------------------------
    Text relies on backend to render in most cases, so its boundary should be gotten from backend.
    """

    def __init__(self, 
                window: _window.WindowEntity, 
                text: str, 
                style: _styles.text_style.TextStyle, 
                texture: _styles.texture.Texture | _styles.texture.TextureLike, 
                offset: _styles.shape.Point | _typing.Literal["auto"] = "auto", 
                anchor: _styles.shape.Point | _typing.Literal["auto"] = "auto", 
                ):
        """Used to express text drawn on GUI or canvas.

        :param text: The text content, in Python string
        :param style: The text style to use
        :param texture: The texture to use on 
        :param offset: Position of the drawn text
        :param anchor: Point of anchor on the text
        """
        super().__init__(window)
        self._attrs = ["text", "style", "texture", "offset", "anchor"]

        self.text: str = text
        self.style: _styles.text_style.TextStyle = style
        self._texture: _styles.texture.Texture = _styles.texture.ensure_texture(texture)
        if offset == "auto":
            offset = (0, 0)
        self.offset: _styles.shape.Point = offset
        if anchor == "auto":
            anchor = (0, 0)
        self.anchor: _styles.shape.Point = anchor

        self._backend_reported_boundary: _styles.shape.ShapeRange = (0, 0), (0, 0)

    @property
    def texture(self) -> _styles.texture.Texture:
        """Texture of the drawn text."""
        return self._texture

    @texture.setter
    def texture(self, new_texture: _styles.texture.Texture | _styles.texture.TextureLike) -> None:
        if isinstance(new_texture, _styles.texture.Texture):
            self._texture = new_texture
        else:
            # Convert into texture
            self._texture = _styles.texture.ensure_texture(new_texture)

    @property
    def boundary(self) -> _styles.shape.ShapeRange:
        """Rect boundary of the drawn text."""
        # TODO: Implement getting text boundary via text-shape conversion
        return self._backend_reported_boundary

    def draw(self) -> _typing.Self:
        """Draw the text.

        :param window: The window to draw text to
        """
        backend = self.window.parent.backend
        # Remove self from render list if already rendered
        if self in self.window._drawing_list:
            self.window._drawing_list.remove(self)
        # Rendering process
        if backend.TextBase.supports.direct_render:
            # TODO: Add support for backend's prefer_conversion flag
            #### Direct render
            ### Handle fallback of styles
            if not False in [
                    backend.TextBase.supports.custom_strikethrough, 
                    backend.TextBase.supports.custom_underline, 
                    backend.TextBase.supports.any_fontweight, 
                    ]:
                ## Make a copy of current style
                rendered_style = _copy.deepcopy(self.style)
                ## Custom underline and strikethrough
                if not backend.TextBase.supports.custom_underline:
                    rendered_style.underlined = True
                if not backend.TextBase.supports.custom_strikethrough:
                    rendered_style.strikethrough = True
                ## Font weight
                # Set font weight to closest supported one
                # This part vibed with GitHub Copilot using model GPT-5 mini
                available_weights = backend.TextBase.supports.fontweight
                if self.style.weight not in available_weights:
                    closest = min(available_weights, key=lambda w: abs(w - self.style.weight))
                    rendered_style.weight = closest
                ## Make new render object
                rendered_text = _copy.deepcopy(self)
                rendered_text.style = rendered_style
            else:
                rendered_text = self
            self.window.backend_base.charmy_window._drawing_list.append(rendered_text)
            if _DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY:
                _draw_bbox(self)
        else:
            #### Render as shape
            # TODO: Implement text → shape fallback
            raise NotImplementedError("Currently cannot render text as shape!")
        self._drawn = True
        return self

    def __contains__(self, point: _styles.shape.Point) -> bool:
        return point in _styles.shape.Rect(*self.boundary)