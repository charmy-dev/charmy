"""Regression tests for the defects reported in `CODE_REVIEW.md`.

Each test class names the review item it guards, so a failure points straight back at the report. 
Everything here runs headless — see `tests/conftest.py`.
"""

import pytest

from charmy.styles import texture as tx
from charmy.styles.theme import Theme
from charmy.widgets.button import Button
from charmy.widgets.container import Container


# region P0-5 — the color / texture chain

class TestColorChain:
    """P0-5: colors and textures were silently wrong or raised on valid input."""

    def test_accepts_the_theme_json_alpha_scale(self):
        """Every theme JSON file uses 0-255 alpha; it must normalize to 0.0-1.0."""
        assert tx.Color([40, 130, 255, 255]).color == (40, 130, 255, 1.0)
        assert tx.Color((40, 130, 255, 10)).a == pytest.approx(10 / 255)

    def test_accepts_float_alpha(self):
        assert tx.Color((40, 130, 255, 0.5)).a == 0.5

    def test_int_and_float_alpha_are_never_confused(self):
        assert tx.Color((0, 0, 0, 1)).a == pytest.approx(1 / 255)
        assert tx.Color((0, 0, 0, 1.0)).a == 1.0

    def test_hex_strings(self):
        assert tx.Color("#F00").color == (255, 0, 0, 1.0)
        assert tx.Color("#ff000080").color[:3] == (255, 0, 0)
        assert tx.Color("#ff000080").a == pytest.approx(128 / 255)
        assert tx.Color("00ff00").color == (0, 255, 0, 1.0)

    def test_named_colors(self):
        assert tx.Color("white").color == (255, 255, 255, 1.0)
        assert tx.Color("BLACK").color == (0, 0, 0, 1.0)
        assert tx.Color("gray").color == (128, 128, 128, 1.0)

    def test_unknown_color_raises_instead_of_returning_green(self):
        """The old code silently returned (0, 255, 0, 1) for anything it did not understand."""
        with pytest.raises(ValueError, match="Unknown color"):
            tx.Color("not-a-color")
        with pytest.raises(ValueError, match="transparent"):
            tx.Color("transparent")

    def test_transparent_keyword_none_and_zero_alpha(self):
        assert isinstance(tx.ensure_texture("transparent"), tx.Transparent)
        assert isinstance(tx.ensure_texture("TRANSPARENT"), tx.Transparent)
        assert isinstance(tx.ensure_texture(None), tx.Transparent)
        assert isinstance(tx.ensure_texture([0, 0, 0, 0]), tx.Transparent)
        assert isinstance(tx.ensure_texture((0, 0, 0, 0.0)), tx.Transparent)

    def test_near_transparent_stays_a_color(self):
        assert isinstance(tx.ensure_texture((0, 0, 0, 10)), tx.Color)

    @pytest.mark.parametrize(
        "bad", 
        [
            (1, 2), 
            (1, 2, 3, 4, 5), 
            (0, 0, 299), 
            (0, 0, 0, 300), 
            (0, 0, 0, 2.0), 
            (0, 0, 0, 0.5, 9), 
            "nope", 
            3.5, 
            object(), 
            ], 
        )
    def test_invalid_values_raise(self, bad):
        """`ensure_texture` used to raise UnboundLocalError, or silently accept bad input."""
        with pytest.raises((TypeError, ValueError)):
            tx.ensure_texture(bad)

    def test_is_texture_like_agrees_with_ensure_texture(self):
        """The length test was inverted, so it rejected exactly the valid RGB/RGBA tuples."""
        accepted = [
            (255, 0, 0), (255, 0, 0, 255), (255, 0, 0, 0.5), 
            [255, 0, 0], [255, 0, 0, 128], [255, 0, 0, 128], 
            None, "transparent", "#fff", "#ff000080", "white", 
            ]
        for value in accepted:
            assert tx.Texture.is_texture_like(value) is True, value
            tx.ensure_texture(value)  # must not raise
        rejected = [(1, 2), (1, 2, 3, 4, 5), (0, 0, 0, 300), {}, 3.0, "not-a-color", (True, 0, 0)]
        for value in rejected:
            assert tx.Texture.is_texture_like(value) is False, value

    def test_from_json_accepts_json_arrays(self):
        """JSON decodes arrays to `list`, but the texture layer only accepted `tuple`."""
        assert tx.Texture.from_json({"type": "color", "color": [255, 0, 0, 128]}).color[:3] == (255, 0, 0)
        assert isinstance(tx.Texture.from_json({"type": "transparent"}), tx.Transparent)

    def test_from_json_reports_bad_input_clearly(self):
        with pytest.raises(TypeError, match="not valid JSON"):
            tx.Texture.from_json("linear_gradient")
        with pytest.raises(TypeError, match="no 'type' key"):
            tx.Texture.from_json({})
        with pytest.raises(ValueError, match="Invalid texture type"):
            tx.Texture.from_json({"type": "gaussian_blur"})

    def test_hard_coded_debug_alpha_literals_now_parse(self):
        """These literals live in graphics.py / window.py / genesis.py and used to raise."""
        for literal in [(0, 0, 255, 20), (255, 0, 100, 50), (255, 0, 0, 255)]:
            assert isinstance(tx.ensure_texture(literal), tx.Color)


# region P0-5 — the theme layer

class TestTheme:
    """P0-5: `Theme` could not be instantiated and no built-in theme was ever loaded."""

    def test_builtin_themes_are_loaded_at_import(self):
        """`_load_internal_theme()` was defined but never called."""
        assert Theme.DEFAULT_THEME is not None
        assert set(Theme.INTERNAL_THEME) == {
            "default.light", "default.dark", "sun_valley.light", "sun_valley.dark", 
            }

    def test_default_theme_is_the_light_one(self):
        assert Theme.DEFAULT_THEME is Theme.INTERNAL_THEME["default.light"]
        assert Theme.DEFAULT_THEME["name"] == "default.light"

    def test_base_parent_chain_is_resolved(self):
        """`base: "ROOT"` means no parent; the others must be linked up regardless of file order."""
        assert Theme.INTERNAL_THEME["default.light"].parent is None
        assert Theme.INTERNAL_THEME["default.dark"].parent is Theme.INTERNAL_THEME["default.light"]
        assert Theme.INTERNAL_THEME["sun_valley.light"].parent is Theme.INTERNAL_THEME["default.light"]
        assert Theme.INTERNAL_THEME["sun_valley.dark"].parent is Theme.INTERNAL_THEME["sun_valley.light"]

    def test_theme_is_instantiable(self):
        """`Theme()` used to raise `TypeError: argument after ** must be a mapping, not tuple`."""
        assert Theme() is not None
        assert Theme({"bg": [1, 2, 3]})["styles"] == {"bg": [1, 2, 3]}

    def test_theme_behaves_like_a_mapping(self):
        theme = Theme({"bg": [1, 2, 3]})
        assert theme["styles"] == {"bg": [1, 2, 3]}
        assert "name" in theme
        assert "missing" not in theme
        assert set(theme) >= {"name", "friendly_name", "base", "styles", "color_palette"}
        assert len(theme) == len(list(theme))
        assert theme.get("missing", "fallback") == "fallback"

    def test_default_construction_copies_the_default_styles(self):
        theme = Theme()
        assert theme["styles"] == Theme.DEFAULT_THEME["styles"]
        assert theme["styles"] is not Theme.DEFAULT_THEME["styles"]

    def test_rename_and_set_parent_exist(self):
        """`load_from_json` called both of these, and neither was implemented."""
        theme = Theme({})
        theme.rename("my.theme", "My Theme")
        assert theme["name"] == "my.theme"
        assert theme["friendly_name"] == "My Theme"
        theme.set_parent("default.dark")
        assert theme.parent is Theme.INTERNAL_THEME["default.dark"]
        assert theme in Theme.INTERNAL_THEME["default.dark"].children
        theme.set_parent("ROOT")
        assert theme.parent is None

    def test_unknown_parent_is_deferred_not_fatal(self):
        theme = Theme({})
        with pytest.warns(RuntimeWarning, match="not loaded"):
            theme.set_parent("does.not.exist")
        assert theme.parent is None

    def test_find_and_validate(self):
        assert Theme.find_loaded_theme("default.light") is Theme.DEFAULT_THEME
        assert Theme.find_loaded_theme("nope") is None
        assert Theme.validate_theme_existed("default.light") is True
        assert Theme.validate_theme_existed("nope") is False

    def test_rejects_incomplete_data_without_crashing(self):
        theme = Theme({})
        with pytest.warns(ResourceWarning):
            theme.load_from_json({"name": "broken"})
        assert theme["name"] != "broken"

    def test_rejects_wrongly_typed_data_without_crashing(self):
        theme = Theme({})
        with pytest.warns(ResourceWarning, match="Error data type"):
            theme.load_from_json(
                {
                    "name": "broken", "friendly_name": "Broken", "base": "ROOT", 
                    "styles": "not a dict", "color_palette": {}, 
                    }
                )
        assert theme["name"] != "broken"

    def test_from_file_returns_none_for_a_bad_file(self, theme_file):
        bad = theme_file('{"name": "x"}')
        with pytest.warns(ResourceWarning):
            assert Theme.from_file(bad) is None
        # No placeholder theme is left behind under an "untitled.N" name
        assert Theme.find_loaded_theme("x") is None

    def test_from_file_loads_a_valid_theme(self, theme_file):
        good = theme_file(
            '{"name": "test.custom", "friendly_name": "Test Custom", "base": "default.light", '
            '"styles": {"bg": [1, 2, 3, 255]}, "color_palette": {}}'
            )
        theme = Theme.from_file(good)
        assert theme is not None
        assert theme["name"] == "test.custom"
        assert theme["styles"] == {"bg": [1, 2, 3, 255]}
        assert theme.parent is Theme.INTERNAL_THEME["default.light"]

    def test_from_file_on_a_shipped_theme_returns_the_loaded_one(self):
        """Re-loading a built-in theme must not create a duplicate or an orphan placeholder."""
        shipped = Theme.INTERNAL_THEME_DIR / "sv_2dark.json"
        before = len(Theme.LOADED_THEMES)
        with pytest.warns(RuntimeWarning, match="already loaded"):
            theme = Theme.from_file(shipped)
        assert theme is Theme.INTERNAL_THEME["sun_valley.dark"]
        assert len(Theme.LOADED_THEMES) == before


# region P0-2 — the container child list and the `layers` cache

class TestContainerChildren:
    """P0-2: `layers` was cached against `children` but `add_child` mutated the list in place."""

    def test_newly_added_child_reaches_the_layers(self, headless_window):
        assert headless_window.layers[2] == []  # first access caches the (empty) place layer
        button = Button(headless_window)
        assert button in headless_window.children
        assert headless_window.layers[2] == [button]

    def test_a_child_added_after_a_frame_is_still_drawn(self, headless_window):
        Button(headless_window)
        assert len(headless_window.layers[2]) == 1
        second = Button(headless_window)
        # Reading `layers` in between used to freeze the cache at one child
        assert len(headless_window.layers[2]) == 2
        assert second in headless_window.layers[2]

    def test_destroyed_child_stops_rendering(self, headless_window):
        button = Button(headless_window)
        assert button in headless_window.layers[2]
        button.destroy()
        assert button not in headless_window.children
        assert button not in headless_window.layers[2]

    def test_destroy_is_idempotent(self, headless_window):
        button = Button(headless_window)
        button.destroy()
        button.destroy()
        assert headless_window.children == []

    def test_clear_children_empties_the_list(self, headless_window):
        buttons = [Button(headless_window) for _ in range(3)]
        assert len(headless_window.children) == 3
        headless_window._clear_children()  # used to leave the destroyed children in place
        assert headless_window.children == []
        assert all(not button._alive for button in buttons)

    def test_removing_a_child_keeps_its_siblings(self, headless_window):
        first, second = Button(headless_window), Button(headless_window)
        headless_window.remove_child(first)
        assert headless_window.layers[2] == [second]

    def test_layers_is_invalidated_by_direct_assignment(self, headless_window):
        Button(headless_window)
        assert len(headless_window.layers[2]) == 1
        headless_window.children = []
        assert headless_window.layers[2] == []


# region Integration — the two fixes together

class TestIntegration:
    def test_button_components_build_with_the_repaired_texture_layer(self, headless_window):
        button = Button(headless_window)
        button.place((0, 0), (100, 100))
        shape, text = button._update_components()
        assert isinstance(shape.texture, tx.Color)
        assert isinstance(shape.border_texture, tx.Color)
        assert isinstance(text.texture, tx.Color)

    def test_window_background_accepts_theme_style_values(self, headless_window):
        """Alpha from a theme JSON file is 0-255 and used to raise on assignment."""
        headless_window.background = (240, 240, 240, 255)
        assert isinstance(tx.ensure_texture(headless_window.background), tx.Color)

    def test_container_protocol_still_works(self, headless_window):
        button = Button(headless_window)
        assert button in headless_window
        assert isinstance(headless_window, Container)
        assert headless_window.layers[0] == (255, 255, 255)
