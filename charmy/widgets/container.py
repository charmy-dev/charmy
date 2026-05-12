"""The container base class."""

import threading
import typing

from ..object import CharmyObject


class Container:
    """Container represents a widget's ability to contain and arrange other widgets inside.

    The `Container` class contains the ability of managing widgets within the container, and should 
    be inherited by all types of containers including windows, frames, etc., but not supposed to be 
    instantiated directly.

    What is a Root Container?
    -------------------------
    A root container is a `Container` object (which allows containing other widgets inside) that 
    operates backend modules to serve items within it. Root containers are marked with class 
    property `is_root_container`.
    """

    is_root_container: typing.ClassVar[bool] = False # Flags if the container is a root container

    _local = threading.local()

    def __init__(self, *args, **kwargs):
        """Initialize a container base class.

        The container base class is not supposed to be instantiated directly, make sure you are 
        executing this method during subclassing.
        """
        super().__init__(*args, **kwargs)

        self.children = []

    def __post_init__(self):
        """Validates self status. Not supposed to be called from outside."""
        if True in [
            self.is_root_container and hasattr(self, "parent"), 
            not self.is_root_container and not hasattr(self, "parent"), 
            not self.is_root_container and not hasattr(self, "root_container"), 
            ]:
            raise RuntimeError(
                "A container must either be a root continer, or has a parent and contained within "
                "a root container."
                )

    @property
    def rect(self):
        """Get the container's rect."""
        return (0, 0), (0, 0)

    # region Context

    @classmethod
    def _get_context_stack(cls) -> typing.List["Container"]:
        """Get the context stack of the current thread"""
        if not hasattr(cls._local, "context_stack"):
            cls._local.context_stack = []
        return cls._local.context_stack

    @classmethod
    def get_context(cls) -> typing.Optional["Container"]:
        """Get the current context container"""
        stack = cls._get_context_stack()
        return stack[-1] if stack else None

    def __enter__(self) -> "Container":
        """Enter the context"""
        stack = self._get_context_stack()
        stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context"""
        stack = self._get_context_stack()
        if stack and stack[-1] is self:
            stack.pop()
        return False  # 不抑制异常

    def add_child(self, child: "CharmyObject"):
        """Add a child object"""
        if child not in self.children:
            self.children.append(child)

    def draw_children(self, canvas):
        """Draw the container and its children"""
        for child in self.children:
            if hasattr(child, "draw"):
                child.draw(canvas)

    # endregion