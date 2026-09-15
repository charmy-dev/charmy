from __future__ import annotations

import inspect
import json
import pathlib
import typing
import warnings

from ..cm_object import CharmyObject

__all__ = ["Theme"]


# TODO: Come on, rewrite this shit, I believe you can do it, I'm speaking to myself...


def _read_theme_json(file_path: pathlib.Path) -> dict:
    """Read and parse a theme JSON file.

    :param file_path: Path of the theme file
    :raises OSError: If the file cannot be read
    :raises ValueError: If the file is not a JSON object
    """
    with open(file_path, mode="r", encoding="utf-8") as f:
        style_raw = f.read()
    theme_data = json.loads(style_raw)
    if not isinstance(theme_data, dict):
        raise ValueError(
            f"Theme file {file_path} must contain a JSON object, got {type(theme_data)}."
            )
    return theme_data


class Theme(CharmyObject):
    """Theme class for CWindow and CWidgets.

    Theme data is stored like a mapping, so `theme["name"]`, `theme["styles"]` and 
    `theme.get("color_palette", {})` all work. Metadata lives under the keys `name`, 
    `friendly_name`, `base`, `styles` and `color_palette`.

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

    LOADED_THEMES: list["Theme"] = []
    INTERNAL_THEME_DIR = pathlib.Path(__file__).parent.parent / "resources" / "themes"
    INTERNAL_THEME: dict[str, "Theme"] = {}
    # 👇 Assigned by `_load_internal_theme()`; stays `None` if the theme files are unavailable.
    DEFAULT_THEME: typing.Optional["Theme"] = None
    DEFAULT_THEME_FILENAME: str = "light"
    # 👇 The `base` value meaning "this theme has no parent".
    STRUCTURAL_PARENT: str = "ROOT"
    EXPECTED_DATA_TYPE = {
        "styles": dict,
        "color_palette": dict,
        "name": str,
        "friendly_name": str,
        "base": str,
    }

    def __init__(
        self, styles: dict | None = None, parent: typing.Union["Theme", None] = None, **kwargs
    ) -> None:
        """Theme for CWindow and CWidgets.

        Example
        -------
        .. code-block:: python

            my_theme = CTheme({<Some styles>})
            my_sub_theme = CTheme(parent="default.light")
            my_external_theme = CTheme().load_from_file("./path/to/a/theme.json")
        This shows examples of creating themes, either from a JSON, a parent theme or a file.

        :param styles: Styles of the theme. When `None`, the default theme's styles are used.
        :param parent: Parent theme
        """
        super().__init__(**kwargs)

        self._data: dict[str, typing.Any] = {}
        self._parent_name: typing.Optional[str] = None

        self["name"] = f"untitled.{len(Theme.LOADED_THEMES) + 1}"
        self["friendly_name"] = f"Untitled theme {len(Theme.LOADED_THEMES) + 1}"
        self["base"] = Theme.STRUCTURAL_PARENT
        self.parent: typing.Union["Theme", None] = parent
        self.children: list["Theme"] = []
        self["is_special"] = False

        if styles is None:
            default_theme = Theme.DEFAULT_THEME
            if default_theme is None:
                warnings.warn(
                    "No default theme is available (the built-in themes may have failed to load), "
                    f"so theme <{self['name']}> starts with empty styles.",
                    RuntimeWarning,
                )
                self["styles"] = {}
            else:
                self["styles"] = default_theme["styles"].copy()
        else:
            self["styles"] = styles
        self["color_palette"] = {}

        Theme.LOADED_THEMES.append(self)
        return

    # region Mapping behaviour

    def __getitem__(self, key: str) -> typing.Any:
        return self._data[key]

    def __setitem__(self, key: str, value: typing.Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """Get a theme data entry, returning default when the key is absent."""
        return self._data.get(key, default)

    def keys(self):
        """Theme data keys."""
        return self._data.keys()

    def values(self):
        """Theme data values."""
        return self._data.values()

    def items(self):
        """Theme data items."""
        return self._data.items()

    def __repr__(self) -> str:
        return f"Theme(name={self.get('name')!r}, keys={sorted(self._data)})"

    # endregion

    @classmethod
    def find_loaded_theme(cls, theme_name: str) -> "Theme | None":
        """Search for a loaded theme by name, returns the CTheme object if found, or None if not.

        Example
        -------
        .. code-block:: python

            DEFAULT_THEME = CTheme.find_loaded_theme("default.light")
        This returns the CTheme object of the default theme to `DEFAULT_THEME`.

        :param theme_name: Name of the theme to load
        :return: The CTheme object if found, otherwise None
        """
        for theme in cls.LOADED_THEMES:
            if theme.get("name") == theme_name:
                return theme
        return None

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
        return cls.find_loaded_theme(theme_name) is not None

    def rename(self, name: str, friendly_name: typing.Optional[str] = None) -> "Theme":
        """Rename the theme.

        :param name: The new theme name
        :param friendly_name: The new friendly name, or None to keep the current one
        :return self: The CTheme itself
        """
        if not isinstance(name, str) or not name:
            raise TypeError(f"Theme name must be a non-empty string, received {name!r}.")
        self["name"] = name
        if friendly_name is not None:
            if not isinstance(friendly_name, str):
                raise TypeError(
                    f"Friendly name must be a string, received {friendly_name!r}."
                    )
            self["friendly_name"] = friendly_name
        return self

    def set_parent(self, base: typing.Optional[str]) -> "Theme":
        """Set the parent of this theme by name.

        The name is looked up right away when the parent is already loaded; otherwise the name is 
        remembered and `resolve_parent()` can attach it later (the built-in theme loader does this 
        in a second pass, so theme files may be loaded in any order).

        :param base: Name of the parent theme, or `None` / `"ROOT"` for no parent
        :return self: The CTheme itself
        """
        if base is not None and not isinstance(base, str):
            raise TypeError(f"Theme parent name must be a string or None, received {base!r}.")
        self["base"] = base
        if base is None or base == self.STRUCTURAL_PARENT:
            self._parent_name = None
            self.parent = None
            return self
        self._parent_name = base
        return self.resolve_parent()

    def resolve_parent(self) -> "Theme":
        """Look up and attach the parent theme recorded by `set_parent()`.

        :return self: The CTheme itself
        """
        if self._parent_name is None:
            return self
        found = type(self).find_loaded_theme(self._parent_name)
        if found is None or found is self:
            if found is self:
                warnings.warn(
                    f"Theme <{self.get('name')}> cannot be its own parent.", RuntimeWarning
                    )
            else:
                warnings.warn(
                    f"Parent theme <{self._parent_name}> of <{self.get('name')}> is not loaded, "
                    "so this theme has no parent for now.",
                    RuntimeWarning,
                )
            self.parent = None
            return self
        self.parent = found
        if self not in found.children:
            found.children.append(self)
        return self

    # region Load theme

    @classmethod
    def _load_internal_theme(cls) -> None:
        """Load internal themes. Should be run once at import, see the end of this file."""
        theme_dir = cls.INTERNAL_THEME_DIR
        if not theme_dir.is_dir():
            warnings.warn(
                f"Internal theme directory {theme_dir} does not exist, so no built-in theme was "
                "loaded and Charmy will fall back to empty styles. This usually means the "
                "`charmy/resources/themes` data files were not installed.",
                RuntimeWarning,
            )
            return

        default_path = theme_dir / f"{cls.DEFAULT_THEME_FILENAME}.json"
        # Load the default theme first, so `Theme()` can use its styles while the rest load
        files = sorted(
            (path for path in theme_dir.iterdir() if path.suffix == ".json"), 
            key = lambda path: path != default_path, 
            )
        if not files:
            warnings.warn(f"No theme JSON file found in {theme_dir}.", RuntimeWarning)
            return

        for path in files:
            try:
                theme = cls.from_file(path)
            except Exception as error:  # A single broken file must not break the import
                warnings.warn(f"Failed to load theme file {path.name}: {error!r}", RuntimeWarning)
                continue
            if theme is None:
                continue
            cls.INTERNAL_THEME[theme["name"]] = theme
            if cls.DEFAULT_THEME is None or path == default_path:
                cls.DEFAULT_THEME = theme

        # Second pass: every theme name is registered by now, so `base` can be resolved
        for theme in cls.INTERNAL_THEME.values():
            theme.resolve_parent()

    @classmethod
    def from_file(cls, file_path: str | pathlib.Path) -> "Theme | None":
        """Load a new theme from a theme file and return it.

        Unlike `load_from_file()`, this never renames an existing theme and never leaves a 
        placeholder behind when the file is rejected: it either returns a ready theme or `None`.

        :param file_path: Path to the theme file
        :return: The loaded CTheme, or None if the file was rejected
        """
        theme_data = _read_theme_json(pathlib.Path(file_path))
        name = theme_data.get("name")
        if not isinstance(name, str) or not name:
            warnings.warn(
                f"Theme file {file_path} has no valid 'name' entry, so it was skipped.", 
                RuntimeWarning, 
                )
            return None
        existing = cls.find_loaded_theme(name)
        if existing is not None:
            warnings.warn(f"Theme <{name}> already loaded or existed.", RuntimeWarning)
            return existing

        theme = cls({})
        theme.load_from_json(theme_data)
        if theme.get("name") != name:
            # `load_from_json()` refused the data, so drop the placeholder we just registered
            if theme in cls.LOADED_THEMES:
                cls.LOADED_THEMES.remove(theme)
            return None
        return theme

    def load_from_file(self, file_path: str | pathlib.Path) -> "Theme | None":
        """Load styles to theme from a file.

        Relative paths are resolved against the directory of the file that calls this method, not 
        against the current working directory.

        Example
        -------
        .. code-block:: python

            my_theme = CTheme().load_from_file("./path/to/a/theme.json")
            my_theme.load_from_file("./path/to/another/theme.json")

        This shows loading a theme to `my_theme` from the theme file at `./path/to/a/theme.json`,
        and change it to theme from `./path/to/another/theme.json` later.

        :param file_path: Path to the theme file
        :return: The CTheme itself, or the already-loaded theme when the name is occupied
        """
        # Change path string into pathlib Path
        if type(file_path) is str:
            file_path = pathlib.Path(file_path)
        # Get path where lies codes calling this function (to support relative path)
        if not file_path.is_absolute():
            frame = inspect.currentframe()
            try:
                outer_frame = inspect.getouterframes(frame)[1]
            finally:
                del frame  # Do not keep the calling frame (and its locals) alive
            caller_file = pathlib.Path(outer_frame.filename).parent
            file_path = (caller_file / file_path).resolve()

        theme_data = _read_theme_json(file_path)
        name = theme_data.get("name")
        if not isinstance(name, str) or not name:
            warnings.warn(
                f"Theme file {file_path} has no valid 'name' entry, so it was not loaded.", 
                RuntimeWarning, 
                )
            return self
        if (existing := type(self).find_loaded_theme(name)) is not None and existing is not self:
            # If name already occupied, meaning the theme might already be loaded
            # (or just simply has an occupied name)
            warnings.warn(f"Theme <{name}> already loaded or existed.", RuntimeWarning)
            return existing

        return self.load_from_json(theme_data)

    def load_from_json(self, theme_data: dict) -> "Theme":
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
        for item, expected_type in self.EXPECTED_DATA_TYPE.items():
            if item not in theme_data:
                warnings.warn(
                    f"Theme data is missing the required <{item}> key, so it will not be loaded "
                    f"to the theme <{self.get('name')}>.",
                    ResourceWarning,
                )
                return self
            if type(theme_data[item]) is not expected_type:
                theme_name = (
                    theme_data["name"] if type(theme_data["name"]) is str else "(Type error)"
                )
                warnings.warn(
                    f"Error data type of <{item}> in theme data that is about to be loaded. "
                    f"Expected {expected_type} but got {type(theme_data[item])}. The json data "
                    f"with theme named <{theme_name}> will not be loaded to the theme "
                    f"<{self.get('name')}>",
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


# Load the built-in themes once, at import.
Theme._load_internal_theme()
