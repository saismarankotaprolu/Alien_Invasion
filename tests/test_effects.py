"""Tests for time-based pixel effects."""

import pygame

from alien_invasion.effects import ShipExplosion


def test_ship_explosion_finishes_after_its_duration() -> None:
    explosion = ShipExplosion((400, 500), duration=0.65, scale=1.0)

    explosion.update(0.3)
    assert not explosion.finished

    explosion.update(0.35)
    assert explosion.finished


def test_ship_explosion_draws_without_moving_its_origin() -> None:
    surface = pygame.Surface((800, 600))
    explosion = ShipExplosion((400, 500), duration=0.65, scale=1.0)

    explosion.update(0.2)
    explosion.draw(surface)

    assert explosion.center == (400, 500)
    assert len(explosion.particles) == 28
