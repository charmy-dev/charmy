from __future__ import annotations as _

import typing

from .styles import texture as cm_texture

if typing.TYPE_CHECKING:
    from .widgets import window as cm_window
    from .styles import shape as cm_shape


# region Drawn Lines / Shapes

class DrawnLine():
    """A class used to represent lines drawn to windows."""
    line: cm_shape.LinePath
    _texture: cm_texture.Texture
    width: int = 5

    def __init__(self, line: cm_shape.LinePath, texture: cm_texture.Texture | cm_texture.TextureLike, width: int = 5):
        """Used to express lines drawn on GUI or canvas.

        :param line: The line (to be drawn)
        :param texture: cm_texture.Texture of the drawn line        :param width:  width
        """
        self.line = line
        self.texture = texture
        self.width = width

    @property
    def texture(self) -> cm_texture.Texture:
        return self._texture

    @texture.setter
    def texture(self, new_texture: cm_texture.Texture | cm_texture.TextureLike) -> None:
        if isinstance(new_texture, cm_texture.Texture):
            self._texture = new_texture
        else:
            # Convert into texture
            self._texture = cm_texture.ensure_texture(new_texture)

    def draw(self, window: cm_window.Window, _fallback_from: list[type[cm_shape.LinePath]] = []) -> typing.Self:
        """Draw the line.

        :param _fallback_from: Fallback path, for internal use
        :param window: The window to draw line to
        """
        backend = window.backend_base.backend
        # 👆 Alias to avoid path to backend properties getting too long. 😅
        if self.line.type == "line_path_class":
            raise TypeError("cm_shape.LinePath class is a template, cannot be drawn.")
        else:
            if self.line.type in backend.LineBase.supports:
                # If supported by the windows' backend.
                window.backend_base.drawing_list.append(self)
                # backend.LineBase.draw_line(self, window, texture)
            else:
                _fallback_from.append(self.line.__class__)
                for fallback_line in self.line.fallback(_from = _fallback_from):
                    fallback_line.draw(window, self.texture, self.width, 
                                       _fallback_from=_fallback_from)
                # warnings.warn(f"Line type {self.line.type} is not supported by "
                #               f"backend {backend.friendly_name}")
        return self


class DrawnShape():
    """A Class used to represent shapes drawn to windows"""
    shape: cm_shape.AnyShape
    _texture: cm_texture.Texture
    border_width: int = 0
    _border_texture: cm_texture.Texture = cm_texture.ensure_texture(None)

    def __init__(self, shape: cm_shape.AnyShape, texture: cm_texture.Texture | cm_texture.TextureLike, 
                 border_width: int = 5, border_texture: cm_texture.Texture | cm_texture.TextureLike = None):
        """Used to express shapes drawn on GUI or canvas.

        :param shape: The shape (to be drawn)
        :param texture: cm_texture.Texture inside the drawn shape
        :param border_width: Border width in px, positive for outer and negative for inner
        :param border_texture: cm_texture.Texture of the drawn border
        """
        self.shape = shape
        self.texture = texture
        self.border_width = border_width
        self.border_texture = border_texture

    @property
    def texture(self) -> cm_texture.Texture:
        return self._texture

    @texture.setter
    def texture(self, new_texture: cm_texture.Texture | cm_texture.TextureLike) -> None:
        if isinstance(new_texture, cm_texture.Texture):
            self._texture = new_texture
        else:
            # Convert into texture
            self._texture = cm_texture.ensure_texture(new_texture)

    @property
    def border_texture(self) -> cm_texture.Texture:
        return self._border_texture

    @border_texture.setter
    def border_texture(self, new_texture: cm_texture.Texture | cm_texture.TextureLike) -> None:
        if isinstance(new_texture, cm_texture.Texture):
            self._border_texture = new_texture
        else:
            # Convert into texture
            self._border_texture = cm_texture.ensure_texture(new_texture)

    def draw(self, window: cm_window.Window) -> typing.Self:
        """Draw the shape using backend.

        :param window: The window to draw shape to
        :param texture: cm_texture.Texture within the shape
        :param border_width: Width of borderline in px, positive for outer and negative for inner
        :param border_texture: cm_texture.Texture used on border
        """
        backend = window.backend_base.backend
        if self.shape.type in backend.ShapeBase.supports or "any_shape" in backend.ShapeBase.supports:
            window.backend_base.drawing_list.append(self)
        return self

# endregion