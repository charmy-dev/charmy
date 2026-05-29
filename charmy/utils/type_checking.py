import typing


@typing.runtime_checkable
class PILImageType(typing.Protocol):
    im: typing.Any
    def save(self, fp, format, **params) -> None: ...

@typing.runtime_checkable
class Curve(typing.Protocol):
    def save(self, fp, format, **params) -> None: ...