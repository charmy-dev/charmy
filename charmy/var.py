import typing

from .event import Event, EventHandling


class Var(EventHandling):
    """Similar to Tkinter's `Var`, it is used for data transfer and synchronization.

    Args:
        default_value: The initial _value of the variable.
        value_type: The type of the variable.
    """

    def __init__(self, default_value=None, value_type: type | typing.Any = typing.Any):
        super().__init__()

        self.new(
            "value",
            default_value if default_value is not None else value_type(),
            set_func=self._set_value,
        )
        self._value_type: type = value_type

    def _set_value(self, value: typing.Any) -> typing.Self:
        if self["value"] != value:
            try:
                self.set("value", self._value_type(value), skip=True)
            except ValueError:
                pass
            else:
                self.trigger(Event(self, "change", value=value))

        return self


class StringVar(Var):
    """Only records values of type `str`."""

    def __init__(self, default_value: str = ""):
        super().__init__(default_value, str)


class IntVar(Var):
    """Only records values of type `int`."""

    def __init__(self, default_value: int = 0):
        super().__init__(default_value, int)


class BooleanVar(Var):
    """Only records values of type `bool`."""

    def __init__(self, default_value: bool = False):
        super().__init__(default_value, bool)


class FloatVar(Var):
    """Only records values of type `float`."""

    def __init__(self, default_value: float = 0.0):
        super().__init__(default_value, float)
