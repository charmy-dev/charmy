import importlib

from ..const import MAINAPP_ID, DrawingFrame
from ..object import CharmyObject
from ..widgets.app import App


class Color(CharmyObject):
    """Color manager"""

    def __init__(self, *args, draw_framework: DrawingFrame = None, **kwargs):
        super().__init__(*args, **kwargs)

        # The Drawing Framework
        if draw_framework is None:
            # Auto find CApp Object
            app = self.get_obj(MAINAPP_ID)
            if app is None:
                raise ValueError("Not found main App")
            self.app: App = app
            self.new(
                "drawing.framework",
                self._get_drawing_framework(),
                get_func=self._get_drawing_framework,
            )
        else:
            self.new("drawing.framework", draw_framework)

        # Import Drawing Framework
        match self["drawing.framework"]:
            case DrawingFrame.SKIA:
                self.skia = self.app.skia
            case _:
                raise ValueError("Not supported drawing framework")

    def set_color_rgba(
        self, r: int | float, g: int | float, b: int | float, a: int | float = 255
    ) -> None:
        """set_rgba(r=255, g=255, b=255, a=255) or set_rgba(r=1.0, g=1.0, b=1.0, a=1.0)

        Args:
            r (int | float): The red component of the color.
            g (int | float): The green component of the color.
            b (int | float): The blue component of the color.
            a (int | float): The alpha component of the color.

        Returns:
            None
        """
        match self["drawing.framework"]:
            case DrawingFrame.SKIA:
                self["color_object"] = self.skia.Color(
                    self._c(r), self._c(g), self._c(b), self._c(a)
                )

    def set_color_hex(self, _hex: str) -> None:
        """
        Convert hex color string to color.

        Args:
            _hex (str): Hex color string (support #RRGGBB and #RRGGBBAA format)

        Returns:
            skia.Color: Corresponding RGBA color object

        Raises:
            ValueError: When hex color format is invalid
        """
        hex_color = _hex.lstrip("#")
        if len(hex_color) == 6:  # RGB 格式，默认不透明(Alpha=255)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            match self["drawing.framework"]:
                case DrawingFrame.SKIA:
                    self["color_object"] = self.skia.ColorSetRGB(r, g, b)  # 返回不透明颜色
        elif len(hex_color) == 8:  # RGBA 格式(含 Alpha 通道)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = int(hex_color[6:8], 16)
            match self["drawing.framework"]:
                case DrawingFrame.SKIA:
                    self["color_object"] = self.skia.ColorSetARGB(a, r, g, b)  # 返回含透明度的颜色
        else:
            raise ValueError("HEX Should be #RRGGBB or #RRGGBBAA format")

    def set_color_name(self, name: str) -> None:
        """Convert color name string to color.

        Args:
            name (str): Color name
        Returns:
            skia.Color: Corresponding RGBA color object
        Raises:
            ValueError: When color not exists
        """
        match self["drawing.framework"]:
            case DrawingFrame.SKIA:
                try:
                    self["color_object"] = getattr(self.skia, f"Color{name.upper()}")
                except:
                    raise ValueError(f"Unknown color name: {name}")

    @staticmethod
    def _c(x):
        """Convert float color component to int.

        Args:
            x (int | float): Color component value (0.0-1.0 or 0-255)

        Returns:
            int: Corresponding int value (0-255)
        """
        if isinstance(x, float):
            if 0 < x <= 1.0:
                x = x * 255
        return x

    def _get_drawing_framework(self):
        return self.app["drawing.framework"]
