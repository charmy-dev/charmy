from .object import CObject


class CSize(CObject):
    """CSize is a class to store size"""

    def __init__(self, width=0, height=0):
        super().__init__()
        self.new("width", width)
        self.new("height", height)

    def __call__(self, width: int | float | None = None, height: int | float | None = None):
        if width:
            self.set("width", width)
        if height:
            self.set("height", height)

    def __str__(self):
        return f"CSize({self.get('width')}, {self.get('height')})"
