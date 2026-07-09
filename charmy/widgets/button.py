"""Charmy button."""

from __future__ import annotations as _

import typing as _typing

import reactive_caching

from .widget import Widget as _Widget
from .. import styles as _styles
from .. import event_types as _event_types
from .. import graphics as _graphics

if _typing.TYPE_CHECKING:
    from .. import container as _container


button_default_style: dict[str, _typing.Any] = {
    # Default button style (bootstrap)
    # These styles JSON might be moved to somewhere else in the future...
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
            "color": (20, 20, 20), 
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
    ":hover": { # Hovering
        "background": {
            "type": "color", 
            "color": (0, 0, 0)
            }, 
        "text_texture": {
            "type": "color", 
            "color": (255, 255, 255), 
            }, 
        }, 
    }


class Button(_Widget):
    """Text buttons in Charmy."""

    def __init__(self, 
                parent: _container.Container | None = None, 
                text: str = "Button", 
                on_click: _typing.Callable = lambda: None, 
                style: _typing.Optional[dict[str, _typing.Any]] = None, 
                *args, **kwargs):
        """Text buttons in Charmy.

        :param parent: Parent of the button
        :param text: Text shown on the button
        :param on_click: Function to execute when clicked
        :param styles: Styles of the button
        :param *args: → See `Widget.__init__(...)`
        :param **kwargs: → See `Widget.__init__(...)`
        """
        if style is None:
            style = button_default_style
        super().__init__(parent, style)
        self.text: str = text
        self.on_click: _typing.Callable = on_click
        self.style: dict[str, _typing.Any] = style.copy()
        self.theme: _typing.Optional[_styles.theme.Theme] = None
        self.state: str = "normal"

        # Drawn objects, used by internal drawing functions
        self._components: tuple[_graphics.DrawnShape, _graphics.DrawnText] = (
            _graphics.DrawnShape(
                self.root_container, 
                _styles.shape.Rect((0, 0), (0, 0)), 
                None
                ), 
            _graphics.DrawnText(
                self.root_container, 
                self.text, _styles.text_style.TextStyle.sys_default, 
                None
                ), 
            )

        # Internal event binds
        self.bind(
            _event_types.MouseClick, 
            lambda _: self.on_click(), {"button": 0}, _is_internal=True
            )
        self.bind(
            _event_types.MouseEnter, 
            lambda _: self.config(state="hover"), _is_internal=True
            )
        self.bind(
            _event_types.MouseLeave, 
            lambda _: self.config(state="normal"), _is_internal=True
            )

    @reactive_caching.cached_property("-exposed-")
    # BUG of reactive_caching: cannot listen change in properties
    def components(self) -> _typing.Tuple[_graphics.DrawnObject, ...]:
        """Components (drawn objects) that make up the button."""
        state=self.state
        self.state="default"
        curr_style = self.curr_state_styles.copy()
        self.state=state
        curr_style.update(self.curr_state_styles)
        # Make background shape
        self._components[0].shape = \
            _styles.shape.AnyShape.from_json(curr_style["shape"])
        self._components[0].texture = \
            _styles.texture.Texture.from_json(curr_style["background"])
        self._components[0].border_width = \
            curr_style["border_width"]
        self._components[0].border_texture = \
            _styles.texture.Texture.from_json(curr_style["border_texture"])
        self._components[0].offset = \
            self.abs_pos
        # Drawn text
        self._components[1].text = \
            self.text
        self._components[1].style = \
            _styles.text_style.TextStyle.from_json(curr_style["text_style"])
        self._components[1].texture = \
            _styles.texture.Texture.from_json(curr_style["text_texture"])
        self._components[1].offset = \
            (self.abs_pos[0] + ((self.width - self._components[1].boundary[1][0]) // 2), 
             self.abs_pos[1] + ((self.height - self._components[1].boundary[1][1]) // 2))
        return self._components