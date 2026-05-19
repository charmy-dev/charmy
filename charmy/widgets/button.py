from __future__ import annotations

import typing

from .widget import Widget
from .window import Window
from .. import styles
from .. import graphics

if typing.TYPE_CHECKING:
    from .. import container


class Button(Widget):
    """Text buttons in Charmy."""

    def __init__(self, 
                parent: container.Container, 
                text: str, 
                on_click: typing.Callable = lambda: None, 
                style: dict[str, typing.Any] = {
                    # Default button style (bootstrap)
                    # These styles JSON might be moved to somewhere else in future...
                    ":default": { # Default state
                        "shape": {
                            "type": "rect", 
                            "pos": "$[widget.pos]", 
                            "size": "$[widget.size]", 
                            }, 
                        "background": {
                            "type": "color", 
                            "color": (200, 200, 200), 
                            }, 
                        "border_width": 2, 
                        "border_texture": {
                            "type": "color", 
                            "color": (20, 20, 20)
                            }, 
                        "text_style": {
                            "font": None, 
                            "size": None, 
                            }, 
                        "text_texture": {
                            "type": "color", 
                            "color": (0, 0, 0), 
                            }, 
                        }, 
                    }, 
                *args, **kwargs):
        """Text buttons in Charmy.

        :param parent: Parent of the button
        :param text: Text shown on the button
        :param on_click: Function to execute when clicked
        :param styles: Styles of the button
        :param *args: → See `Widget.__init__(...)`
        :param **kwargs: → See `Widget.__init__(...)`
        """
        super().__init__(parent, style, *args, **kwargs)
        self.text: str = text
        self.on_click: typing.Callable = on_click
        self.style: dict[str, typing.Any] = style
        self.theme: typing.Optional[styles.theme.Theme] = None
        self.state: str = "normal"
        self._initialized = True

        # Drawn objects, used by internal drawing functions
        self._background_shape: graphics.DrawnShape

    def draw(self, 
            pos: styles.shape.Point, 
            size: typing.Optional[styles.shape.Size], 
            *args, **kwargs, 
            ) -> typing.Self:
        """Draw the button."""
        # Fill vars to style
        style_vars = (
            self.theme, 
            self.root_container, 
            self
            )
        style_state = ':' + (self.state if self.state in self.style.keys() else "default")
        curr_style = styles.style.fill_vars(self.style[style_state], *style_vars)
        # Widget.draw
        Widget.draw(self, pos, size, *args, **kwargs)
        # Background shape
        self._background_shape.offset = self.pos
        self._background_shape.shape = self.style["shape"]
        self._background_shape.draw
        return self

    def _update_draw_list(self):
        """Update draw list of a button, for internal use only."""
        super()._update_draw_list()
        # Fill vars to style
        style_vars = (
            self.theme, 
            self.root_container, 
            self
            )
        style_state = ':' + (self.state if self.state in self.style.keys() else "default")
        curr_style = styles.style.fill_vars(self.style[style_state], *style_vars)
        # Make draw objects
        self._draw_list.append(
            graphics.DrawnShape(
                styles.shape.AnyShape.from_json(curr_style["shape"]), 
                styles.texture.Texture.from_json(curr_style["background"]), 
                curr_style["border_width"], 
                styles.texture.Texture.from_json(curr_style["border_texture"]), 
                offset=self.pos, 
                )
            )
        self._draw_list.append(graphics.DrawnText(
            self.text, 
            styles.text_style.TextStyle.from_json(curr_style["text_style"]), 
            styles.texture.Texture.from_json(curr_style["text_texture"]), 
            (self.x + (self.width - self._draw_list) // 2, 0), 
            ))
