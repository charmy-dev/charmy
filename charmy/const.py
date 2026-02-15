"""Charmy constants."""

from enum import Enum


class ID(Enum):
    """ID is an enum to store object ID.

    AUTO: Auto generate ID.
    NONE: No ID.
    """

    AUTO = 0
    NONE = 1


class UIFrame(Enum):
    """UIFrame is an enum to store UI frame.

    GLFW: GLFW is an enum to store UI frame.
    SDL: SDL is an enum to store UI frame.
    """

    GLFW = glfw = "GLFW"
    SDL = sdl = "SDL"


class BackendFrame(Enum):
    """BackendFrame is an enum to store backend frame.

    OPENGL: OPENGL is an enum to store backend frame.
    """

    OPENGL = opengl = "OPENGL"


class DrawingFrame(Enum):
    """DrawingFrame is an enum to store drawing frame.

    SKIA: SKIA is an enum to store drawing frame.
    """

    SKIA = skia = "SKIA"


class DrawingMode(Enum):
    """DrawingMode is an enum to store drawing mode.
    IMMEDIATE(immediate): IMMEDIATE is an enum to store drawing mode.
    RETAINED(retained): RETAINED is an enum to store drawing mode.
    """

    IMMEDIATE = immediate = "IMMEDIATE"
    RETAINED = retained = "READIED"
