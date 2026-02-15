import typing
import threading
import functools

from ..object import CharmyObject


class Container(CharmyObject):
    """CContainer is a class to store child objects"""

    _local = threading.local()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new("children", [])

    # region Context

    @classmethod
    def _get_context_stack(cls) -> typing.List['Container']:
        """Get the context stack of the current thread"""
        if not hasattr(cls._local, 'context_stack'):
            cls._local.context_stack = []
        return cls._local.context_stack
    
    @classmethod
    def get_context(cls) -> typing.Optional['Container']:
        """Get the current context container"""
        stack = cls._get_context_stack()
        return stack[-1] if stack else None

    def __enter__(self) -> 'Container':
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

    def add_child(self, child: 'CharmyObject'):
        """Add a child object"""
        if child not in self["children"]:
            self["children"].append(child)

    # endregion


def auto_find_parent(widget_class: typing.Callable) -> typing.Callable:
    """Add a decorator to automatically inject the parent container to the widget constructor"""

    # Save the original constructor
    original_init = widget_class.__init__  # NOQA

    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        # Check if parent is specified in keyword arguments
        parent_specified = False

        # Check if parent is specified in keyword arguments
        if 'parent' in kwargs:
            parent_specified = True
        # Check if parent is specified in positional arguments
        elif len(args) >= 2:
            parent_specified = True

        # If parent is not specified, try to get it from context
        if not parent_specified:
            parent = Container.get_context()
            if parent is not None:
                kwargs['parent'] = parent

        # Call the original constructor
        original_init(self, *args, **kwargs)

    # Replace the constructor
    widget_class.__init__ = new_init
    return widget_class