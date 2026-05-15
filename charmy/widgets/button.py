from __future__ import annotations

import typing

from .widget import Widget
from .window import Window
from .. import styles
from .. import graphics

if typing.TYPE_CHECKING:
    from .. import container


class TextButton(Widget):
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
                            "pos": "{widget.pos}", 
                            "size": "{widget.size}", 
                            }, 
                        "background": {
                            "type": "color", 
                            "color": (150, 150, 150), 
                            }, 
                        "border_width": 2, 
                        "border_texture": {
                            "type": "color", 
                            "color": (20, 20, 20)
                            }, 
                        }, 
                        "text_style": {
                            }, 
                        "text_texture": {
                            "type": "color", 
                            "color": (0, 0, 0), 
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

    def _update_draw_list(self):
        """Update draw list of a button, for internal use only."""
        super()._update_draw_list()
        style_vars = (
            self.theme, 
            self.root_container, 
            self
            )
        # Background
        bg_shape = styles.shape.AnyShape.from_json(
            styles.style.fill_vars(self.style["shape"], *style_vars)
            )
        bg_texture = styles.texture.Texture.from_json(
            styles.style.fill_vars(self.style["background"], *style_vars)
            )
        bd_width = styles.style.fill_vars(self.style["border_width"], *style_vars)
        bd_texture = styles.texture.Texture.from_json(
            styles.style.fill_vars(self.style["border_texture"], *style_vars)
            )
        self._draw_list.append(
            graphics.DrawnShape(bg_shape, bg_texture, bd_width, bd_texture, offset=self.pos)
            )
        # Text
        text_style = styles.text_style.TextStyle.from_json(
            styles.style.fill_vars(self.style["text_texture"], *style_vars)
            )
        text_texture = styles.texture.Texture.from_json(
            styles.style.fill_vars(self.style["text_texture"], *style_vars)
            )
        self._draw_list.append(
            graphics.DrawnText(self.text, text_style, (0, 0))
            )
