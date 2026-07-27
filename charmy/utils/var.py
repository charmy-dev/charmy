"""Charmy vars.

These are used to implement thing like C(++) pointers. A var will be able to be referenced or 
modified from somewhere else, providing experience like C(++) pointers.
"""

import typing as _typing

from ..event import event_types, EventHandling


VarType = _typing.TypeVar("VarType")

class Var(EventHandling, _typing.Generic[VarType]):
    """Aimed to provide experience like C vars with pointers.

    Args:
        default_value: The initial _value of the variable.
        value_type: The type of the variable.
    """

    def __init__(self, default_value: _typing.Optional[VarType] = None):
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


@_typing.overload
def unpack_var(var_or_val: Var[VarType] | VarType, default: None = None) -> VarType | None: ...
@_typing.overload
def unpack_var(var_or_val: Var[VarType] | VarType, default: VarType) -> VarType: ...

def unpack_var(
        var_or_val: Var[VarType] | VarType, 
        default: VarType | None = None
        ) -> VarType | None:
    """To convert a var to its value if param 1 is a var, otherwise return the param 1 as-is.

    :param var_or_val: The var to dispatch or the value to return as-is
    :param default: Value to return if the value of the var is False
    """
    if isinstance(var_or_val, Var):
        val = var_or_val.value
        if val is None:
            return default
        else:
            return val
    else:
        return var_or_val


VarOrVal: _typing.TypeAlias = VarType | Var[VarType]
