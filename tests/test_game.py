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
    assert game.ship.rect.centerx == game.screen.get_rect().centerx

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
    assert game.ship.screen_rect == game.screen.get_rect()

    pygame.quit()


def test_run_can_stop_after_one_frame() -> None:
    game = AlienInvasion()

    assert game.run(max_frames=1) == 0
    assert not pygame.get_init()


def test_game_processes_ship_movement_keys() -> None:
    game = AlienInvasion()
    game.handle_action("play")

    game._handle_movement_key(pygame.K_d, True)
    game._update(0.1)

    assert game.ship.rect.centerx > game.screen.get_rect().centerx

    game._handle_movement_key(pygame.K_d, False)
    assert not game.ship.movement["right"]
    pygame.quit()
