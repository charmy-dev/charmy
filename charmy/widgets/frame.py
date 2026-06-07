"""Charmy Frame."""

from .container import Container as _Container
from .widget import Widget as _Widget


class Frame(_Widget, _Container):
    pass
