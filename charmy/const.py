from enum import Enum


class ID(Enum):
    AUTO = 0
    NONE = 1


class UIFrame(Enum):
    GLFW = glfw = "GLFW"
    SDL = sdl = "SDL"


class BackendFrame(Enum):
    OPENGL = opengl = "OPENGL"


class DrawingFrame(Enum):
    SKIA = skia = "SKIA"


class DrawingMode(Enum):
    IMMEDIATE = immediate = "IMMEDIATE"
    Retained = retained = "READIED"