import typing
import warnings

from ..const import ID, MANAGER_ID
from ..object import CharmyObject
from ..rect import Rect
from .cmm import CharmyManager


class CanvasBase(CharmyObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Auto find CharmyManager Object
        manager = self.get_obj(MANAGER_ID)
        if manager is None:
            raise ValueError("Not found main CharmyManager")
        self.manager: CharmyManager = manager
        self.new(
            "framework",
            self._get_framework(),
            get_func=self._get_framework,
        )
        # element config
        self.elements = []  # e.g. [{"type": "rect", "id": "element0", "radius": 12}]
        self.draw_type_map: dict[str, typing.Callable[[dict, dict], None]] = {
            "rect": self.draw_rect,
        }  # 元素绘制映射表
        self.new("color_object", None)
        self._last_count = 0

    def draw(self, canvas):
        """Draw the widget"""
        for element in self.elements:
            if element["type"] in self.draw_type_map:
                self.draw_type_map[element["type"]](canvas, element)
            else:
                warnings.warn(f"Warning: Unknown element type {element['type']}")

    def draw_rect(self, canvas, element: dict):
        self["framework"].drawing.draw_rect(
            canvas,
            rect=element.get("rect"),
            radius=element.get("radius", 0),
            bg=element.get("bg", None),
        )

    def _template(self, type_: str, rect: Rect, id_: ID = ID.AUTO, **kwargs):
        """Create a new element.

        Args:
            type_ (str): Element type
            rect (Rect): Element position and size
            id_ (ID, optional): Element ID. Defaults to ID.AUTO.

        Returns:
            dict: Element config dict
        """
        if id_ == ID.AUTO:
            id_ = f"element{self._last_count}"

        self._last_count += 1

        return {"type": type_, "rect": rect, "id": id_, **kwargs}

    # region Element config

    def add_element(self, type_: str, rect: Rect, **kwargs):
        self.elements.append(self._template(type_, rect, **kwargs))

    def insert_element(self, index: int, type_: str, rect: Rect, **kwargs):
        self.elements.insert(index, self._template(type_, rect, **kwargs))

    def remove_element(self, index: int):
        self.elements.remove(index)

    def find_element(self, id_: ID) -> dict | None:
        for element in self.elements:
            if element["id"] == id_:
                return element
        return None

    get_element = find_element

    def _get_framework(self):
        return self.manager["framework"]
