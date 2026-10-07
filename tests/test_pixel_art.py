"""Tests for procedural pixel-art HUD assets."""

from alien_invasion.pixel_art import PIXEL_PATTERNS, create_pixel_icon


def test_every_pixel_icon_has_content() -> None:
    for name in PIXEL_PATTERNS:
        icon = create_pixel_icon(name, pixel_size=3)

        assert icon.get_width() > 0
        assert icon.get_height() > 0
        assert icon.get_bounding_rect().width > 0


def test_pixel_icons_scale_with_nearest_square_units() -> None:
    small_icon = create_pixel_icon("ship", pixel_size=2)
    large_icon = create_pixel_icon("ship", pixel_size=4)

    assert large_icon.get_width() == small_icon.get_width() * 2
    assert large_icon.get_height() == small_icon.get_height() * 2
