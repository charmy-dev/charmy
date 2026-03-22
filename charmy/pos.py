from .object import CharmyObject


class Pos(CharmyObject):
    """Pos is a class to store position."""

    def __init__(self, x=0, y=0):
        super().__init__()
        self.x: int | float = x
        self.y: int | float = y

    def __call__(self, x: int | float | None = None, y: int | float | None = None):
        if x:
            self.set("x", x)
        if y:
            self.set("y", y)

    def __str__(self):
        """Return position in string."""
        return f"Pos({self.get('x')}, {self.get('y')})"
