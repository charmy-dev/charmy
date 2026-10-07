"""Charmy vars.

This module contains Var and Query, which are used for referencing in Python.

Vars are used to implement thing like C(++) pointers. A var will be able to be referenced or
modified from somewhere else, providing experience like C(++) pointers.

Starting from [Commit hash here later], this module also provides a Query class for realtime
referencing the return value of a specific callable (like class properties, but may be used outside
classes), with an interface that is similar to Vars.
"""

import typing as _typing

from ..event import event_types, EventHandling


VarType = _typing.TypeVar("VarType")

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


@_typing.overload
def unpack_var(
    var_or_val: Var[VarType] | Query[VarType] | VarType, 
    default: None = None
    ) -> VarType | None: ...
@_typing.overload
def unpack_var(
    var_or_val: Var[VarType] | Query[VarType] | VarType, 
    default: VarType
    ) -> VarType: ...

def unpack_var(
        var_or_val: Var[VarType] | Query[VarType] | VarType, 
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


VarOrVal: _typing.TypeAlias = VarType | Var[VarType] | Query[VarType]
