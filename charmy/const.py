"""Charmy constants."""
from __future__ import annotations as _

import typing
import dataclasses
# import sys
from os import environ
from enum import Enum


class DEBUG_FLAGS:
    """Debug options, for testing only, no guarantee under production."""
    DRAW_OBJECTS_BOUNDARY: bool = False
    WAIT_AFTER_EACH_FRAME: bool | float = False
    MARK_REDRAWS: bool = False # BUG: redraw markings will be kept until next redraw
    FORCE_REDRAW_WHOLE_WIN: bool = False
    PRINT_REDRAWN_OBJ_IDS: bool = False


@dataclasses.dataclass
class Configs:
    default_backend: str         = environ.get("CHARMY_BACKEND", "auto")


class MOUSE_KEYS:
    """Consts of mouse keys.

    - LEFT: 0
    - MIDDLE: 1
    - RIGHT: 2
    """
    LEFT    : int = 0
    MIDDLE  : int = 1
    RIGHT   : int = 2

class DIRECTIONS:
    """Consts to represent directions.

    Currently used by linear layout.

    - ROW / X / HORIZONTAL / H: 0
    - COLUMN / Y / VERTICAL / V: 1
    """
    ROW         : int = 0
    COLUMN      : int = 1
    X           : int = 0
    Y           : int = 1
    HORIZONTAL  : int = 0
    VERTICAL    : int = 1
    H           : int = 0
    V           : int = 1

class FONTWEIGHT:
    """Preset constant values of fontweight.

    Introduction to TrueType Fontweight
    -----------------------------------
    TrueType fontweight determines the thickness of text. It has some common presets which are 
    listed below. Learn more in [MSDN docs about this](https://learn.microsoft.com/en-us/dotnet/api\
/system.windows.fontweights?view=netframework-4.8#remarks).

    List of Presets
    ---------------
    =========================== ============== =======
    Font Weight                 Preset         Value  
    =========================== ============== =======
    Thin / Hairline             `THIN`         100    
    Extra Light / Ultra Light   `EXTRALIGHT`   200    
    Light                       `LIGHT`        300    
    Regular                     `REGULAR`      400    
    Medium                      `MEDIUM`       500    
    Semi Bold                   `SEMIBOLD`     600    
    Bold                        `BOLD`         700    
    Extra Bold / Ultra Bold     `EXTRABOLD`    800    
    Black / Heavy               `BLACK`        900    
    Extra Black / Ultra Black   `EXTRABLACK`   950    

    **Note:** Some fontweights might not be supported by all backends!
    """
    THIN        : int = 100
    EXTRALIGHT  : int = 200
    LIGHT       : int = 300
    REGULAR     : int = 400
    MEDIUM      : int = 500
    SEMIBOLD    : int = 600
    BOLD        : int = 700
    EXTRABOLD   : int = 800
    BLACK       : int = 900
    EXTRABLACK  : int = 950


# if sys.platform.startswith("darwin"):
#     PLATFORM = "macos"
# elif sys.platform == "win32":
#     PLATFORM = "windows"
