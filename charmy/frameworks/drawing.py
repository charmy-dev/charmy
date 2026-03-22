import importlib.util
from abc import ABC, abstractmethod

from ..rect import Rect


# region Drawing
class DrawingFramework(ABC):
    """The base class of DrawingFramework."""

    @abstractmethod
    def draw_rect(self, canvas, rect: Rect, radius: int = 0, bg=None, bd=None):
        """Draw a rectangle

        Args:
            canvas (Canvas): The canvas to draw
            rect (Rect): The rect area to draw
            radius (int, optional): The radius of the rectangle. Defaults to 0.
            bg (charmy.styles.color.Color, optional): The background color of the rectangle. Defaults to None.
            bd (charmy.styles.color.Color, optional): The border color of the rectangle. Defaults to None.
        """
        ...


drawing_framework_map = {}


class SKIA(DrawingFramework):
    def __init__(self):
        self.skia = importlib.import_module("skia")

    def draw_rect(self, canvas, rect: Rect, radius: int | float = 8, bg=None, bd=None):  # noqa
        # from skia import RRect, Rect, Canvas, Paint
        # Paint()
        # canvas: Canvas

        if bg is None:
            bg = {}
        canvas.drawRoundRect(
            rect=self.skia.Rect.MakeXYWH(rect.x, rect.y, rect.width, rect.height),
            rx=radius,
            ry=radius,
            paint=self.skia.Paint(
                Color=bg.get("color_object", self.skia.ColorBLACK),
                Style=self.skia.Paint.kFill_Style,
            ),
        )


if importlib.util.find_spec("skia") is not None:
    drawing_framework_map["SKIA"] = SKIA  # NOQA

# endregion
