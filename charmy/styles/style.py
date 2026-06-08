from __future__ import annotations as _

import typing as _typing

import re as _re

if _typing.TYPE_CHECKING:
    import charmy as cm


class DEBUG_FLAGS:
    FILL_VARS_DEBUG_OUTPUT: bool = False


StyleType: _typing.TypeAlias = dict[str, _typing.Any]


def fill_vars(style_value: _typing.Any, 
            theme: _typing.Optional[cm.styles.theme.Theme] = None, 
            window: _typing.Optional[cm.window.WindowEntity | cm.widgets.Container] = None, 
            widget: _typing.Optional[cm.Widget] = None, 
            ) -> _typing.Any:
    """To replace vars in a style value.

    :param style_value: The style value containing the var
    :param theme: Theme currently used
    :param window: Current window
    :param widget: Current widget
    """
    if isinstance(style_value, str):
        requested_vars = _re.findall("\\$\\[.*?\\]", style_value)
        if DEBUG_FLAGS.FILL_VARS_DEBUG_OUTPUT:
            print(f"{style_value=} | {requested_vars=}")
        if len(requested_vars) == 0: # If no vars requested
            # Return original value
            return style_value
        elif len(requested_vars) == 1: # If only 1 var requested, return the value of it
            if DEBUG_FLAGS.FILL_VARS_DEBUG_OUTPUT:
                print(f"{requested_vars[0]} -> {eval(requested_vars[0][2:-1])}")
            return eval(requested_vars[0][2:-1])
            # TODO: Refactor styles system and avoid unsafe eval() like this
        else:
            result = style_value
            for var in requested_vars:
                result = result.replace(var, eval(var[2:-1]))
        # return style_value.format(
        #     theme=theme, 
        #     window=window, 
        #     widget=widget, 
        #     )
    elif isinstance(style_value, dict):
        result = style_value.copy()
        for item in result.keys():
            result[item] = fill_vars(style_value[item], theme, window, widget)
        return result
    else:
        return style_value