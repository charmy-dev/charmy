"""Misc of misc."""

class Mark:
    """A class use to represent a mark.
    A mark is used to represent some meaning with a specific Mark data type, so it will not be 
    mistaken with other meanings.
    """
    def __init__(self, means: str = "nothing"):
        self.meaning = means

profile_value_fallback_mark = Mark("profile_value_fallback")