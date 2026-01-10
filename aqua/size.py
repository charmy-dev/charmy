from .object import AqObject


class AqSize(AqObject):
    def __init__(self, width=0, height=0):
        super().__init__()
        self.new("width", width)
        self.new("height", height)