from ..object import CObject


class CContainer(CObject):
    """CContainer is a class to store child objects"""
    def __init__(self):
        super().__init__()

        self.new("children", [])
