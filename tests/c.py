from contextlib import contextmanager
from typing import Optional, Callable, Any, List
import functools
import threading


class ContainerV2:
    """容器类V2：修复版"""

    # 使用线程局部存储
    _local = threading.local()

    def __init__(self, name: str = None):
        self.name = name or f"ContainerV2_{id(self)}"
        self.children: List[WidgetV2] = []

    @classmethod
    def _get_context_stack(cls) -> List['ContainerV2']:
        """获取当前线程的上下文栈"""
        if not hasattr(cls._local, 'context_stack'):
            cls._local.context_stack = []
        return cls._local.context_stack

    @classmethod
    def get_context(cls) -> Optional['ContainerV2']:
        """获取当前上下文容器"""
        stack = cls._get_context_stack()
        return stack[-1] if stack else None

    def __enter__(self) -> 'ContainerV2':
        """进入上下文"""
        stack = self._get_context_stack()
        stack.append(self)
        print(f"进入 ContainerV2: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        stack = self._get_context_stack()
        if stack and stack[-1] is self:
            stack.pop()
        print(f"退出 ContainerV2: {self.name}")
        return False  # 不抑制异常

    def add_child(self, child: 'WidgetV2'):
        """添加子部件"""
        if child not in self.children:
            self.children.append(child)
            print(f"ContainerV2 {self.name} 添加 {child.name}")


def auto_parent(widget_class: Callable) -> Callable:
    """装饰器：自动注入父容器到部件构造函数"""

    # 保存原始构造函数
    original_init = widget_class.__init__

    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        # 检查是否传入了parent参数
        parent_specified = False

        # 检查关键字参数
        if 'parent' in kwargs:
            parent_specified = True
        # 检查位置参数（假设parent是第二个位置参数）
        elif len(args) >= 2:
            parent_specified = True

        # 如果没有指定parent，尝试从上下文获取
        if not parent_specified:
            parent = ContainerV2.get_context()
            if parent is not None:
                kwargs['parent'] = parent

        # 调用原始构造函数
        original_init(self, *args, **kwargs)

    # 替换构造函数
    widget_class.__init__ = new_init
    return widget_class


@auto_parent
class WidgetV2:
    def __init__(self, name: str, parent: Optional[ContainerV2] = None):
        self.name = name
        self._parent = parent

        # 如果有父容器，添加到子部件列表
        if parent is not None:
            parent.add_child(self)

        print(f"创建 WidgetV2: {self.name}, parent={parent.name if parent else None}")

    @property
    def parent(self) -> Optional[ContainerV2]:
        return self._parent

    @parent.setter
    def parent(self, value: ContainerV2):
        self._parent = value


# 使用示例
print("=== 修复后的装饰器方案 ===")

with ContainerV2("装饰器容器") as c:
    w1 = WidgetV2("装饰器部件1")
    w2 = WidgetV2("装饰器部件2")

    print(f"容器 {c.name} 的子部件: {[w.name for w in c.children]}")

print("\n=== 嵌套容器测试 ===")

with ContainerV2("外层容器") as outer:
    w1 = WidgetV2("外层部件")

    with ContainerV2("内层容器") as inner:
        w2 = WidgetV2("内层部件")
        w3 = WidgetV2("另一个内层部件")

        print(f"内层容器 {inner.name} 的子部件: {[w.name for w in inner.children]}")

    w4 = WidgetV2("回到外层后的部件")

    print(f"外层容器 {outer.name} 的子部件: {[w.name for w in outer.children]}")

print("\n=== 显式指定parent测试 ===")

c1 = ContainerV2("独立容器")
# 显式指定parent
w1 = WidgetV2("独立部件1", parent=c1)
# 不指定parent，也没有上下文
w2 = WidgetV2("独立部件2")

print(f"独立容器 {c1.name} 的子部件: {[w.name for w in c1.children]}")
print(f"独立部件2的parent: {w2.parent}")
