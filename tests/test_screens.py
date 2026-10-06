"""Tests for procedural screen rendering."""

import pygame

from alien_invasion.screens import create_space_background


def test_background_matches_requested_size() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))

    background = create_space_background((800, 600), "Earth Orbit")

    assert background.get_size() == (800, 600)
    pygame.quit()


def test_earth_orbit_has_blue_atmospheric_glow() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    background = create_space_background((800, 600), "Earth Orbit")

    top_pixel = background.get_at((400, 0))
    bottom_pixel = background.get_at((400, 599))

    assert bottom_pixel.b > top_pixel.b
    assert bottom_pixel.b > bottom_pixel.r
    pygame.quit()
