"""Caching module for caching data that are not frequently changed."""

import typing as _typing

from dataclasses import dataclass as _dataclass

from . import var as _var


def custom_cached_property(func, rule_func: _typing.Callable) -> property:
    """Decorator for cached data with their dirty state defined by a callable.

    Notes on Param `rule_func`
    --------------------------
    The value of this should ba a callable, including function or lambda expression etc. The 
    callable should implement the caching rule for the property. The callable should return `True` 
    when the property's cache is dirty, and otherwise return `False`.

    :param rule_func: A callable that implements the caching rule
    """

    @property
    def wrapper(self):
        if rule_func():
            return func(self)
        else:
            return NotImplemented

    return wrapper
