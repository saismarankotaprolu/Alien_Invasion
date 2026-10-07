"""Tests for difficulty progression and game modes."""

import pygame
import pytest

from alien_invasion.game import AlienInvasion
from alien_invasion.settings import DEFAULT_GAME_OPTIONS


def test_game_options_defaults_and_selection_screen() -> None:
    game = AlienInvasion()

    assert game.game_options == DEFAULT_GAME_OPTIONS

    game.handle_action("game_options")
    assert game.current_screen == "game_options"
    assert set(game.buttons) == {
        "mode_previous",
        "mode_next",
        "difficulty_previous",
        "difficulty_next",
        "start_game",
        "menu",
    }
    pygame.quit()


def test_mode_and_difficulty_options_wrap() -> None:
    game = AlienInvasion()
    game.handle_action("game_options")

    game.handle_action("mode_previous")
    game.handle_action("difficulty_previous")

    assert game.game_options == {
        "mode": "Time Attack",
        "difficulty": "Easy",
    }
    pygame.quit()


@pytest.mark.parametrize(
    ("difficulty", "ships", "speed"),
    [("Easy", 5, 70), ("Normal", 3, 90), ("Hard", 2, 120)],
)
def test_difficulty_sets_starting_ships_and_speed(
    difficulty: str,
    ships: int,
    speed: int,
) -> None:
    game = AlienInvasion()
    game.game_options["difficulty"] = difficulty

    game.handle_action("play")

    assert game.game_stats["ships_left"] == ships
    assert game.aliens[0].speed == pytest.approx(speed)
    pygame.quit()


def test_fleet_speed_grows_by_level_and_stops_at_cap() -> None:
    game = AlienInvasion()
    game.handle_action("play")
    level_one_speed = game.aliens[0].speed

    game.game_stats["level"] = 2
    game._start_new_fleet()
    assert game.aliens[0].speed == pytest.approx(level_one_speed * 1.12)

    game.game_stats["level"] = 100
    game._start_new_fleet()
    assert game.aliens[0].speed == pytest.approx(260)
    pygame.quit()


@pytest.mark.parametrize(
    ("difficulty", "expected_points"),
    [("Easy", 40), ("Normal", 50), ("Hard", 75)],
)
def test_difficulty_applies_score_multiplier(
    difficulty: str,
    expected_points: int,
) -> None:
    game = AlienInvasion()
    game.game_options["difficulty"] = difficulty
    game.handle_action("play")
    game._try_fire_bullet()
    game.bullets[0].rect.center = game.aliens[0].rect.center

    game._resolve_bullet_collisions()

    assert game.game_stats["score"] == expected_points
    pygame.quit()


def test_classic_mode_has_no_timer() -> None:
    game = AlienInvasion()
    game.handle_action("play")

    assert game.game_stats["time_remaining"] is None
    pygame.quit()


def test_time_attack_ends_when_timer_expires() -> None:
    game = AlienInvasion()
    game.game_options["mode"] = "Time Attack"
    game.handle_action("play")

    assert game.game_stats["time_remaining"] == 120
    game._update(120)

    assert game.game_stats["time_remaining"] == 0
    assert not game.game_stats["game_active"]
    assert game.game_stats["end_reason"] == "Time expired"
    pygame.quit()


def test_time_attack_timer_pauses_during_ship_recovery() -> None:
    game = AlienInvasion()
    game.game_options["mode"] = "Time Attack"
    game.handle_action("play")
    game._handle_ship_hit()

    game._update(0.5)

    assert game.game_stats["time_remaining"] == 120
    pygame.quit()


def test_high_scores_are_separate_for_each_game_configuration() -> None:
    game = AlienInvasion()
    game.handle_action("play")
    game._add_score(500)
    game.handle_action("menu")

    game.game_options.update({"mode": "Time Attack", "difficulty": "Hard"})
    game.handle_action("play")

    assert game.game_stats["high_score"] == 0
    assert game.high_scores[("Classic", "Normal")] == 500
    assert game.high_scores[("Time Attack", "Hard")] == 0
    pygame.quit()


def test_options_cannot_change_during_active_game() -> None:
    game = AlienInvasion()
    game.handle_action("play")

    game._cycle_game_option("difficulty", 1)

    assert game.game_options["difficulty"] == "Normal"
    pygame.quit()
