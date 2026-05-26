"""Charmy Frame."""

from .widget import Widget as _Widget
from .container import Container as _Container


class Frame(_Widget, _Container):
    pass