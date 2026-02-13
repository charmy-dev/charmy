import pathlib
import typing
import os
import os.path
import inspect
import json
import warnings

from ..object import CObject


class CTheme(CObject):
    
    """Theme class for CWindow and CWidgets.

    Example
    -------
    .. code-block:: python
        my_theme = CTheme({<Some styles>})
        my_sub_theme = CTheme(parent="default.light")
        my_external_theme = CTheme().load_from_file("./path/to/a/theme.json")
    This shows examples of creating themes, either from a JSON, a parent theme or a file.

    .. code-block:: python
        all_themes = CTheme.LOADED_THEMES
        INTERNAL_THEME = CTheme.INTERNAL_THEME
        DEFAULT_THEME = CTheme.DEFAULT_THEME
    This shows getting all loaded themes, internal themes, and the default theme.

    .. code-block:: python
        default_light_theme = CTheme.find_loaded_theme("default.light")
        if CTheme.validate_theme_existed("default.light"):
            print("Default light theme exists!")
    This shows finding a theme and checking if it exists

    重置后我摸改了一些地方，但逻辑、功能应是大差不差的，某些方法名、变量名我改的易读了点
    """
    
    LOADED_THEMES: list["CTheme"] = []
    INTERNAL_THEME_DIR = pathlib.Path(__file__).parent.parent / "resources" / "themes"
    INTERNAL_THEME: dict[str, "CTheme"] = {}
    DEFAULT_THEME: "CTheme"
    DEFAULT_THEME_FILENAME: str = "light"
    EXPECTED_DATA_TYPE = {
        "styles": dict,
        "color_palette": dict,
        "name": str,
        "friendly_name": str,
        "base": str,
    }

    def __init__(
        self, styles: dict | None = None, parent: typing.Union["CTheme", None] = None, *kwargs
    ) -> None:
        """Theme for CWindow and CWidgets.

        Example
        -------
        .. code-block:: python
            my_theme = CTheme({<Some styles>})
            my_sub_theme = CTheme(parent="default.light")
            my_external_theme = CTheme().load_from_file("./path/to/a/theme.json")
        This shows examples of creating themes, either from a JSON, a parent theme or a file.

        :param styles: Styles of the theme
        :param parent: Parent theme
        """
        super().__init__(**kwargs)  # NOQA

        self["name"]: str = f"untitled.{len(CTheme.LOADED_THEMES) + 1}"
        self["friendly_name"] = f"Untitled theme {len(CTheme.LOADED_THEMES) + 1}"
        # NOQA: friendly_name感觉有点多余? ——Little White Cloud
        # NOQA: Keep it 4 now currently. ——rgzz666
        self.parent: typing.Union["CTheme", None] = parent
        self.children = []
        self["is_special"]: bool = False

        if styles is None:
            self["styles"]: dict = CTheme.DEFAULT_THEME["styles"]
        else:
            self["styles"]: dict = styles
        self["color_palette"] = {}

        CTheme.LOADED_THEMES.append(self)
        return
    
    @classmethod
    def find_loaded_theme(cls, theme_name: str) -> "CTheme | typing.Literal[False]":
        """Search for a loaded theme by name, returns the CTheme object if found, or False if not.

        Example
        -------
        .. code-block:: python
            DEFAULT_THEME = CTheme.find_loaded_theme("default.light")
        This returns the CTheme object of the default theme to `DEFAULT_THEME`.

        :param theme_name: Name of the theme to load
        :return: The CTheme object if found, otherwise False
        """
        for theme in cls.LOADED_THEMES:
            if theme["name"] == theme_name:
                return theme
        return False
    
    @classmethod
    def validate_theme_existed(cls, theme_name: str) -> bool:
        """Validate if the theme with given name existed and loaded.

        Example
        -------
        .. code-block:: python
            CTheme.validate_theme_existed("default.light")
        This returns if the theme `default.light` is loaded.

        :param theme_name: Name of the theme to validate
        :return: If the theme loaded
        """
        return CTheme.find_loaded_theme(theme_name) != False  # ☝🤓

    # region Load theme

    @classmethod
    def _load_internal_theme(cls):
        """Load internal themes. Should be run once at import, see the end of this file."""
        # Load default (ROOT) theme
        CTheme.DEFAULT_THEME = typing.cast(
            "CTheme",
            CTheme({}).load_from_file(
                CTheme.INTERNAL_THEME_DIR / f"{CTheme.DEFAULT_THEME_FILENAME}.json"
            ),
        )

        # Load other internal themes
        for file in os.listdir(CTheme.INTERNAL_THEME_DIR):
            if file == f"{CTheme.DEFAULT_THEME_FILENAME}.json":
                # For default theme, no need to reload it
                CTheme.INTERNAL_THEME[CTheme.DEFAULT_THEME["name"]] = CTheme.DEFAULT_THEME
                continue
            _ = CTheme({}).load_from_file(CTheme.INTERNAL_THEME_DIR / file)
            CTheme.INTERNAL_THEME[_["name"]] = _

    def load_from_file(self, file_path: str | pathlib.Path) -> "CTheme | typing.Literal[False]":
        """Load styles to theme from a file.

        Example
        -------
        .. code-block:: python
            my_theme = CTheme().load_from_file("./path/to/a/theme.json")
            my_theme.load_from_file("./path/to/another/theme.json")

        This shows loading a theme to `my_theme` from the theme file at `./path/to/a/theme.json`,
        and change it to theme from `./path/to/another/theme.json` later.

        :param file_path: Path to the theme file
        :return self: The CTheme itself
        """
        # Change path string into pathlib Path
        if type(file_path) is str:
            file_path = pathlib.Path(file_path)
        # Get path where lies codes calling this function (to support relative path)
        if not file_path.is_absolute():
            frame = inspect.currentframe()
            outer_frame = inspect.getouterframes(frame)[1]
            caller_file = pathlib.Path(outer_frame.filename).parent
            file_path = (caller_file / file_path).resolve()
        # We need a file to load from file \o/ \o/ \o/
        with open(file_path, mode="r", encoding="utf-8") as f:
            style_raw = f.read()

            theme_data = json.loads(style_raw)
            if (search_result := CTheme.find_loaded_theme(theme_data["name"])) != False:
                # If name already occupied, meaning the theme might already be loaded
                # (or just simply has an occupied name)
                warnings.warn(
                    f"Theme <{theme_data['name']}> already loaded or existed.",
                    RuntimeWarning,
                )
                return search_result

        return self.load_from_json(theme_data)

    def load_from_json(self, theme_data: dict) -> "CTheme":
        """Load all data (including metadata) to the theme.

        Example
        -------
        .. code-block:: python
            my_theme = CTheme().load_from_json({<Some JSON theme data>})
            my_theme.load_from_json({<Some JSON theme data>})
        This shows loading a theme to `my_theme` from JSON data, and change it to theme from
        another JSON later.

        :param theme_data: dict that contains the theme data
        :return self: The CTheme itself
        """
        # Type check
        for item in self.EXPECTED_DATA_TYPE.keys():
            if type(theme_data[item]) != self.EXPECTED_DATA_TYPE[item]:
                theme_name = (
                    theme_data["name"] if type(theme_data["name"]) is str else "(Type error)"
                )
                warnings.warn(
                    f"Error data type of <{item}> in theme data that is about to be loaded. "
                    f"Expected {self.EXPECTED_DATA_TYPE[item]} but got {type(item)}. The json data with "
                    f"theme named <{theme_name}> will not be loaded to the theme <{self['name']}>",
                    ResourceWarning,
                )
                return self
        # Load data
        self["styles"] = theme_data["styles"].copy()
        self["color_palette"] = theme_data["color_palette"].copy()
        # Load Metadata
        self.rename(theme_data["name"], theme_data["friendly_name"])
        self.set_parent(theme_data["base"])

        return self

    # endregion