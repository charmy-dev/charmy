from .widget import Widget
from ..styles.color import Color

class Button(Widget):
    def __init__(self, *args, text: str = "", **kwargs):
        super().__init__(*args, **kwargs)

        self.text = text
        self._bg = Color().set_color_name("white")
        self._rect_id = self.add_element("rect", rect=self.rect, bg=self._bg)

    def draw_config(self, canvas):
        self.config_element(self._rect_id, rect=self.rect)
