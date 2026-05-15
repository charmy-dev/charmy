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

import typing

import json

from . import style


# region Texture base class

class Texture:
    """Texture base class in Charmy."""
    type: typing.ClassVar[str] = "texture"

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
    def from_json(json_content: dict[str, typing.Any] | str) -> Texture:
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
            "color": (255, 0, 0, 100),
            }
        """
        # Convert raw content to JSON
        if isinstance(json_content, str):
            json_content = json.loads(json_content)
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


# region Color

# Color types
RGB: typing.TypeAlias = tuple[int, int, int]
RGBA: typing.TypeAlias = tuple[int, int, int, int]
HEX: typing.TypeAlias = str

ColorLike: typing.TypeAlias = RGB | RGBA | HEX

# Color class
class Color(Texture):
    """Represents pure colors."""
    type: typing.ClassVar[str] = "color"

    # @typing.overload
    # def __init__(self, r: int, g: int, b: int, a: int = 255): ... # RGB(A)
    # @typing.overload
    # def __init__(self, color: tuple[int, int, int, int] | \
    #              tuple[int, int, int]): ... # Single RGB(A) tuple
    # @typing.overload
    # def __init__(self, color: str): ... # Single HEX string (RRGGBB / RRGGBBAA)

    def __init__(self, color: RGB | RGBA | HEX):
        """Initialize a color object.
        
        :param color: The RGB(A) tuple or the HEX string that represents the color
        """

        self.color: RGBA = (0, 255, 0, 255)

        if isinstance(color, tuple): # Expressed by int tuple
            if len(color) == 4: # RGBA
                self.color = color
            elif len(color) == 3: # RGB
                self.color = (*color, 255)
        elif isinstance(color, str):
            if color[0] == "#": # Remove leading hash if exists
                color = color[1:]
            if len(color) == 6:
                raise NotImplementedError("HEX colors conversion not implemented")
                # TODO: Implement HEX colors

    def __iter__(self):
        return iter(self.color)

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
    def a(self) -> int:
        return self.color[3]


# region Transparent

class Transparent(Texture):
    """Represents transparent.

    Note that, in actual rendering, items with Transparent texture should be skipped.
    """
    type: typing.ClassVar[str] = "transparent"

    def __init__(self):
        """Initialize a Transparent object."""
        self.color = (0, 0, 0, 0)

    def __iter__(self):
        return iter(self.color)

TransparentLike: typing.TypeAlias = None | tuple[int, int, int, typing.Literal[0]]

# endregion


# region ensure_texture

TextureLike: typing.TypeAlias = ColorLike | TransparentLike

def ensure_texture(texture_like: Texture | TextureLike) -> Texture:
    """Convert TextureLike types into Texture objects.

    :param texture_like: The TextureLike value
    :return texture: The converted Texture object.
    """
    if isinstance(texture_like, Texture):
        result = texture_like
    else:
        # Convert into texture
        if isinstance(texture_like, tuple): # RGB(A)
            if len(texture_like) == 4: # RGBA
                if texture_like[-1] == 0: # Transparent
                    result = Transparent()
                else: # RGBA, not transparent
                    result = Color(texture_like)
            elif len(texture_like) == 3: # RGB
                result = Color(texture_like)
        elif isinstance(texture_like, str): # HEX
            result = Color(texture_like)
        elif texture_like is None: # Transparent
            result = Transparent()
        else:
            raise ValueError(
                f"Value {texture_like} in type {type(texture_like)} does not "
                "represent a valid texture!"
                )
    return result

# endregion