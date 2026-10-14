"""Marks that are used to represent a meaning with a specific data type."""

from __future__ import annotations

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

    def __str__(self) -> str:
        return f"CM_Mark:{self.meaning}{tuple(self.payload)}"

    # def __eq__(self, other: Mark) -> bool:
    #     if other.meaning != self.meaning:
    #         return False
    #     if len(self.payload) != len(other.payload):
    #         return False
    #     if len(self.payload) == 0 or len(other.payload) == 0:
    #         return False
    #     for index, item in enumerate(self.payload):
    #         if item != other.payload[index]:
    #             return False
    #     return True

profile_value_fallback_mark = Mark("profile_value_fallback")
profile_fallback_unspecified_mark = Mark("profile_fallback_unspecified")
profile_fallback_root_mark = Mark("profile_fallback_root")

def profile_fallback_widget_state_mark(state: str):
    """Profile refs var."""
    mark = Mark("profile_fallback_widget_state")
    mark.payload.append(state)
    return mark