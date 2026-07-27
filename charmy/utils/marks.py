"""Marks that are used to represent a meaning with a specific data type."""

import typing as _typing


class Mark:
    """A class use to represent a mark.
    A mark is used to represent some meaning with a specific Mark data type, so it will not be 
    mistaken with other meanings.
    """
    def __init__(self, means: str = "nothing"):
        self.meaning = means
        self.payload: list[_typing.Any] = []

profile_value_fallback_mark = Mark("profile_value_fallback")

def profile_var(item: str):
    """"""
    mark = Mark("profile_var")
    mark.payload.append(item)
    return mark