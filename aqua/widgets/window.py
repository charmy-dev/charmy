from .container import AqContainer
from .windowbase import AqWindowBase


class AqWindow(AqWindowBase, AqContainer):
    def __init__(self, *args, **kwargs):
        AqWindowBase.__init__(self, *args, **kwargs)
