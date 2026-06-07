"""Caching module for caching data that are not frequently changed."""

# import typing as _typing

import reactive_caching


class CharmyCachedClass(reactive_caching.CachedClass):
    """Charmy cached class, with event bind

    Must set `self._cache_initialized` to `True` after `__init__()`
    """

    def __init__(self):
        reactive_caching.CachedClass.__init__(self)
