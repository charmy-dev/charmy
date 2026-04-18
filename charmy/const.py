"""Charmy constants."""
import typing
import dataclasses
# import sys
from os import environ
from enum import Enum

if typing.TYPE_CHECKING:
    from . import cmm



@dataclasses.dataclass
class Configs():
    default_backend: str         = environ.get("CHARMY_BACKEND", "auto")


class Common():
    managers_instances: list[cmm.CharmyManager] = []


class ID(Enum):
    """ID is an enum to store object ID.

    AUTO: Auto generate ID.
    NONE: No ID.
    """

    AUTO = 0
    NONE = 1


# @dataclasses.dataclass
# class Backends:
#     OPENGL = opengl = "OPENGL"


# @dataclasses.dataclass
# class UI:
#     GLFW = glfw = "GLFW"
#     SDL = sdl = "SDL"


# @dataclasses.dataclass
# class Drawing:
#     SKIA = skia = "SKIA"


class DrawingMode(Enum):
    """DrawingMode is an enum to store drawing mode.
    IMMEDIATE(immediate): IMMEDIATE is an enum to store drawing mode.
    RETAINED(retained): RETAINED is an enum to store drawing mode.
    """

    IMMEDIATE = immediate = "IMMEDIATE"
    RETAINED = retained = "READIED"


MANAGER_ID = "manager"


class Orient(Enum):
    HORIZONTAL = H = "h"
    VERTICAL = V = "v"


# if sys.platform.startswith("darwin"):
#     PLATFORM = "macos"
# elif sys.platform == "win32":
#     PLATFORM = "windows"
