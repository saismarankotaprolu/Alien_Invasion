"""Tests for safe preference and high-score persistence."""

import json
from pathlib import Path

import pygame

from alien_invasion.game import AlienInvasion
from alien_invasion.storage import load_game_data, save_game_data


def test_storage_round_trip(tmp_path: Path) -> None:
    save_path = tmp_path / "save" / "settings.json"
    data = {"resolution": [800, 600], "background": "Deep Space"}

    assert save_game_data(save_path, data)
    assert load_game_data(save_path) == data
    assert not save_path.with_suffix(".tmp").exists()


def test_damaged_save_file_falls_back_safely(tmp_path: Path) -> None:
    save_path = tmp_path / "settings.json"
    save_path.write_text("{damaged", encoding="utf-8")

    assert load_game_data(save_path) == {}


def test_game_restores_valid_preferences_and_high_scores(tmp_path: Path) -> None:
    save_path = tmp_path / "settings.json"
    game = AlienInvasion(save_path=save_path)
    game.user_settings = {
        "resolution": (800, 600),
        "background": "Deep Space",
    }
    game.game_options = {"mode": "Time Attack", "difficulty": "Hard"}
    game.high_scores[("Time Attack", "Hard")] = 4_250
    assert game._save_progress()
    pygame.quit()

    restored_game = AlienInvasion(save_path=save_path)

    assert restored_game.user_settings == {
        "resolution": (800, 600),
        "background": "Deep Space",
    }
    assert restored_game.game_options == {
        "mode": "Time Attack",
        "difficulty": "Hard",
    }
    assert restored_game.high_scores[("Time Attack", "Hard")] == 4_250
    pygame.quit()


def test_invalid_saved_values_use_defaults(tmp_path: Path) -> None:
    save_path = tmp_path / "settings.json"
    save_path.write_text(
        json.dumps(
            {
                "resolution": [1, 1],
                "background": "Missing",
                "mode": "Unknown",
                "difficulty": "Impossible",
            }
        ),
        encoding="utf-8",
    )

    game = AlienInvasion(save_path=save_path)

    assert game.user_settings["resolution"] == (1200, 800)
    assert game.user_settings["background"] == "Earth Orbit"
    assert game.game_options == {"mode": "Classic", "difficulty": "Normal"}
    pygame.quit()
