"""Caching module for caching data that are not frequently changed."""

import typing as _typing


raise NotImplementedError(
    "THIS FUCKING CACHING MODULE IS NOT IMPLEMENTED BECAUSE I DON'T HAVE ANY FUCKING IDEA ON THIS. "
    "IF YOU FIND THE GUI TOO SLOW, THEN FUCK YOUR WALLET TO GET A NEW COMPUTER OR CONTRIBUTE YOUR "
    "SOLUTION TO THE PROJECT."
    )


# This module is supposed to be used to cache some properties that are frequently used, but not 
# frequently changed. I designed it to be some kinda decorators lying on top of some properties, 
# but got no idea to implement.


class CachedClass():
    """Caching ability of a class"""

    def __init_subclass__(cls) -> None:
        cls._cached_list: dict[_typing.Callable, list | _typing.Literal["all"]] = {}
        cls._cache_dirty_state: dict[_typing.Callable, bool] = {}

    @classmethod
    def _cached_property(
        cls, 
        func: _typing.Callable, 
        watched_attrs: list[str] | _typing.Literal["all"]
        ):
        cls._cached_list[func] = watched_attrs
        cls._cache_dirty_state[func] = False

        @property
        def wrapper(self):
            pass