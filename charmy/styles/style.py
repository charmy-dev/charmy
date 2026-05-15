from __future__ import annotations as _

import typing

if typing.TYPE_CHECKING:
    import charmy as cm


StyleType: typing.TypeAlias = dict[str, typing.Any]


def fill_vars(style_value: typing.Any, 
            theme: typing.Optional[cm.styles.theme.Theme] = None, 
            window: typing.Optional[cm.window.WindowEntity | cm.widgets.Container] = None, 
            widget: typing.Optional[cm.Widget] = None, 
            ) -> typing.Any:
    """To replace vars in a style value.

    :param style_value: The style value containing the var
    :param theme: Theme currently used
    :param backend: Backend currently used
    :param window: Current window
    :param widget: Current widget
    """
    if isinstance(style_value, str):
        return style_value.format(
            theme=theme, 
            window=window, 
            widget=widget, 
            )
    else:
        return style_value