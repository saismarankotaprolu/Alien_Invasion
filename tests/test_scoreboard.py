"""Tests for score and status rendering."""

import pygame

from alien_invasion.scoreboard import Scoreboard


def test_score_format_uses_thousands_separators() -> None:
    assert Scoreboard.format_score(0) == "0"
    assert Scoreboard.format_score(1250) == "1,250"


def test_scoreboard_refreshes_when_statistics_change() -> None:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    stats = {
        "score": 0,
        "high_score": 0,
        "level": 1,
        "ships_left": 3,
    }
    scoreboard = Scoreboard(screen, stats)
    original_images = scoreboard.images

    scoreboard.draw()
    assert scoreboard.images is original_images

    stats["score"] = 50
    scoreboard.draw()
    assert scoreboard.images is not original_images
    pygame.quit()
