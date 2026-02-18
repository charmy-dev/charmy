from .object import CharmyObject


class Size(CharmyObject):
    """Size is a class to store size.

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
        self.width = width
        self.height = height

    def __call__(self, width: int | float | None = None, height: int | float | None = None):
        if width:
            self.width = width
        if height:
            self.height = height

    def __str__(self):
        return f"Size({self.get('width')}, {self.get('height')})"

size = Size(300, 400)

print(size)