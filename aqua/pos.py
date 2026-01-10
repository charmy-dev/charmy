from .object import AqObject


class AqPos(AqObject):
    def __init__(self, x=0, y=0):
        super().__init__()
        self.new("x", x)
        self.new("y", y)
