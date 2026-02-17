from .object import CharmyObject


class Rect(CharmyObject):
    """Rect is a class to store the position and size of a rectangle.

    Args:
        **kwargs: The keyword arguments to initialize the rectangle.
            The keyword arguments are:
                x (int): The x coordinate of the top-left corner of the rectangle.
                y (int): The y coordinate of the top-left corner of the rectangle.
                width (int): The width of the rectangle.
                height (int): The height of the rectangle.
                left (int): The left coordinate of the top-left corner of the rectangle.
                top (int): The top coordinate of the top-left corner of the rectangle.
                right (int): The right coordinate of the top-left corner of the rectangle.
                bottom (int): The bottom coordinate of the top-left corner of the rectangle.
    """

    def __init__(self, **kwargs):
        super().__init__()
        # 基础四要素
        self.new("base_x", 0)
        self.new("base_y", 0)
        self.new("base_width", 0)
        self.new("base_height", 0)

        #
        self.new("top", 0, set_func=self._set_top, get_func=self._get_top)
        self.new("left", 0, set_func=self._set_left, get_func=self._get_left)
        self.new("bottom", 0, set_func=self._set_bottom, get_func=self._get_bottom)
        self.new("right", 0, set_func=self._set_right, get_func=self._get_right)
        self.new("x", 0, set_func=self._set_left, get_func=self._get_left)  # = left
        self.new("y", 0, set_func=self._set_top, get_func=self._get_top)  # = top
        self.new("width", 0, set_func=self._set_width, get_func=self._get_width)
        self.new("height", 0, set_func=self._set_height, get_func=self._get_height)
        self.__call__(**kwargs)

    def __call__(self, **kwargs):
        self.set("x", kwargs.get("x", 0))
        self.set("y", kwargs.get("y", 0))
        self.set("width", kwargs.get("width", 0))
        self.set("height", kwargs.get("height", 0))
        #############################################################
        self.set("left", kwargs.get("left", 0))
        self.set("top", kwargs.get("top", 0))
        self.set("right", kwargs.get("right", 0))
        self.set("bottom", kwargs.get("bottom", 0))

    def __str__(self):
        """Return position in string."""
        return f"Rect({self.get('left')}, {self.get('top')}, {self.get('width')}, {self.get('height')})"

    # region Attributes set/get
    def _set_left(self, x):
        self.set("base_x", x)

    def _get_left(self):
        return self.get("base_x")

    def _set_top(self, y):
        self.set("base_y", y)

    def _get_top(self):
        return self.get("base_y")

    def _set_right(self, x):
        self.set("base_width", x - self.get("base_x"))

    def _get_right(self):
        return self.get("base_x") + self.get("base_width")

    def _set_bottom(self, y):
        self.set("base_height", y - self.get("base_y"))

    def _get_bottom(self):
        return self.get("base_y") + self.get("base_height")

    def _set_width(self, w):
        self.set("base_width", w)

    def _get_width(self):
        return self.get("base_width")

    def _set_height(self, h):
        self.set("base_height", h)

    def _get_height(self):
        return self.get("base_height")

    # endregion
