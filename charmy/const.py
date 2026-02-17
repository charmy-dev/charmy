"""Charmy constants."""

import sys
from enum import Enum


class ID(Enum):
    """ID is an enum to store object ID.

    AUTO: Auto generate ID.
    NONE: No ID.
    """

    AUTO = 0
    NONE = 1


class Backends(Enum):
    """UIFrame is an enum to store UI frame.

    GLFW, SDL, OPENGL, SKIA are consts representing those backends
    """

    GLFW = glfw = "GLFW"
    SDL = sdl = "SDL"
    OPENGL = opengl = "OPENGL"
    SKIA = skia = "SKIA"


class DrawingMode(Enum):
    """DrawingMode is an enum to store drawing mode.
    IMMEDIATE(immediate): IMMEDIATE is an enum to store drawing mode.
    RETAINED(retained): RETAINED is an enum to store drawing mode.
    """

    IMMEDIATE = immediate = "IMMEDIATE"
    RETAINED = retained = "READIED"


MANAGER_ID = "manager"


if sys.platform.startswith("darwin"):
    PLATFORM = "macos"
elif sys.platform == "win32":
    PLATFORM = "windows"