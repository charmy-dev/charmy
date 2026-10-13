"""Marks that are used to represent a meaning with a specific data type."""

import typing as _typing


class Mark:
    """A class use to represent a mark.
    A mark is used to represent some meaning with a specific Mark data type, so it will not be 
    mistaken with other meanings.
    """
    def __init__(self, means: str = "nothing", payload: _typing.Optional[list] = None):
        self.meaning = means
        if payload is None:
            payload = []
        self.payload: list[_typing.Any] = payload

profile_value_fallback_mark = Mark("profile_value_fallback")
profile_fallback_unspecified_mark = Mark("profile_fallback_unspecified")
profile_fallback_root_mark = Mark("profile_fallback_root")

def profile_fallback_widget_state_mark(state: str):
    """Profile refs var."""
    mark = Mark("profile_fallback_widget_state")
    mark.payload.append(state)
    return mark