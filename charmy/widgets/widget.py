import typing

from ..object import CObject
from .container import CContainer, auto_find_parent


@auto_find_parent
class CWidget(CObject):
    def __init__(self, parent: CContainer | None = None):
        super().__init__()

        self._parent = parent

        # 如果有父容器，添加到子部件列表
        if parent is not None:
            parent.add_child(self)

        print(f"创建 WidgetV2: {self.name}, parent={parent.name if parent else None}")

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
