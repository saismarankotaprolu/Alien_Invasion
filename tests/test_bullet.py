"""Tests for player bullet positioning and movement."""

import pygame
import pytest

from alien_invasion.bullet import Bullet
from alien_invasion.settings import BULLET_SETTINGS


def test_bullet_starts_at_ship_position() -> None:
    bullet = Bullet((600, 700), BULLET_SETTINGS, (1200, 800))

    assert bullet.rect.midbottom == (600, 700)


def test_bullet_moves_up_using_delta_time() -> None:
    bullet = Bullet((600, 700), BULLET_SETTINGS, (1200, 800))
    starting_y = bullet.y

    bullet.update(0.5)

    assert bullet.y == pytest.approx(starting_y - 350)
    assert bullet.rect.y == round(bullet.y)


def test_bullet_reports_when_it_leaves_screen() -> None:
    bullet = Bullet((600, 10), BULLET_SETTINGS, (1200, 800))
    assert not bullet.is_off_screen()

    bullet.update(1)

    assert bullet.is_off_screen()


def test_bullet_speed_scales_with_display_height() -> None:
    small_bullet = Bullet((400, 500), BULLET_SETTINGS, (800, 600))
    large_bullet = Bullet((800, 800), BULLET_SETTINGS, (1600, 900))

    assert small_bullet.speed == pytest.approx(525)
    assert large_bullet.speed == pytest.approx(787.5)


def test_bullet_draws_without_changing_its_collision_rect() -> None:
    surface = pygame.Surface((1200, 800))
    bullet = Bullet((600, 700), BULLET_SETTINGS, (1200, 800))
    original_rect = bullet.rect.copy()

    bullet.draw(surface)

    assert bullet.rect == original_rect
