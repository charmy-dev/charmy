import typing
import warnings

from ..const import ID
from ..object import CharmyObject


class CanvasBase(CharmyObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.elements = []  # e.g. [{"type": "rect", "id": "element0", "radius": 12}]
        self.draw_type_map: dict[str, typing.Callable[[dict], None]] = {
            "rect": self.draw_rect,
        }
        self.new("")
        self._last_count = 0

    def draw(self):
        for element in self.elements:
            if element["type"] in self.draw_type_map:
                self.draw_type_map[element["type"]](element)
            else:
                warnings.warn(f"Warning: Unknown element type {element['type']}")

    def draw_rect(self, element: dict):
        pass

    def _template(self, type_: str, size: tuple[int, int], id_: ID = ID.AUTO, **kwargs):

        if id_ == ID.AUTO:
            id_ = f"element{self._last_count}"

        self._last_count += 1

        return {"type": type_, "size": size, "id": id_, **kwargs}

    # region Element config

    def add_element(self, type_: str, size: tuple[int, int], **kwargs):
        self.elements.append(self.template(type_, size, **kwargs))

    def insert_element(self, index: int, type_: str, size: tuple[int, int], **kwargs):
        self.elements.insert(index, self.template(type_, size, **kwargs))

    def remove_element(self, index: int):
        self.elements.remove(index)

    def find_element(self, id_: ID) -> dict | None:
        for element in self.elements:
            if element["id"] == id_:
                return element
        return None
