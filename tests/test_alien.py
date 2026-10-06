"""Tests for individual alien behavior."""

import pygame
import pytest

from alien_invasion.alien import Alien
from alien_invasion.settings import ALIEN_SETTINGS


def test_alien_moves_in_shared_direction() -> None:
    alien = Alien((100, 80), ALIEN_SETTINGS, (1200, 800))

    alien.update(1, 0.5)
    assert alien.x == pytest.approx(145)

    alien.update(-1, 0.5)
    assert alien.x == pytest.approx(100)


def test_alien_drops_without_changing_horizontal_position() -> None:
    alien = Alien((100, 80), ALIEN_SETTINGS, (1200, 800))

    alien.drop(24)

    assert alien.rect.topleft == (100, 104)
    assert alien.x == 100


def test_alien_detects_screen_edges() -> None:
    screen_rect = pygame.Rect(0, 0, 1200, 800)
    alien = Alien((0, 80), ALIEN_SETTINGS, screen_rect.size)
    assert alien.reached_edge(screen_rect)

    alien.rect.right = screen_rect.right
    alien.x = float(alien.rect.x)
    assert alien.reached_edge(screen_rect)
