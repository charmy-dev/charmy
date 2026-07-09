"""DO NOT RUN THIS FILE DIRECTLY!!!"""

from typing import ClassVar, cast, TypeAlias, Self, Protocol, TypeVar

class WidgetProfile: ...
class ButtonProfile(WidgetProfile):
    dummy_attr: int = 5


# 1. cast
class WidgetA:
    Profile: ClassVar[type[WidgetProfile]] = WidgetProfile

    def foo(self) -> WidgetProfile:
        result = WidgetProfile()
        return cast(type(self).Profile, result)


# 2. TypeAlias
class WidgetB:
    Profile: TypeAlias = WidgetProfile

    def foo(self) -> Profile:
        ...

class ButtonB(WidgetB):
    Profile: TypeAlias = ButtonProfile

r = ButtonB().foo()
r.dummy_attr


# 3. Self
class Widget:
    Profile = WidgetProfile

    def foo(self: Self):
        reveal_type(self)
        reveal_type(type(self))
        reveal_type(self.Profile)


# 4. Protocol
class HasProfile(Protocol):
    Profile: ClassVar[type[WidgetProfile]]

def f(x: HasProfile):
    reveal_type(x.Profile)


# 5.
P = TypeVar("P", bound=WidgetProfile)

class Widget:
    Profile: type[P]