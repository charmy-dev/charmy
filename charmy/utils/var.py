"""Charmy vars.

This module contains Var and Query, which are used for referencing in Python.

Vars are used to implement thing like C(++) pointers. A var will be able to be referenced or
modified from somewhere else, providing experience like C(++) pointers.

Starting from commit 2708f2f, this module also provides a Query class for realtime referencing the
return value of a specific callable (like class properties, but may be used outside classes), with
an interface that is similar to Vars.
"""

import contextvars as _contextvars
import types as _types
import typing as _typing
from collections.abc import MutableMapping as _MutableMapping

from ..event import event_types, EventHandling


VarType = _typing.TypeVar("VarType")
_active_query_keys: _contextvars.ContextVar[frozenset[tuple[object, ...]]] = \
    _contextvars.ContextVar("active_query_keys", default=frozenset())

class Var(EventHandling, _typing.Generic[VarType]):
    """Aimed to provide experience like C vars with pointers."""

    def __init__(self, default_value: _typing.Optional[VarType] = None):
        """To initialize a var.

        Args:
            default_value: The initial _value of the variable
        """
        super().__init__()
        self._value: _typing.Optional[VarType] = default_value

    @property
    def value(self) -> _typing.Optional[VarType]:
        """The value stored in the var."""
        return self._value

    @value.setter
    def value(self, new: VarType) -> None:
        if self._value != new:
            self._value = new
            self.trigger(event_types.VarChanged(self))


class Query(_typing.Generic[VarType]):
    """To reference the realtime return value of a function.

    When taking the value, its usage is same as Var:
    .. code-block:: python
        Query(...).value
        var.unpack_var(Query(...))
    """
    def __init__(self, func: _typing.Callable[..., VarType]):
        """To initialize a Query object.

        :param func: The callable to query when getting the value
        """
        self.func: _typing.Callable[..., VarType] = func
        self.func_args: tuple | list = []
        self.func_kwargs: dict = {}

    @property
    def value(self) -> VarType:
        return self.func(*self.func_args, **self.func_kwargs)


VarOrVal: _typing.TypeAlias = VarType | Var[VarType] | Query[VarType]


@_typing.overload
def unpack_var(
    var_or_val: VarOrVal[VarType],
    default: None = None
    ) -> VarType | None: ...
@_typing.overload
def unpack_var(
    var_or_val: VarOrVal[VarType],
    default: VarType
    ) -> VarType: ...

def unpack_var(
    var_or_val: VarOrVal[VarType],
        default: VarType | None = None
        ) -> VarType | None:
    """To extract the value from param 1 if it is a var or query, otherwise return it as-is.

    :param var_or_val: The var to dispatch or the value to return as-is
    :param default: Value to return if the value of the var is False
    """
    if isinstance(var_or_val, Var) or isinstance(var_or_val, Query):
        val = var_or_val.value
        if val is None:
            return default
        else:
            return val
    else:
        return var_or_val


def resolve_references(original: VarOrVal[VarType]) -> VarType:
    """Replace nested Vars and Queries in containers and object attributes.

    Please note that this is a vibed module!

    Objects with no possible Var or Query attributes are returned unchanged.
    Mutable values are updated in place; immutable containers are rebuilt when a child changes.
    Cycles are stopped by identity and active Query tracking.

    :param original: The object to perform operations on
    """
    resolved_by_id: dict[int, object] = {}
    contains_reference: dict[int, bool] = {}
    checking: set[int] = set()

    def attributes(value: object) -> list[tuple[str, object]]:
        try:
            items = list(vars(value).items())
        except TypeError:
            items = []

        for cls in type(value).__mro__:
            slots = cls.__dict__.get("__slots__", ())
            if isinstance(slots, str):
                slots = (slots,)
            for name in slots:
                if name in ("__dict__", "__weakref__"):
                    continue
                if name.startswith("__") and not name.endswith("__"):
                    name = f"_{cls.__name__.lstrip('_')}{name}"
                if any(existing_name == name for existing_name, _ in items):
                    continue
                try:
                    items.append((name, getattr(value, name)))
                except AttributeError:
                    continue
        return items

    def children(value: object) -> _typing.Iterable[object]:
        if isinstance(value, _MutableMapping):
            for key, item in value.items():
                yield key
                yield item
        elif isinstance(value, (list, tuple, set, frozenset)):
            yield from value
        elif not isinstance(value, (type, _types.ModuleType, _types.FunctionType,
                                    _types.BuiltinFunctionType, _types.MethodType)):
            for _, item in attributes(value):
                yield item

    def may_contain_reference(value: object) -> bool | None:
        if isinstance(value, (Var, Query)):
            return True
        value_id = id(value)
        if value_id in contains_reference:
            return contains_reference[value_id]
        if value_id in checking:
            return None
        if value is None or isinstance(value, (str, bytes, int, float, complex, bool,
                                               type, _types.ModuleType,
                                               _types.FunctionType,
                                               _types.BuiltinFunctionType,
                                               _types.MethodType)):
            contains_reference[value_id] = False
            return False

        checking.add(value_id)
        result = False
        uncertain = False
        for item in children(value):
            child_result = may_contain_reference(item)
            if child_result is True:
                result = True
                break
            if child_result is None:
                uncertain = True
        checking.remove(value_id)
        if result:
            contains_reference[value_id] = True
            return True
        if uncertain:
            return None
        contains_reference[value_id] = False
        return False

    def query_value_key(value: object) -> tuple[type, object]:
        if value is None or isinstance(value, (str, bytes, int, float, complex, bool)):
            return type(value), value
        return type(value), id(value)

    def query_key(query: Query) -> tuple[object, ...]:
        func = query.func
        target = getattr(func, "__func__", func)
        code = getattr(target, "__code__", target)
        defaults = getattr(target, "__defaults__", None) or ()
        kwdefaults = getattr(target, "__kwdefaults__", None) or {}
        closure = getattr(target, "__closure__", None) or ()
        closure_ids = tuple(id(cell.cell_contents) for cell in closure)
        bound_self = getattr(func, "__self__", None)
        return (
            code,
            id(bound_self) if bound_self is not None else None,
            tuple(query_value_key(item) for item in defaults),
            tuple(sorted((key, query_value_key(item)) for key, item in kwdefaults.items())),
            closure_ids,
            tuple(id(arg) for arg in query.func_args),
            tuple((key, id(arg)) for key, arg in query.func_kwargs.items()),
        )

    def resolve(value: object) -> object:
        value_id = id(value)
        if value_id in resolved_by_id:
            return resolved_by_id[value_id]
        if may_contain_reference(value) is False:
            return value

        if isinstance(value, (Var, Query)):
            resolved_by_id[value_id] = value
            if isinstance(value, Query):
                key = query_key(value)
                active_keys = _active_query_keys.get()
                if key in active_keys:
                    return value
                token = _active_query_keys.set(active_keys | {key})
                try:
                    resolved = resolve(value.value)
                finally:
                    _active_query_keys.reset(token)
            else:
                resolved = resolve(value.value)
            resolved_by_id[value_id] = resolved
            return resolved

        if isinstance(value, _MutableMapping):
            resolved_by_id[value_id] = value
            items = [(resolve(key), resolve(item)) for key, item in value.items()]
            value.clear()
            value.update(items)
            return value

        if isinstance(value, list):
            resolved_by_id[value_id] = value
            for index, item in enumerate(value):
                value[index] = resolve(item)
            return value

        if isinstance(value, set):
            resolved_by_id[value_id] = value
            items = [resolve(item) for item in value]
            value.clear()
            value.update(items)
            return value

        if isinstance(value, tuple):
            resolved_by_id[value_id] = value
            items = tuple(resolve(item) for item in value)
            if all(new is old for new, old in zip(items, value)):
                resolved_by_id[value_id] = value
                return value
            if type(value) is tuple:
                resolved = items
            else:
                constructor = _typing.cast(_typing.Callable[..., object], type(value))
                try:
                    resolved = constructor(*items)
                except TypeError:
                    try:
                        resolved = constructor(items)
                    except TypeError:
                        resolved = items
            resolved_by_id[value_id] = resolved
            return resolved

        if isinstance(value, frozenset):
            resolved_by_id[value_id] = value
            items = [resolve(item) for item in value]
            if all(new is old for new, old in zip(items, value)):
                resolved_by_id[value_id] = value
                return value
            resolved = type(value)(items)
            resolved_by_id[value_id] = resolved
            return resolved

        resolved_by_id[value_id] = value
        try:
            instance_attributes = vars(value)
        except TypeError:
            instance_attributes = {}
        for name, item in attributes(value):
            new_item = resolve(item)
            if new_item is not item:
                if name in instance_attributes:
                    instance_attributes[name] = new_item
                else:
                    try:
                        object.__setattr__(value, name, new_item)
                    except (AttributeError, TypeError):
                        pass
        return value

    return _typing.cast(VarType, resolve(original))


