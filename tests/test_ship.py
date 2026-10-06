"""Tests for player ship positioning and movement."""

import pygame
import pytest

from alien_invasion.settings import SHIP_SETTINGS
from alien_invasion.ship import Ship


@pytest.fixture
def ship() -> Ship:
    """Return a ship on the default-size screen."""
    return Ship(pygame.Rect(0, 0, 1200, 800), SHIP_SETTINGS)


def test_ship_starts_at_bottom_center(ship: Ship) -> None:
    assert ship.rect.centerx == ship.screen_rect.centerx
    assert ship.rect.bottom == ship.screen_rect.bottom - ship.bottom_margin


def test_ship_moves_right_and_left(ship: Ship) -> None:
    starting_x = ship.x
    ship.set_movement("right", True)
    ship.update(0.5)
    assert ship.x > starting_x

    ship.set_movement("right", False)
    ship.set_movement("left", True)
    ship.update(0.5)
    assert ship.x == pytest.approx(starting_x)


def test_opposite_directions_cancel_each_other(ship: Ship) -> None:
    starting_x = ship.x
    ship.set_movement("left", True)
    ship.set_movement("right", True)

    ship.update(1.0)

    assert ship.x == starting_x


def test_ship_stays_inside_screen(ship: Ship) -> None:
    ship.set_movement("left", True)
    ship.update(100)
    assert ship.rect.left == ship.screen_rect.left

    ship.stop()
    ship.set_movement("right", True)
    ship.update(100)
    assert ship.rect.right == ship.screen_rect.right


def test_center_resets_position_and_resize_scales_speed(ship: Ship) -> None:
    ship.set_movement("right", True)
    ship.update(0.5)
    ship.center()
    assert ship.rect.centerx == 600

    ship.resize(pygame.Rect(0, 0, 800, 600))
    assert ship.rect.centerx == 400
    assert ship.speed == pytest.approx(280)
    assert not any(ship.movement.values())


def test_unknown_movement_direction_is_rejected(ship: Ship) -> None:
    with pytest.raises(ValueError, match="Unknown movement direction"):
        ship.set_movement("up", True)
