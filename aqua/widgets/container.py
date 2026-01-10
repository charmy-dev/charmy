from ..object import AqObject


class AqContainer(AqObject):
    def __init__(self):
        super().__init__()

        self.new("children", [])
