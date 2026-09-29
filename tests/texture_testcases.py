"""Regression tests for issues in the texture and color layers.

This file intentionally stays focused on the rendering primitives that are stable
and independent from theme or widget API churn.

This is a vibed module.
"""

import pytest

from charmy.styles import texture as tx


# region P0-5 — the color / texture chain

class TestColorChain:
    """P0-5: colors and textures were silently wrong or raised on valid input."""

    def test_accepts_the_theme_json_alpha_scale(self):
        """Theme JSON stores alpha in 0-255; textures must normalize to 0.0-1.0."""
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
            tx.ensure_texture(value)
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

    def test_linear_gradient_interpolates_rgb_and_alpha(self):
        gradient = tx.LinearGradient((0, 0), (10, 0), {
            0: (0, 0, 0, 0.0),
            1: (255, 255, 255, 1.0),
        })

        assert gradient.get_color_at_ratio(0.5) == (127, 127, 127, 0.5)
        assert gradient.get_color_at_point((5, 0)).color == (127, 127, 127, 0.5)
        assert gradient.get_color_at_point((0, 0)).color == (0, 0, 0, 0.0)
        assert gradient.get_color_at_point((10, 0)).color == (255, 255, 255, 1.0)
