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
                parent: container.Container | None = None, 
                text: str = "Button", 
                on_click: typing.Callable = lambda: None, 
                style: dict[str, typing.Any] = {
                    # Default button style (bootstrap)
                    # These styles JSON might be moved to somewhere else in future...
                    ":default": { # Default state
                        "size": (72, 28), 
                        "shape": {
                            "type": "rect", 
                            "pos": (0, 0), 
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
        super().__init__(parent, style)
        self.text: str = text
        self.on_click: typing.Callable = on_click
        self.style: dict[str, typing.Any] = style
        self.theme: typing.Optional[styles.theme.Theme] = None
        self.state: str = "normal"

        # Drawn objects, used by internal drawing functions
        self._drawn_background_shape: graphics.DrawnShape = \
            graphics.DrawnShape(styles.shape.Rect((0, 0), (0, 0)), None)
        self._drawn_text: graphics.DrawnText = \
            graphics.DrawnText(self.text, styles.text_style.TextStyle.sys_default, None)

        self._update_drawing_objects()

    def draw_components(self, *args, **kwargs) -> typing.Self:
        """Draw the button."""
        self._drawn_background_shape.draw(self.root_container)
        self._drawn_text.draw(self.root_container)
        return self

    def _update_drawing_objects(self):
        """Update draw list of a button, for internal use only."""
        curr_style = self.curr_state_styles
        # Make background shape
        self._drawn_background_shape.shape = \
            styles.shape.AnyShape.from_json(curr_style["shape"])
        self._drawn_background_shape.texture = \
            styles.texture.Texture.from_json(curr_style["background"])
        self._drawn_background_shape.border_width = \
            curr_style["border_width"]
        self._drawn_background_shape.border_texture = \
            styles.texture.Texture.from_json(curr_style["border_texture"])
        self._drawn_background_shape.offset = \
            self.pos # TODO: Support parent container offset
        # Drawn text
        self._drawn_text.text = \
            self.text
        self._drawn_text.style = \
            styles.text_style.TextStyle.from_json(curr_style["text_style"])
        self._drawn_text.texture = \
            styles.texture.Texture.from_json(curr_style["text_texture"])
        self._drawn_text.offset = \
            (self.x + ((self.width - self._drawn_text.boundary[1][0]) // 2), 
             self.y + ((self.height - self._drawn_text.boundary[1][1]) // 2))
        # TODO: Support parent container offset