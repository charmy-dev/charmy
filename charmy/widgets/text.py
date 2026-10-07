"""Charmy text."""

from __future__ import annotations as _

import typing as _typing
import dataclasses as _dataclasses

from .widget import Widget as _Widget, WidgetProfile as _WidgetProfile
from .. import styles as _styles
from .. import event_types as _event_types
from .. import graphics as _graphics
from ..utils import type_checking as _type_checking, marks as _marks, var as _var

if _typing.TYPE_CHECKING:
    from .. import container as _container


@_dataclasses.dataclass
class TextProfile(_WidgetProfile):
    """Text profile."""
    text_style: _type_checking.ProfileProp[dict | _styles.text_style.TextStyle] = \
        _marks.profile_value_fallback_mark
    text_texture: _type_checking.ProfileProp[dict | _styles.texture.TextureType] = \
        _marks.profile_value_fallback_mark

    @classmethod
    def default(cls) -> _typing.Self:
        instance = cls(
            size=(72, 28),
            text_style = _styles.text_style.TextStyle.sys_default,
            text_texture = _styles.texture.Color((0, 0, 0)),
            )
        return instance


class Text(_Widget):
    """Text labels in Charmy."""

    ProfileClass = TextProfile
    ProfileType = TextProfile

    def __init__(self,
            parent: _container.Container | None = None,
            text: str = "Text",
            *args, **kwargs):
        """Text labels in Charmy.

        :param parent: Parent of the label
        :param text: Text shown on the label
        :param on_click: Function to execute when clicked
        :param styles: Styles of the label
        :param *args: → See `Widget.__init__(...)`
        :param **kwargs: → See `Widget.__init__(...)`
        """
        super().__init__(parent, *args, **kwargs)
        self.text: str = text
        self.theme: _typing.Optional[_styles.theme.Theme] = None
        self.state: str = "normal"

        # Override profiles type
        self.profiles: _typing.Dict[str, TextProfile]

        # Drawn objects, used by internal drawing functions
        self._components: tuple[_graphics.DrawnText] = (
            _graphics.DrawnText(
                self.root_container,
                self.text, _styles.text_style.TextStyle.sys_default,
                None
                ),
            )

    def _update_components(self) -> _typing.Tuple[_graphics.DrawnObject, ...]:
        """Components (drawn objects) that make up the text."""
        # Generate a full profile for current state
        curr_profile = self.migrate_full_curr_profile()
        curr_profile = _typing.cast(TextProfile, curr_profile)
        curr_profile._query_widget = self
        # Drawn text
        self._components[0].text = \
            self.text
        self._components[0].style = \
            _styles.text_style.TextStyle.from_profile_value(curr_profile.text_style)
        self._components[0].texture = \
            _styles.texture.Texture.from_profile_value(curr_profile.text_texture)
        self._components[0].offset = \
            (self.abs_pos[0] + ((self.width - self._components[0].boundary[1][0]) // 2),
             self.abs_pos[1] + ((self.height - self._components[0].boundary[1][1]) // 2))
        return self._components