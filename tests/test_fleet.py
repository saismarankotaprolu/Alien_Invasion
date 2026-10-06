"""Tests for alien fleet creation and movement."""

import pygame

from alien_invasion.fleet import create_fleet, update_fleet
from alien_invasion.settings import ALIEN_SETTINGS


def test_fleet_has_consistent_size_at_supported_resolutions() -> None:
    for size in [(800, 600), (1200, 800), (1600, 900)]:
        aliens = create_fleet(pygame.Rect((0, 0), size), ALIEN_SETTINGS)

        assert len(aliens) == 48
        assert all(pygame.Rect((0, 0), size).contains(alien.rect) for alien in aliens)


def test_fleet_aliens_do_not_overlap() -> None:
    aliens = create_fleet(pygame.Rect(0, 0, 1200, 800), ALIEN_SETTINGS)

    for index, alien in enumerate(aliens):
        assert not any(
            alien.rect.colliderect(other.rect) for other in aliens[index + 1 :]
        )


def test_fleet_moves_as_one_group() -> None:
    screen_rect = pygame.Rect(0, 0, 1200, 800)
    aliens = create_fleet(screen_rect, ALIEN_SETTINGS)
    starting_positions = [alien.x for alien in aliens]

    direction = update_fleet(
        aliens,
        1,
        screen_rect,
        ALIEN_SETTINGS,
        0.5,
    )

    assert direction == 1
    assert all(
        alien.x > starting_x for alien, starting_x in zip(aliens, starting_positions)
    )


def test_fleet_drops_and_reverses_at_edge() -> None:
    screen_rect = pygame.Rect(0, 0, 1200, 800)
    aliens = create_fleet(screen_rect, ALIEN_SETTINGS)
    rightmost = max(aliens, key=lambda alien: alien.rect.right)
    horizontal_shift = screen_rect.right - rightmost.rect.right
    for alien in aliens:
        alien.rect.x += horizontal_shift
        alien.x = float(alien.rect.x)
    starting_y_positions = [alien.rect.y for alien in aliens]

    direction = update_fleet(
        aliens,
        1,
        screen_rect,
        ALIEN_SETTINGS,
        0.1,
    )

    assert direction == -1
    assert all(
        alien.rect.y > starting_y
        for alien, starting_y in zip(aliens, starting_y_positions)
    )
