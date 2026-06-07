from __future__ import annotations as _

import typing as _typing

if _typing.TYPE_CHECKING:
    from .. import styles as _styles
    from ..backend.template import WindowBase as _WindowBase
    from ..widgets import container as _container
    from ..widgets import widget as _widget


@_typing.runtime_checkable
class PILImageType(_typing.Protocol):
    im: _typing.Any

    def save(self, fp, format, **params) -> None: ...


@_typing.runtime_checkable
class ContainerLike(_typing.Protocol):
    def get_mouse_hover(
        self, pos: _styles.shape.Point
    ) -> _typing.List[_container.Container | _widget.Widget]: ...


@_typing.runtime_checkable
class WindowLike(_typing.Protocol):
    backend_base: _WindowBase
