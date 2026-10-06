"""Tests for application navigation and settings."""

import pygame

from alien_invasion.game import AlienInvasion


def test_game_starts_on_menu() -> None:
    game = AlienInvasion()

    assert game.current_screen == "menu"
    assert set(game.buttons) == {"play", "settings", "quit"}

    pygame.quit()


def test_menu_actions_change_screens() -> None:
    game = AlienInvasion()

    game.handle_action("play")
    assert game.current_screen == "game"

    game.handle_action("menu")
    game.handle_action("settings")
    assert game.current_screen == "settings"

    pygame.quit()


def test_apply_changes_resolution_and_background() -> None:
    game = AlienInvasion()
    game.handle_action("settings")
    game.pending_settings = {
        "resolution": (800, 600),
        "background": "Deep Space",
    }

    game.handle_action("apply")

    assert game.screen.get_size() == (800, 600)
    assert game.user_settings["background"] == "Deep Space"
    assert game.status_message == "Settings applied"

    pygame.quit()


def test_run_can_stop_after_one_frame() -> None:
    game = AlienInvasion()

    assert game.run(max_frames=1) == 0
    assert not pygame.get_init()
