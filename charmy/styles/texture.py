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
"""
# TODO: Write the fucking document

from __future__ import annotations as _

import typing as _typing

from abc import abstractmethod as _abstractmethod
import bisect
import json as _json
import warnings as _warnings

from ..utils import \
    marks as _marks, \
    type_checking as _type_checking, \
    var as _var, \
    clamp_val as _clamp_val

if _typing.TYPE_CHECKING:
    from . import shape as _shape


# region Texture base class

class Texture:
    """Texture base class in Charmy."""
    type: _typing.ClassVar[str] = "texture"

    @staticmethod
    def is_texture_like(value: object) -> bool:
        """Runtime check of TextureLike objects."""
        # return _type_checking.isinstance_of_any(value, [tuple, None])
        match value:
            case tuple(): # Suspect RGB / RGBA
                if len(value) not in [3, 4]:
                    return False
                if False in [type(v) is int for v in value[:3]]:
                    return False
                if len(value) == 4:
                    if type(value[3]) is not float and type(value[3]) is not int:
                        return False
                return True
            case str(): # Suspect HEX
                if value.startswith("#"):
                    starts_with_hashtag = 1 # 1 for yes
                else:
                    starts_with_hashtag = 0 # 0 for no
                if len(value) not in [6 + starts_with_hashtag, 8 + starts_with_hashtag]:
                    return False
                ALLOWED_CHARS = "0123456789ABCDEF"
                if False in [char in ALLOWED_CHARS for char in value[starts_with_hashtag:]]:
                    return False
                return True
            case None: # Suspect TransparentLike (actually confirmed)
                return True
            case _: # Not even suspected to be anything
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
            "color": (255, 0, 0, 0.5),
            }
        """
        # If texture-like stuff, then 'ensure' it and return directly
        if Texture.is_texture_like(json_content):
            json_content = _typing.cast(TextureLike, json_content)
            return ensure_texture(json_content)
        json_content = _typing.cast(dict[str, _typing.Any] | str, json_content)
        # Convert raw content to JSON
        if isinstance(json_content, str):
            json_content = _json.loads(json_content)
            assert type(json_content) is dict
            # 👆 Must assert the type here, because the fucking json module did not specify the 
            # type of the return value of loads()
        if not isinstance(json_content["type"], str):
            raise TypeError(f"Invalid texture JSON: {json_content}")
        cls = Texture.find_class_by_type(json_content["type"])
        if cls is None:
            raise ValueError(f"Invalid texture type {json_content["type"]}.")
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
        if profile_value == _marks.profile_value_fallback_mark:
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
RGB: _typing.TypeAlias = tuple[
    _var.VarOrVal[int], 
    _var.VarOrVal[int], 
    _var.VarOrVal[int]
    ]
ExactRGB: _typing.TypeAlias = tuple[int, int, int]
RGBA: _typing.TypeAlias = tuple[
    _var.VarOrVal[int], 
    _var.VarOrVal[int], 
    _var.VarOrVal[int], 
    _var.VarOrVal[float]
    ]
ExactRGBA: _typing.TypeAlias = tuple[int, int, int, float]
HEX: _typing.TypeAlias = str

ColorLike: _typing.TypeAlias = RGB | RGBA | HEX

# Color class
class Color(Texture):
    """Represents pure colors."""
    type: _typing.ClassVar[str] = "color"

    def __init__(self, color: _var.VarOrVal[RGB | RGBA | HEX]):
        """Initialize a color object.
        
        :param color: The RGB(A) tuple or the HEX string that represents the color
        """

        self._color: _var.VarOrVal[RGB | RGBA | HEX] = (0, 0, 0, 0)
        self.color = color

    def __iter__(self):
        return iter(self.color)

    @staticmethod
    def to_rgba(color: RGB | RGBA | HEX) -> ExactRGBA:
        if isinstance(color, tuple): # Expressed by int tuple
            if len(color) == 4: # RGBA
                r, g, b, a = color
            elif len(color) == 3: # RGB
                r, g, b = color
                a = 1
        elif isinstance(color, str):
            if color[0] == "#": # Remove leading hash if exists
                color = color[1:]
            if len(color) != 6:
                raise ValueError(f"Incorrect HEX color format: incorrect length of {len(color)}.")
                # TODO: Color presets?
            raise NotImplementedError("HEX colors conversion not implemented")
            # TODO: Implement HEX colors
        r = _var.unpack_var(r, 0)
        g = _var.unpack_var(g, 0)
        b = _var.unpack_var(b, 0)
        a = _var.unpack_var(a, 0)
        return r, g, b, a

    @property
    def color(self) -> ExactRGBA:
        color = self.to_rgba(_var.unpack_var(self._color, (0, 0, 0, 0)))
        r = _var.unpack_var(color[0], 0)
        g = _var.unpack_var(color[1], 0)
        b = _var.unpack_var(color[2], 0)
        a = _var.unpack_var(color[3], 0.0)
        # Value check
        if False in [
                0 <= r <= 255, 
                0 <= g <= 255, 
                0 <= b <= 255, 
                0 <= a <= 1
                ]:
            _warnings.warn(
                "Color should be in form of (R 0~255, G 0~255, B 0~255, A 0.0~1.0). "
                f"Received wrong value {(r, g, b, a)} and will be clamped."
                )
            r = _clamp_val(r, 0, 255)
            g = _clamp_val(g, 0, 255)
            b = _clamp_val(b, 0, 255)
            a = _clamp_val(a, 0.0, 1.0)
        return r, g, b, a

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

    def _manipulate_value(self, index: int, new: int | float) -> bool:
        if isinstance(self._color, _var.Query):
            _warnings.warn("Cannot set color value for colors expressed by Query.")
            return False
        if isinstance(self._color, _var.Var):
            color = self._color.value
        else:
            color = self._color
        if type(color) is str:
            color_vals = list(self.to_rgba(color))
        color_vals[index] = new
        assert len(color_vals) == 3 or len(color_vals) == 4
        if isinstance(self._color, _var.Var):
            self._color.value = tuple(color_vals) # type: ignore
        else:
            self._color = tuple(color_vals) # type: ignore
        return True

    @r.setter
    def r(self, new: int):
        if not 0 < new < 255:
            _warnings.warn(
                f"Invalid value {new} for Color.r, must be between 0~255. Will be clamped."
                )
            new = _clamp_val(new, 0, 255)
        self._manipulate_value(0, new)
    @g.setter
    def g(self, new: int):
        if not 0 < new < 255:
            _warnings.warn(
                f"Invalid value {new} for Color.g, must be between 0~255. Will be clamped."
                )
            new = _clamp_val(new, 0, 255)
        self._manipulate_value(1, new)
    @b.setter
    def b(self, new: int):
        if not 0 < new < 255:
            _warnings.warn(
                f"Invalid value {new} for Color.b, must be between 0~255. Will be clamped."
                )
            new = _clamp_val(new, 0, 255)
        self._manipulate_value(2, new)
    @a.setter
    def a(self, new: float):
        if not 0 < new < 1:
            _warnings.warn(
                f"Invalid value {new} for Color.a, must be between 0~1. Will be clamped."
                )
            new = _clamp_val(new, 0.0, 1.0)
        self._manipulate_value(3, new)

    @color.setter
    def color(self, new: _var.VarOrVal[RGB | RGBA | HEX]):
        self._color = _var.unpack_var(new, (0, 0, 0, 0))
        


# region Transparent

class Transparent(Texture):
    """Represents transparent.

    Note that, in actual rendering, items with Transparent texture should be skipped.
    """
    type: _typing.ClassVar[str] = "transparent"

    def __init__(self):
        """Initialize a Transparent object."""
        self.color = (0, 0, 0, 0)

    def __iter__(self):
        return iter(self.color)

TransparentLike: _typing.TypeAlias = None | tuple[int, int, int, _typing.Literal[0]]


# region Gradient

class Gradient(Texture):
    """Gradient base class."""

    @_abstractmethod 
    def get_color_at_ratio(self, ratio: float) -> Color: ...

    @_abstractmethod
    def get_color_at_point(self, point: _shape.Point) -> Color: ...


class LinearGradient(Gradient):
    """Linear gradient."""
    type: _typing.ClassVar[str] = "linear_gradient"

    def __init__(self, 
            start_point: tuple[_var.VarOrVal[int], _var.VarOrVal[int]], 
            end_point: tuple[_var.VarOrVal[int], _var.VarOrVal[int]], 
            colors: _var.VarOrVal[dict[float, \
                    _var.VarOrVal[Color | ColorLike | Transparent | TransparentLike]]]
            ):
        """Initialize a linear gradient texture.

        :param start_point: Start point of gradient line
        :param end_point: End point of gradient line
        :param colors: Colors in the gradient, in form of {ratio: color, ...}
        """
        self.start_point: tuple[_var.VarOrVal[int], _var.VarOrVal[int]] = start_point
        self.end_point: tuple[_var.VarOrVal[int], _var.VarOrVal[int]] = end_point
        self.colors: _var.VarOrVal[dict[float, \
                    _var.VarOrVal[Color | ColorLike | Transparent | TransparentLike]]] = colors

    def get_color_at_ratio(self, ratio: float) -> RGBA:
        """To get the color at a specific ratio in linear gradient.

        This is a vibed module.

        :param ratio: The ratio to get color at
        """
        colors = _var.unpack_var(self.colors, {})
        if not colors:
            raise ValueError("Linear gradient requires at least one color stop.")

        ratio_list = sorted(colors.keys())
        if ratio <= ratio_list[0]:
            return _typing.cast(RGBA, 
                                ensure_texture(colors[ratio_list[0]]).color) # type: ignore
        if ratio >= ratio_list[-1]:
            return _typing.cast(RGBA, 
                                ensure_texture(colors[ratio_list[-1]]).color) # type: ignore

        insert_pos = bisect.bisect_left(ratio_list, ratio)
        if insert_pos == len(ratio_list):
            insert_pos = len(ratio_list) - 1
        if ratio == ratio_list[insert_pos]:
            return _typing.cast(RGBA, 
                        ensure_texture(self.colors[ratio_list[insert_pos]]).color) # type: ignore

        lower_ratio = ratio_list[insert_pos - 1]
        higher_ratio = ratio_list[insert_pos]
        lower_color = _typing.cast(Color, ensure_texture(_var.unpack_var(colors[lower_ratio])))
        higher_color = _typing.cast(Color, ensure_texture(_var.unpack_var(colors[higher_ratio])))

        span = higher_ratio - lower_ratio
        if span == 0:
            return _typing.cast(RGBA, lower_color.color)

        weight = (ratio - lower_ratio) / span
        result = [
            int(lower_v + (higher_v - lower_v) * weight)
            for lower_v, higher_v in zip(lower_color.color[:3], higher_color.color[:3])
        ]
        result.append(lower_color.color[3] + (higher_color.color[3] - lower_color.color[3]) \
                      * weight) # type: ignore
        return _typing.cast(RGBA, tuple(result))

    def get_color_at_point(self, point: _shape.Point) -> Color:
        """To get the color at a specific pixel.

        This is a vibed module.

        :param point: The point to get color at
        """
        x0, y0 = _var.unpack_var(self.start_point, (0, 0))
        x1, y1 = _var.unpack_var(self.end_point, (0, 0))
        x0 = _var.unpack_var(x0, 0); y0 = _var.unpack_var(y0, 0)
        x1 = _var.unpack_var(x1, 0); y1 = _var.unpack_var(y1, 0)
        dx, dy = x1 - x0, y1 - y0
        if dx == 0 and dy == 0:
            ratio = 0.0
        else:
            numerator = (point[0] - x0) * dx + (point[1] - y0) * dy
            denominator = dx * dx + dy * dy
            ratio = numerator / denominator
            ratio = max(0.0, min(1.0, ratio))
        return Color(self.get_color_at_ratio(ratio))


# region ensure_texture

TextureLike: _typing.TypeAlias = ColorLike | TransparentLike

def ensure_texture(texture_like: Texture | TextureLike, 
        prefer_color_on_zero_alpha: bool = False
        ) -> Texture:
    """Convert TextureLike types into Texture objects.

    :param texture_like: The TextureLike value
    :param prefer_color_on_zero_alpha: Returns color instead of transparent when set to True
    :return texture: The converted Texture object.
    """
    if isinstance(texture_like, Texture):
        result = texture_like
    else:
        if not Texture.is_texture_like(texture_like):
            # Not TextureLike
            raise TypeError(
                f"Expected a TextureLike type to convert to Texture, but got {texture_like}"
                )
        # Convert into texture
        if isinstance(texture_like, tuple): # RGB(A)
            if len(texture_like) == 4: # RGBA
                if texture_like[-1] == 0 and not prefer_color_on_zero_alpha: # Transparent
                    result = Transparent()
                else: # RGBA, not transparent
                    result = Color(texture_like)
            elif len(texture_like) == 3: # RGB
                result = Color(texture_like)
        elif isinstance(texture_like, str): # HEX
            result = Color(texture_like)
        elif texture_like is None: # Transparent
            result = Transparent() if not prefer_color_on_zero_alpha else Color((0, 0, 0))
        else:
            raise ValueError(
                f"Value {texture_like} in type {type(texture_like)} does not "
                "represent a valid texture!"
                )
    return result


# region: TextureType

TextureType: _typing.TypeAlias = Texture | TextureLike
TextureJSON: _typing.TypeAlias = dict[str, _typing.Any]

# endregion