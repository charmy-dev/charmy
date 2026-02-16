from .canvas import CanvasBase
from .container import Container, auto_find_parent


@auto_find_parent
class Widget(CanvasBase):
    """Basic widget class."""

    def __init__(self, parent: Container | None = None):
        super().__init__()

        if parent is None:
            parent = self.find("window0", default=None)

        self.new("parent", parent)

        # Automatically add to parent's children list if parent exists
        if parent is not None:
            parent.add_child(self)
