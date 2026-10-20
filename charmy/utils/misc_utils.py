import typing as _typing


@_typing.overload
def clamp_val(val: int, min_val: int, max_val: int) -> int: ...
@_typing.overload
def clamp_val(val: int | float, min_val: int | float, max_val: int | float) -> int | float: ...

def clamp_val(val: int | float, min_val: int | float, max_val: int | float) -> int | float:
    if val > max_val:
        return max_val
    elif val < min_val:
        return min_val
    else:
        return val