"""Charmy text style module.

This module is relatively simple, which only contains ability to express fonts.
"""

from __future__ import annotations as _

import typing as _typing

if _typing.TYPE_CHECKING:
    from .. import graphics as cm_draw
    from ..backend import template as cm_backend


class WEIGHT:
    """Preset constant values of fontweight.

    Introduction to TrueType Fontweight
    -----------------------------------
    TrueType fontweight determines the thickness of text. It has some common 
    presets which are listed below. Learn more in [MSDN docs about this](https:\
//learn.microsoft.com/en-us/dotnet/api/system.windows.fontweights?view=netframe\
work-4.8#remarks).

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
    """

    THIN: int = 100
    EXTRALIGHT: int = 200
    LIGHT: int = 300
    REGULAR: int = 400
    MEDIUM: int = 500
    SEMIBOLD: int = 600
    BOLD: int = 700
    EXTRABOLD: int = 800
    BLACK: int = 900
    EXTRABLACK: int = 950


class TextStyle:
    """Represents text styles in Charmy."""

    sys_fonts: _typing.ClassVar[list[str]] = ["Arial"]
    sys_default: _typing.ClassVar[_typing.Self]

    def __init__(
        self,
        font: _typing.Optional[str] = None,
        size: _typing.Optional[int] | float = None,
        weight: int = WEIGHT.REGULAR,
        italic: bool = False,
        underlined: bool | cm_draw.DrawnLine = False,
        strikethrough: bool | cm_draw.DrawnLine = False,
    ):
        """To express a font style in Charmy.

        :param font: The name of the font to use, default is system font (reported by backend)
        :param size: The size of the text, default is system font size (reported by backend)
        :param weight: 
            Weight of the text, in integer, default is `charmy.font.WEIGHT.REGULAR` which equals to 
            400
        :param italic: Whether the text should be italic, default is `False`
        :param underlined: 
            Either a bool indicating if underlined, or a `DrawnLine` object to specify line used, 
            default is `False`
        :param strikethrough:
            Either a bool indicating if striked through, or a `DrawnLine` object to specify line 
            used, default is `False`

        For parameter `weight`
        ----------------------
        See [TrueType fontweight](https://learn.microsoft.com/en-us/dotnet/api/system.windows.fontw\
eights?view=netframework-4.8#remarks) to learn more about the values. Presets are provided in 
        `charmy.font.WEIGHT` class, which my be used in the way shown below

        .. code-block:: python
            import charmy
            myfont = charmy.font.Font("Arial", 14, charmy.font.WEIGHT.REGULAR)

        """
        self.font: str = font if font is not None else self.sys_default.font
        self.size: int | float = size if size is not None else self.sys_default.size
        self.weight: int = weight
        self.italic: bool = italic
        self.underlined: bool | cm_draw.DrawnLine = underlined
        self.strikethrough: bool | cm_draw.DrawnLine = strikethrough

    @staticmethod
    def from_json(json_content):
        return TextStyle(**json_content)

    def get_text_boundary(self, text: str, backend: _typing.Optional[cm_backend.Backend]):
        """Get boundary of a specific text in this style."""
        if backend is not None:
            # If backend specified, then get size from backend
            from .. import graphics

            return backend.TextBase.get_text_bound(graphics.DrawnText(text, self, (0, 0, 0)))
        else:
            pass


TextStyle.sys_default = TextStyle("Arial", 14)
