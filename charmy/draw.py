"""A set of classes represent drawn objects on window. Part of the graphics layer of Charmy."""

from __future__ import annotations as _

import typing

from abc import abstractmethod
import copy

# from .styles import texture as cm_texture
# from .styles import text_style as cm_text_style
from . import styles
from . import object as cm_object

if typing.TYPE_CHECKING:
    from .widgets import window as cm_window
    # from .styles import shape as cm_shape
    # from .styles import text_style as cm_font


class DEBUG_OPTIONS:
    DRAW_OBJECTS_BOUNDARY: bool = True


# region DrawnObject base class
class DrawnObject(cm_object.CharmyObject):
    """Base class of drawn objects in Charmy."""

    def __init__(self):
        """Base class of drawn objects, should not be instantiated directly."""
        self.anchor: styles.shape.Point = (0, 0)

    @abstractmethod
    def draw(self, window: cm_window.Window): ...

# region Lines & Shapes

class DrawnLine(DrawnObject):
    """A class used to represent lines drawn to GUI or canvas."""
    line: styles.shape.LinePath
    _texture: styles.texture.Texture
    width: int = 5

    def __init__(self, 
                line: styles.shape.LinePath, 
                texture: styles.texture.Texture | styles.texture.TextureLike, 
                width: int = 5):
        """Used to express lines drawn on GUI or canvas.

        :param line: The line (to be drawn)
        :param texture: styles.texture.Texture of the drawn line        :param width:  width
        """
        self.line: styles.shape.LinePath = line
        self._texture: styles.texture.Texture = styles.texture.ensure_texture(texture)
        self.width: int = width

    @property
    def texture(self) -> styles.texture.Texture:
        return self._texture

    @texture.setter
    def texture(self, new_texture: styles.texture.Texture | styles.texture.TextureLike) -> None:
        if isinstance(new_texture, styles.texture.Texture):
            self._texture = new_texture
        else:
            # Convert into texture
            self._texture = styles.texture.ensure_texture(new_texture)

    def draw(self, window: cm_window.Window, 
             _fallback_from: list[type[styles.shape.LinePath]] = []) -> typing.Self:
        """Draw the line.

        :param _fallback_from: Fallback path, for internal use
        :param window: The window to draw line to
        """
        backend = window.backend_base.backend
        # 👆 Alias to avoid path to backend properties getting too long. 😅
        if self.line.type == "line_path_class":
            raise TypeError("styles.shape.LinePath class is a template, cannot be drawn.")
        else:
            if self.line.type in backend.LineBase.supports:
                # If supported by the windows' backend.
                window.backend_base.drawing_list.append(self)
            else:
                # If not supported, enters the fallback process
                _fallback_from.append(self.line.__class__)
                for fallback_line in self.line.fallback(_from = _fallback_from):
                    fallback_line.draw(window, self.texture, self.width, 
                                       _fallback_from=_fallback_from)
            if DEBUG_OPTIONS.DRAW_OBJECTS_BOUNDARY:
                window.backend_base.drawing_list.append(DrawnShape(
                    styles.shape.Rect(*self.line.boundary), 
                    (0, 0, 255, 30), 
                    1, (0, 0, 255), 
                    ))
        return self


class DrawnShape(DrawnObject):
    """A Class used to represent shapes drawn to GUI or canvas."""
    shape: styles.shape.AnyShape
    _texture: styles.texture.Texture
    border_width: int = 0
    _border_texture: styles.texture.Texture = styles.texture.ensure_texture(None)

    def __init__(self, 
                shape: styles.shape.AnyShape, 
                texture: styles.texture.Texture | styles.texture.TextureLike, 
                border_width: int = 5, 
                border_texture: styles.texture.Texture | styles.texture.TextureLike = None):
        """Used to express shapes drawn on GUI or canvas.

        :param shape: The shape (to be drawn)
        :param texture: styles.texture.Texture inside the drawn shape
        :param border_width: Border width in px, positive for outer and negative for inner
        :param border_texture: styles.texture.Texture of the drawn border
        """
        self.shape: styles.shape.AnyShape = shape
        self._texture: styles.texture.Texture = styles.texture.ensure_texture(texture)
        self.border_width: int = border_width
        self._border_texture: styles.texture.Texture = styles.texture.ensure_texture(border_texture)

    @property
    def texture(self) -> styles.texture.Texture:
        return self._texture

    @texture.setter
    def texture(self, new_texture: styles.texture.Texture | styles.texture.TextureLike) -> None:
        if isinstance(new_texture, styles.texture.Texture):
            self._texture = new_texture
        else:
            # Convert into texture
            self._texture = styles.texture.ensure_texture(new_texture)

    @property
    def border_texture(self) -> styles.texture.Texture:
        return self._border_texture

    @border_texture.setter
    def border_texture(self, 
                       new_texture: styles.texture.Texture | styles.texture.TextureLike) -> None:
        if isinstance(new_texture, styles.texture.Texture):
            self._border_texture = new_texture
        else:
            # Convert into texture
            self._border_texture = styles.texture.ensure_texture(new_texture)

    def draw(self, window: cm_window.Window) -> typing.Self:
        """Draw the shape using backend.

        :param window: The window to draw shape to
        :param texture: styles.texture.Texture within the shape
        :param border_width: Width of borderline in px, positive for outer and negative for inner
        :param border_texture: styles.texture.Texture used on border
        """
        backend = window.backend_base.backend
        if self.shape.type in backend.ShapeBase.supports or \
            "any_shape" in backend.ShapeBase.supports:
            window.backend_base.drawing_list.append(self)
        return self

# endregion

# region Text

class DrawnText(DrawnObject):
    """A class used to represent texts drawn to GUI or canvas."""

    def __init__(self, 
                text: str, 
                font: styles.text_style.TextStyle, 
                pos: styles.shape.Point, 
                texture: styles.texture.Texture | styles.texture.TextureLike):
        """Used to express text drawn on GUI or canvas.

        :param text: The text content, in Python string
        :param font: The text style to use
        :param texture: The texture to use on text
        """
        self.text: str = text
        self.style: styles.text_style.TextStyle = font
        self.pos: styles.shape.Point = pos
        self._texture: styles.texture.Texture = styles.texture.ensure_texture(texture)

    @property
    def texture(self) -> styles.texture.Texture:
        return self._texture

    @texture.setter
    def texture(self, new_texture: styles.texture.Texture | styles.texture.TextureLike) -> None:
        if isinstance(new_texture, styles.texture.Texture):
            self._texture = new_texture
        else:
            # Convert into texture
            self._texture = styles.texture.ensure_texture(new_texture)

    def draw(self, window: cm_window.Window):
        backend = window.backend_base.backend
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
                rendered_style = copy.deepcopy(self.style)
                ## Custom underline and strikethrough
                if not backend.TextBase.supports.custom_underline:
                    rendered_style.underlined = True
                if not backend.TextBase.supports.custom_strikethrough:
                    rendered_style.strikethrough = True
                ## Fontweight
                # This part vibed with GitHub Copilot using model GPT-5 mini
                available_weights = backend.TextBase.supports.fontweight
                if self.style.weight not in available_weights:
                    closest = min(available_weights, key=lambda w: abs(w - self.style.weight))
                    rendered_style.weight = closest
                ## Make new render object
                rendered_text = copy.deepcopy(self)
                rendered_text.style = rendered_style
            else:
                rendered_text = self
            window.backend_base.drawing_list.append(rendered_text)
        else:
            #### Render as shape
            # TODO: Implement text → shape fallback
            raise NotImplementedError("Currently cannot render text as shape!")