"""A set of classes represent drawn objects on window. Part of the graphics layer of Charmy."""

from __future__ import annotations as _

import typing

from abc import abstractmethod
import copy

from . import styles
from . import object as cm_object

if typing.TYPE_CHECKING:
    from .widgets import window as cm_window


class DEBUG_FLAGS:
    DRAW_OBJECTS_BOUNDARY: bool = False


# region DrawnObject base class
class DrawnObject(cm_object.CharmyObject):
    """Base class of drawn objects in Charmy."""

    def __init__(self):
        self._actual_draw_list: dict[cm_window.Window, list[DrawnObject]] = {}

    @abstractmethod
    def draw(self, window: cm_window.Window, *args, **kwargs) -> typing.Self: ...

    @property
    @abstractmethod
    def boundary(self) -> styles.shape.ShapeRange: ...

# region Line

class DrawnLine(DrawnObject):
    """A class used to represent lines drawn to GUI or canvas."""

    def __init__(self, 
                line: styles.shape.LinePath, 
                texture: styles.texture.Texture | styles.texture.TextureLike, 
                width: int = 5, 
                offset: styles.shape.Point | typing.Literal["auto"] = "auto", 
                anchor: styles.shape.Point | typing.Literal["auto"] = "auto", 
                ):
        """Used to express lines drawn on GUI or canvas.

        :param line: The line (to be drawn)
        :param texture: Texture of the drawn line
        :param width: Line width
        :param offset: Position offset of the drawn line
        :param anchor: Point of anchor on the original line
        """
        super().__init__()

        self.line: styles.shape.LinePath = line
        self._texture: styles.texture.Texture = styles.texture.ensure_texture(texture)
        self.width: int = width
        if offset == "auto":
            offset = self.line.boundary[0]
        self.offset: styles.shape.Point = offset
        if anchor == "auto":
            anchor = self.line.boundary[0]
        self.anchor: styles.shape.Point = anchor

    @property
    def texture(self) -> styles.texture.Texture:
        """Texture of the drawn line."""
        return self._texture

    @texture.setter
    def texture(self, new_texture: styles.texture.Texture | styles.texture.TextureLike) -> None:
        if isinstance(new_texture, styles.texture.Texture):
            self._texture = new_texture
        else:
            # Convert into texture
            self._texture = styles.texture.ensure_texture(new_texture)

    @property
    def boundary(self) -> styles.shape.ShapeRange:
        """Rect boundary of the drawn line"""
        return (
            self.offset[0] + self.line.boundary[0][0] - self.anchor[0], 
            self.offset[1] + self.line.boundary[0][1] - self.anchor[1]
            ), self.line.boundary[1]

    def draw(self, window: cm_window.Window, 
             _fallback_from: list[type[styles.shape.LinePath]] = []) -> typing.Self:
        """Draw the line.

        :param window: The window to draw line to
        :param _fallback_from: Internal use only, the fallback path
        """
        backend = window.backend_base.backend
        # 👆 Alias to avoid path to backend properties getting too long. 😅
        # Remove currently rencdered copy of this object on the current window
        if window not in self._actual_draw_list.keys():
            self._actual_draw_list[window] = []
        for draw_object in self._actual_draw_list[window]:
            if draw_object in window.backend_base.drawing_list:
                window.backend_base.drawing_list.remove(draw_object)
        self._actual_draw_list[window] = []
        # Rendering process
        for draw_object in self._actual_draw_list:
            if draw_object in window.backend_base.drawing_list:
                window.backend_base.drawing_list.remove(draw_object)
        if self.line.type == "line_path_class":
            raise TypeError("styles.shape.LinePath class is a template, cannot be drawn.")
        else:
            if self.line.type in backend.LineBase.supports:
                # If supported by the windows' backend.
                window.backend_base.drawing_list.append(self)
                self._actual_draw_list[window].append(self)
            else:
                # If not supported, enters the fallback process
                _fallback_from.append(self.line.__class__)
                for fallback_line in self.line.fallback(_from = _fallback_from):
                    drawn_host = copy.copy(self)
                    drawn_host.line = fallback_line
                    drawn_host.draw(window, _fallback_from)
                    self._actual_draw_list[window].append(drawn_host)
            if DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY:
                range_rect = DrawnShape(
                    styles.shape.Rect(*self.line.boundary), 
                    (0, 0, 255, 10), 
                    1, (0, 0, 255), 
                    self.offset, 
                    self.anchor, 
                    )
                window.backend_base.drawing_list.append(range_rect)
                self._actual_draw_list[window].append(range_rect)
        return self


# region Shape

class DrawnShape(DrawnObject):
    """A Class used to represent shapes drawn to GUI or canvas."""

    def __init__(self, 
                shape: styles.shape.ShapeType, 
                texture: styles.texture.Texture | styles.texture.TextureLike, 
                border_width: int = 5, 
                border_texture: styles.texture.Texture | styles.texture.TextureLike = None, 
                offset: styles.shape.Point | typing.Literal["auto"] = "auto", 
                anchor: styles.shape.Point | typing.Literal["auto"] = "auto", 
                ):
        """Used to express shapes drawn on GUI or canvas.

        :param shape: The shape (to be drawn)
        :param texture: styles.texture.Texture inside the drawn shape
        :param border_width: Border width in px, positive for outer and negative for inner
        :param border_texture: styles.texture.Texture of the drawn border
        :param offset: Position offset of the drawn shape
        :param anchor: Point of anchor on the original shape
        """
        super().__init__()

        self.shape: styles.shape.ShapeType = shape
        self._texture: styles.texture.Texture = styles.texture.ensure_texture(texture)
        self.border_width: int = border_width
        self._border_texture: styles.texture.Texture = styles.texture.ensure_texture(border_texture)
        if offset == "auto":
            offset = self.shape.boundary[0]
        self.offset: styles.shape.Point = offset
        if anchor == "auto":
            anchor = self.shape.boundary[0]
        self.anchor: styles.shape.Point = anchor

    @property
    def texture(self) -> styles.texture.Texture:
        """Texture of the drawn shape."""
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
        """Texture used on the border of the drawn shape."""
        return self._border_texture

    @border_texture.setter
    def border_texture(self, 
                       new_texture: styles.texture.Texture | styles.texture.TextureLike) -> None:
        if isinstance(new_texture, styles.texture.Texture):
            self._border_texture = new_texture
        else:
            # Convert into texture
            self._border_texture = styles.texture.ensure_texture(new_texture)

    @property
    def boundary(self) -> styles.shape.ShapeRange:
        """Rect boundary of the drawn shape."""
        return (
            self.offset[0] + self.shape.boundary[0][0] - self.anchor[0], 
            self.offset[1] + self.shape.boundary[0][1] - self.anchor[1]
            ), self.shape.boundary[1]

    def draw(self, 
            window: cm_window.Window, 
            _fallback_from: list[type[styles.shape.LinePath]] = [], 
            ) -> typing.Self:
        """Draw the shape using backend.

        :param window: The window to draw shape to
        :param _fallback_from: Internal use only, the fallback path
        """
        backend = window.backend_base.backend
        # Remove currently rencdered copy of this object on the current window
        if window not in self._actual_draw_list.keys():
            self._actual_draw_list[window] = []
        for draw_object in self._actual_draw_list[window]:
            if draw_object in window.backend_base.drawing_list:
                window.backend_base.drawing_list.remove(draw_object)
        self._actual_draw_list[window] = []
        # Rendering process
        if isinstance(self.shape, styles.shape.ShapeGroup):
            for subshape in self.shape.shapes:
                drawn_host = copy.copy(self)
                drawn_host.shape = subshape
                drawn_host.draw(window, _fallback_from)
                self._actual_draw_list[window].append(drawn_host)
        else:
            backend = window.backend_base.backend
            if self.shape.type in backend.ShapeBase.supports or \
                "any_shape" in backend.ShapeBase.supports:
                window.backend_base.drawing_list.append(self)
            if DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY:
                    range_rect = DrawnShape(
                        styles.shape.Rect(*self.shape.boundary), 
                        (0, 0, 255, 50), 
                        1, (0, 0, 255), 
                        self.offset, 
                        self.anchor
                        )
                    window.backend_base.drawing_list.append(range_rect)
                    self._actual_draw_list[window].append(range_rect)
        return self


# region Text

class DrawnText(DrawnObject):
    """A class used to represent texts drawn to GUI or canvas.

    Notes For Getting Boundary
    --------------------------
    Text relies on backend to render in most cases, so its boundary should be get from backend.
    """

    def __init__(self, 
                text: str, 
                style: styles.text_style.TextStyle, 
                texture: styles.texture.Texture | styles.texture.TextureLike, 
                offset: styles.shape.Point | typing.Literal["auto"] = "auto", 
                anchor: styles.shape.Point | typing.Literal["auto"] = "auto", 
                ):
        """Used to express text drawn on GUI or canvas.

        :param text: The text content, in Python string
        :param style: The text style to use
        :param texture: The texture to use on 
        :param offset: Position of the drawn text
        :param anchor: Point of anchor on the text
        """
        super().__init__()

        self.text: str = text
        self.style: styles.text_style.TextStyle = style
        self._texture: styles.texture.Texture = styles.texture.ensure_texture(texture)
        if offset == "auto":
            offset = (0, 0)
        self.offset: styles.shape.Point = offset
        if anchor == "auto":
            anchor = (0, 0)
        self.anchor: styles.shape.Point = anchor

        self._backend_reported_boundary: styles.shape.ShapeRange = (0, 0), (0, 0)

    @property
    def texture(self) -> styles.texture.Texture:
        """Texture of the drawn text."""
        return self._texture

    @texture.setter
    def texture(self, new_texture: styles.texture.Texture | styles.texture.TextureLike) -> None:
        if isinstance(new_texture, styles.texture.Texture):
            self._texture = new_texture
        else:
            # Convert into texture
            self._texture = styles.texture.ensure_texture(new_texture)

    @property
    def boundary(self) -> styles.shape.ShapeRange:
        """Rect boundary of the drawn text."""
        # TODO: Implement getting text boundary via text-shape conversion
        return self._backend_reported_boundary

    def draw(self, window: cm_window.Window):
        """Draw the text.

        :param window: The window to draw text to
        """
        backend = window.backend_base.backend
        # Remove currently rencdered copy of this object on the current window
        if window not in self._actual_draw_list.keys():
            self._actual_draw_list[window] = []
        for draw_object in self._actual_draw_list[window]:
            if draw_object in window.backend_base.drawing_list:
                window.backend_base.drawing_list.remove(draw_object)
        self._actual_draw_list[window] = []
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
                rendered_style = copy.deepcopy(self.style)
                ## Custom underline and strikethrough
                if not backend.TextBase.supports.custom_underline:
                    rendered_style.underlined = True
                if not backend.TextBase.supports.custom_strikethrough:
                    rendered_style.strikethrough = True
                ## Fontweight
                # Set font weight to closest supported one
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
            self._actual_draw_list[window].append(self)
            if DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY:
                range_rect = DrawnShape(
                    styles.shape.Rect(*self.boundary), 
                    (0, 0, 255, 50), 
                    1, (0, 0, 255), 
                    # self.offset, 
                    # self.anchor, 
                    )
                window.backend_base.drawing_list.append(range_rect)
                self._actual_draw_list[window].append(range_rect)
        else:
            #### Render as shape
            # TODO: Implement text → shape fallback
            raise NotImplementedError("Currently cannot render text as shape!")