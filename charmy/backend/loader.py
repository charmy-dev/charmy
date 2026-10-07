from __future__ import annotations as _
import typing

import importlib.metadata

if typing.TYPE_CHECKING:
    from .template import Backend


def list_backends_ep() -> list[importlib.metadata.EntryPoint]:
    """Lists all available backends extentions entry point."""
    return [entry_point for entry_point in \
            importlib.metadata.entry_points(group="charmy.backends")]

def load_backend(name: str) -> type[Backend]:
    if name == "auto":
        # for auto backend
        name = "genesis"
    if name == "genesis":
        from . import genesis
        return genesis.Backend
    else:
        raise NotImplementedError(
            f"Other backends (including {name}) not supported yet in early dev."
            )
