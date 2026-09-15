"""Texture classes in Charmy.

Charmy provides several types of textures, ranging from basid colors (with trasnsparency) to 
more complicated effects such as Gaussian blur implemented by filters.

Types of Textures
-----------------
Currently, following types of textures are provided.

:Color:         Represents pure RGBA colors
:Transparent:   Represents transparent (not visible) and will not be rendered

For details, see docstrings of each class inside this file.

TextureLike Types
-----------------
TextureLike types are type aliases that are used to represent types that are not subclasses of the 
`Texture` base class, but can be used to represent colors. e.g. `tuple[int, int, int, int]` can be 
used to represent RGBA colors.

For full list of TextureLike types, see (NOT WRITTEN YET) section in the document.

Alpha Format
------------
Alpha is accepted in two unambiguous forms, and is always stored internally as a `float` between 
`0.0` and `1.0` (which is what backends expect):

:int alpha:  `0`-`255`, the format used by all theme JSON files. `(40, 130, 255, 255)` is opaque.
:float alpha: `0.0`-`1.0`. `(40, 130, 255, 0.5)` is half transparent.

An `int` is never interpreted as a `0.0`-`1.0` value and a `float` is never interpreted as a 
`0`-`255` value, so `(0, 0, 0, 1)` (nearly transparent) and `(0, 0, 0, 1.0)` (opaque) differ.

Both `tuple` and `list` are accepted. `list` matters because JSON arrays always decode to `list`.
"""
# TODO: Write the fucking document

from __future__ import annotations as _

import typing as _typing

import json as _json

from ..utils import marks as _marks
from ..utils import type_checking as _type_checking


# region Color helpers

NAMED_COLORS: dict[str, tuple[int, int, int]] = {
    # The HTML4 / CSS Level 1 basic palette, plus a couple of common aliases.
    # Theme authors may use these names in place of a hex string.
    "black":   (0, 0, 0), 
    "silver":  (192, 192, 192), 
    "gray":    (128, 128, 128), 
    "grey":    (128, 128, 128), 
    "white":   (255, 255, 255), 
    "maroon":  (128, 0, 0), 
    "red":     (255, 0, 0), 
    "purple":  (128, 0, 128), 
    "fuchsia": (255, 0, 255), 
    "magenta": (255, 0, 255), 
    "green":   (0, 128, 0), 
    "lime":    (0, 255, 0), 
    "olive":   (128, 128, 0), 
    "yellow":  (255, 255, 0), 
    "navy":    (0, 0, 128), 
    "blue":    (0, 0, 255), 
    "teal":    (0, 128, 128), 
    "aqua":    (0, 255, 255), 
    "cyan":    (0, 255, 255), 
    }

TRANSPARENT_KEYWORD = "transparent"

_HEX_DIGITS = "0123456789abcdefABCDEF"


def _is_int(value: object) -> bool:
    """`True` if value is an int and not a bool. (bool is a subclass of int.)"""
    return isinstance(value, int) and not isinstance(value, bool)


def _is_color_number(value: object) -> bool:
    """`True` if value is a valid 0-255 color channel."""
    return _is_int(value) and 0 <= value <= 255  # type: ignore[operator]


def _normalize_alpha(alpha: object) -> float:
    """Convert an alpha value in either accepted form into a `0.0`-`1.0` float.

    :param alpha: Alpha as an int `0`-`255` or a float `0.0`-`1.0`
    :raises TypeError: If alpha is not an int or a float
    :raises ValueError: If alpha is out of range for its type
    """
    if isinstance(alpha, bool):
        raise TypeError(f"Alpha cannot be a bool, received {alpha!r}.")
    if isinstance(alpha, int):
        if not 0 <= alpha <= 255:
            raise ValueError(f"Int alpha must be in 0-255, received {alpha!r}.")
        return alpha / 255
    if isinstance(alpha, float):
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"Float alpha must be in 0.0-1.0, received {alpha!r}.")
        return alpha
    raise TypeError(
        f"Alpha must be an int (0-255) or a float (0.0-1.0), received "
        f"{alpha!r} of type {type(alpha)}."
        )


def _is_transparent_alpha(alpha: object) -> bool:
    """`True` if alpha means fully transparent in either accepted form."""
    if isinstance(alpha, bool):
        return False
    return alpha == 0


def _parse_hex_color(color_str: str) -> tuple[int, int, int, float]:
    """Parse a hex color (with or without a leading `#`) into an RGBA tuple.

    Accepts the 3, 4, 6 and 8 digit forms, in either letter case.

    :param color_str: The hex color string
    :raises ValueError: If the digits or the length are invalid
    """
    body = color_str[1:] if color_str.startswith("#") else color_str
    if len(body) not in (3, 4, 6, 8):
        raise ValueError(
            f"Hex color must have 3, 4, 6 or 8 digits, received {color_str!r} "
            f"with {len(body)} digit(s)."
            )
    if False in [char in _HEX_DIGITS for char in body]:
        raise ValueError(f"Hex color {color_str!r} contains a non-hexadecimal digit.")
    if len(body) in (3, 4):  # #rgb / #rgba, every digit is doubled
        body = "".join(char * 2 for char in body)
    red = int(body[0:2], 16)
    green = int(body[2:4], 16)
    blue = int(body[4:6], 16)
    alpha = int(body[6:8], 16) / 255 if len(body) == 8 else 1.0
    return (red, green, blue, alpha)


def _parse_color_string(color_str: str) -> tuple[int, int, int, float]:
    """Parse a hex string or a named color into an RGBA tuple.

    :param color_str: The color string
    :raises ValueError: If the string is not a known color
    """
    lowered = color_str.strip().lower()
    if lowered == TRANSPARENT_KEYWORD:
        raise ValueError(
            "'transparent' is not a color: it is represented by `Transparent`, not `Color`. "
            "Use `ensure_texture(\"transparent\")` (or `Transparent()`) instead."
            )
    if lowered in NAMED_COLORS:
        return (*NAMED_COLORS[lowered], 1.0)
    if _is_hex_color_string(color_str):
        return _parse_hex_color(color_str)
    raise ValueError(
        f"Unknown color {color_str!r}: not a hex string (e.g. '#RRGGBB') and not one of the "
        f"known color names. Known names: {sorted(NAMED_COLORS)}."
        )


def _is_hex_color_string(color_str: str) -> bool:
    """`True` if the string looks like a hex color (without validating the digits)."""
    body = color_str[1:] if color_str.startswith("#") else color_str
    if len(body) not in (3, 4, 6, 8):
        return False
    return False not in [char in _HEX_DIGITS for char in body]


def _parse_color_sequence(color_seq: tuple | list) -> tuple[int, int, int, float]:
    """Parse an RGB/RGBA sequence into an RGBA tuple.

    :param color_seq: A 3 or 4 element sequence of numbers
    :raises TypeError: If the length or the element types are invalid
    :raises ValueError: If a value is out of range
    """
    if len(color_seq) not in (3, 4):
        raise TypeError(
            f"A color sequence must have 3 (RGB) or 4 (RGBA) elements, received "
            f"{len(color_seq)}: {color_seq!r}."
            )
    if False in [_is_color_number(channel) for channel in color_seq[0:3]]:
        raise TypeError(
            f"The R, G and B channels must each be an int in 0-255, received {color_seq!r}."
            )
    alpha = _normalize_alpha(color_seq[3]) if len(color_seq) == 4 else 1.0
    return (color_seq[0], color_seq[1], color_seq[2], alpha)

# endregion


# region Texture base class

class Texture:
    """Texture base class in Charmy."""
    type: _typing.ClassVar[str] = "texture"

    @staticmethod
    def is_texture_like(value: object) -> bool:
        """Check whether value can be converted into a `Texture` by `ensure_texture()`.

        Accepted forms are `None`, the string `"transparent"`, a hex color string, a known color 
        name, and a 3/4 element RGB(A) `tuple` or `list`.
        """
        # return _type_checking.isinstance_of_any(value, [tuple, list, None])
        match value:
            case tuple() | list():  # Suspect RGB / RGBA
                if len(value) not in (3, 4):
                    return False
                if False in [_is_color_number(channel) for channel in value[0:3]]:
                    return False
                if len(value) == 3:
                    return True
                alpha = value[3]
                if isinstance(alpha, bool):
                    return False
                if isinstance(alpha, int):
                    return 0 <= alpha <= 255
                if isinstance(alpha, float):
                    return 0.0 <= alpha <= 1.0
                return False
            case str():  # Suspect HEX / color name
                lowered = value.strip().lower()
                if lowered == TRANSPARENT_KEYWORD:
                    return True
                if lowered in NAMED_COLORS:
                    return True
                return _is_hex_color_string(value)
            case None:  # Suspect TransparentLike (actually confirmed)
                return True
            case _:  # Not even suspected to be anything
                return False

    @staticmethod
    def find_class_by_type(type_name: str) -> type[Texture] | None:
        """Find a texture class by line type, return `None` if not found.

        :param type_name: Texture type in string
        """
        for cls in Texture.__subclasses__():
            if cls.type == type_name:
                return cls
        else:
            return None

    @staticmethod
    def from_json(json_content: dict[str, _typing.Any] | str | TextureLike) -> Texture:
        """Create a texture object from json content.

        This function is a static method of Texture and its subclasses. It creates and returns a 
        textre object base on the JSON content given. This will be useful when loading line config 
        from styles.

        :param json_content: The JSON content, either Python dict or raw string data

        JSON Format
        -----------
        Textures can be represented in JSON in a structured way. Each JSON data must has a `type` 
        key that defines the type of the texture, and also other keys and values that specify the 
        params for that texture. The following is an example for pure colors.

        .. code-block:: python

            {
            "type": "color", 
            "color": [255, 0, 0, 128],
            }
        """
        # If texture-like stuff, then 'ensure' it and return directly
        if Texture.is_texture_like(json_content):
            json_content = _typing.cast(TextureLike, json_content)
            return ensure_texture(json_content)
        json_content = _typing.cast(dict[str, _typing.Any] | str, json_content)
        # Convert raw content to JSON
        if isinstance(json_content, str):
            try:
                json_content = _json.loads(json_content)
            except _json.JSONDecodeError as error:
                raise TypeError(
                    f"Texture JSON string {json_content!r} is not valid JSON, and it is not a "
                    f"color string either (not a hex color and not a known color name)."
                    ) from error
            if type(json_content) is not dict:
                # 👆 Must check the type here, because the json module does not specify the 
                # type of the return value of loads()
                raise TypeError(
                    f"Texture JSON string must decode into an object, got {json_content!r}."
                    )
        if "type" not in json_content:
            raise TypeError(f"Texture JSON {json_content!r} has no 'type' key.")
        if not isinstance(json_content["type"], str):
            raise TypeError(f"Invalid texture JSON: {json_content}")
        texture_type = json_content["type"]
        cls = Texture.find_class_by_type(texture_type)
        if cls is None:
            raise ValueError(f"Invalid texture type {texture_type}.")
        params = json_content.copy()
        params.pop("type")
        return cls(**params)

    @staticmethod
    def from_profile_value(
            profile_value: _type_checking.ProfileProp[TextureJSON | TextureType]
            ) -> Texture:
        """Load shape from profile value.

        If is JSON, load from JSON, otherwise return as-is.
        """
        if profile_value is _marks.profile_value_fallback_mark:
            raise TypeError("Profile value used to build shape must be actual value.")
        elif isinstance(profile_value, dict):
            return Texture.from_json(profile_value)
        elif isinstance(profile_value, Texture) or Texture.is_texture_like(profile_value):
            profile_value = _typing.cast(TextureType, profile_value)
            return ensure_texture(profile_value)
        else:
            raise TypeError(
                f"Profile value given to build texture is in wrong type {type(profile_value)}, "
                "while expected ProfileProp[TextureJSON | TextureType]."
                )


# region Color

# Color types
# Inputs may be a tuple or a list (JSON arrays decode to list).
RGB: _typing.TypeAlias = tuple[int, int, int] | list[int]
RGBA: _typing.TypeAlias = tuple[int, int, int, int | float] | list[int | float]
HEX: _typing.TypeAlias = str

ColorLike: _typing.TypeAlias = RGB | RGBA | HEX

# Color class
class Color(Texture):
    """Represents pure colors.

    Accepted inputs
    ---------------
    - a 3 element RGB sequence of ints in `0`-`255`, as `tuple` or `list`
    - a 4 element RGBA sequence, where alpha is an int in `0`-`255` or a float in `0.0`-`1.0`
    - a hex string with 3, 4, 6 or 8 digits, with or without a leading `#`, in either letter case
    - a color name from `NAMED_COLORS`

    The color is stored as `(r, g, b, a)` where the channels are ints in `0`-`255` and alpha is a 
    float in `0.0`-`1.0`, which is the form backends consume. Use `Color.color` for the tuple, or 
    the `r`/`g`/`b`/`a` properties.

    Note that fully transparent colors are represented by `Transparent`, not by `Color`.
    """
    type: _typing.ClassVar[str] = "color"

    # @typing.overload
    # def __init__(self, r: int, g: int, b: int, a: int = 255): ... # RGB(A)
    # @typing.overload
    # def __init__(self, color: tuple[int, int, int, int] | \
    #              tuple[int, int, int]): ... # Single RGB(A) tuple
    # @typing.overload
    # def __init__(self, color: str): ... # Single HEX string (RRGGBB / RRGGBBAA)

    def __init__(self, color: RGB | RGBA | HEX):
        """Initialize a color object.
        
        :param color: The RGB(A) sequence or the HEX / named string that represents the color
        :raises TypeError: If the color is not in an accepted form
        :raises ValueError: If a channel value is out of range, or a string is not a known color
        """

        if isinstance(color, (tuple, list)):
            self.color: RGBA = _parse_color_sequence(color)
        elif isinstance(color, str):
            self.color = _parse_color_string(color)
        else:
            raise TypeError(
                f"Cannot build a Color from {color!r} of type {type(color)}. Expected an RGB(A) "
                "tuple / list, a hex string, or a color name."
                )
        # 👆 All range checking happens inside the parsers, so no silent fallback is possible.

    def __iter__(self):
        return iter(self.color)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return NotImplemented
        return self.color == other.color

    def __hash__(self) -> int:
        return hash(self.color)

    def __repr__(self) -> str:
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a:.4g})"

    @property
    def r(self) -> int:
        return self.color[0]
    @property
    def g(self) -> int:
        return self.color[1]
    @property
    def b(self) -> int:
        return self.color[2]
    @property
    def a(self) -> float:
        return self.color[3]


# region Transparent

class Transparent(Texture):
    """Represents transparent.

    Note that, in actual rendering, items with Transparent texture should be skipped.
    """
    type: _typing.ClassVar[str] = "transparent"

    def __init__(self):
        """Initialize a Transparent object."""
        self.color: RGBA = (0, 0, 0, 0.0)

    def __iter__(self):
        return iter(self.color)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Transparent)

    def __hash__(self) -> int:
        return hash(Transparent)

    def __repr__(self) -> str:
        return "Transparent()"

TransparentLike: _typing.TypeAlias = None | RGB | RGBA


# region ensure_texture

TextureLike: _typing.TypeAlias = ColorLike | TransparentLike

def ensure_texture(texture_like: Texture | TextureLike) -> Texture:
    """Convert TextureLike types into Texture objects.

    :param texture_like: The TextureLike value
    :return texture: The converted Texture object.
    :raises TypeError: If the value is not in an accepted form
    :raises ValueError: If the value is out of range or an unknown color string
    """
    if isinstance(texture_like, Texture):
        return texture_like
    if texture_like is None:
        return Transparent()
    if isinstance(texture_like, str):
        if texture_like.strip().lower() == TRANSPARENT_KEYWORD:
            return Transparent()
        return Color(texture_like)
    if isinstance(texture_like, (tuple, list)):
        # A 4 element sequence whose alpha means fully transparent is Transparent
        if len(texture_like) == 4 and _is_transparent_alpha(texture_like[-1]):
            return Transparent()
        return Color(texture_like)
    raise ValueError(
        f"Value {texture_like!r} in type {type(texture_like)} does not "
        "represent a valid texture!"
        )


# region: TextureType

TextureType: _typing.TypeAlias = Texture | TextureLike
TextureJSON: _typing.TypeAlias = dict[str, _typing.Any]

# endregion