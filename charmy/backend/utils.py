"""Utils for backend, provide a safe way to reference Charmy objects for backends.

This module imports limited parts of Charmy and provide it to backends, allowing backends 
referencing Charmy objects while less likely to trigger circular import errors.
"""

from .. import styles
from .. import graphics
from ..utils import event_types