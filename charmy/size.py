from .object import CharmyObject


class Size(CharmyObject):
    """CSize is a class to store size.

    To reset the size, use the __call__ method.

    Example:
        >>> size = Size(100, 200)
        >>> print(size)  # CSize(100, 200)
        >>> size(300, 400)  # or size.__call__(300, 400)
        >>> print(size)  # CSize(300, 400)
    ```
    """

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
