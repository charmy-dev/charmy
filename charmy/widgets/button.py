from __future__ import annotations

import typing

from .widget import Widget
from .. import styles


class TextButton(Widget):
    """Text button in Charmy."""

    def __init__(self, 
                text: str, 
                on_click: typing.Callable = lambda: None, 
                *args, **kwargs):
        """Text button in Charmy.

        Text buttons are buttons that 
        """
        super().__init__(*args, **kwargs)
        self.text: str = text
        self.on_click: typing.Callable = lambda: None

    def draw(self, 
            pos: styles.shape.Point, 
            size: typing.Optional[styles.shape.Size], 
            *args, **kwargs, 
            ):
        Widget.draw(self, pos, size) # Set self size and run extensive drawings
        # self.
