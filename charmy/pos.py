from .object import CObject


class CPos(CObject):
    """CPos is a class to store position"""

    def __init__(self, x=0, y=0):
        super().__init__()
        self.new("x", x)
        self.new("y", y)

    def __call__(self, x: int | float | None = None, y: int | float | None = None):
        if x:
            self.set("x", x)
        if y:
            self.set("y", y)

    def __str__(self):
        return f"CPos({self.get('x')}, {self.get('y')})"
