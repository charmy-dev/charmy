import typing as _typing

from ..event import event_types, EventHandling


VarType = _typing.TypeVar("VarType")

class Var(_typing.Generic[VarType]):
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
        return self._value

    @value.setter
    def value(self, new: VarType) -> None:
        if self._value != new:
            self._value = new
            # TODO: Triger event when var value changed
            # ...trigger(...)