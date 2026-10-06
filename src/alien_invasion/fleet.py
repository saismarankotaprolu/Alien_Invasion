"""Helpers for creating and moving the alien fleet."""

from typing import Any

import pygame

from alien_invasion.alien import Alien


def display_scale(display_size: tuple[int, int]) -> float:
    """Return the shared visual scale for a supported display size."""
    width, height = display_size
    return max(0.75, min(width / 1200, height / 800))


def create_fleet(
    screen_rect: pygame.Rect,
    settings: dict[str, Any],
) -> list[Alien]:
    """Create a centered grid of aliens that fits the display."""
    scale = display_scale(screen_rect.size)
    alien_width = round(settings["width"] * scale)
    alien_height = round(settings["height"] * scale)
    horizontal_gap = round(settings["horizontal_gap"] * scale)
    vertical_gap = round(settings["vertical_gap"] * scale)
    side_margin = round(settings["side_margin"] * scale)
    top_margin = round(settings["top_margin"] * scale)

    available_width = screen_rect.width - (2 * side_margin)
    fitting_columns = max(
        1,
        (available_width + horizontal_gap) // (alien_width + horizontal_gap),
    )
    columns = min(settings["columns"], fitting_columns)
    rows = settings["rows"]

    fleet_width = columns * alien_width + (columns - 1) * horizontal_gap
    start_x = screen_rect.left + (screen_rect.width - fleet_width) // 2

    aliens = []
    for row in range(rows):
        y = screen_rect.top + top_margin + row * (alien_height + vertical_gap)
        for column in range(columns):
            x = start_x + column * (alien_width + horizontal_gap)
            aliens.append(Alien((x, y), settings, screen_rect.size))
    return aliens


def update_fleet(
    aliens: list[Alien],
    direction: int,
    screen_rect: pygame.Rect,
    settings: dict[str, Any],
    delta_time: float,
) -> int:
    """Move the fleet, dropping and reversing it at a screen edge."""
    if any(alien.reached_edge(screen_rect) for alien in aliens):
        drop_distance = round(
            settings["drop_distance"] * display_scale(screen_rect.size)
        )
        for alien in aliens:
            alien.drop(drop_distance)
        direction *= -1

    for alien in aliens:
        alien.update(direction, delta_time)
    return direction
