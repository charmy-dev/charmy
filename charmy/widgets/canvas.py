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
        self.manager: CharmyManager = self.get_obj(MANAGER_ID)
        self._last_count = 0

        # element config
        # e.g. [{"type": "rect", "id": "element0", "radius": 12}]
        self.elements: list[dict] = []

        self.new(
            "framework",
            self._get_framework(),
            get_func=self._get_framework,
        )
        self.new("color_object", None)

        # 元素绘制映射表
        # TODO: 名字？难以理解感觉
        self.draw_type_map: dict[str, typing.Callable[[dict, dict], None]] = {
            "rect": self.draw_rect,
        }

    def draw_config(self, canvas):
        """Config elements' properties before `draw()`."""
        ...

    def draw(self, canvas):
        """Draw the widget"""
        self.draw_config(canvas)
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
        _ = self._template(type_, rect, **kwargs)
        self.elements.append(_)
        return _["id"]

    def insert_element(self, index: int, type_: str, rect: Rect, **kwargs):
        _ = self._template(type_, rect, **kwargs)
        self.elements.insert(index, _)
        return _["id"]

    def remove_element(self, index: int):
        self.elements.remove(index)

    def find_element(self, id_: ID) -> dict | None:
        for element in self.elements:
            if element["id"] == id_:
                return element
        return None

    get_element = find_element

    def config_element(self, id_: ID, **kwargs):
        element = self.find_element(id_)
        if element is None:
            raise ValueError(f"Not found element {id_}")
        element.update(kwargs)

    def _get_framework(self):
        return self.manager["framework"]
