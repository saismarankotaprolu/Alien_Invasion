"""Tests for application navigation and settings."""

import pygame

from alien_invasion.game import AlienInvasion


def test_game_starts_on_menu() -> None:
    game = AlienInvasion()

    assert game.current_screen == "menu"
    assert set(game.buttons) == {"game_options", "settings", "quit"}

    pygame.quit()


def test_menu_actions_change_screens() -> None:
    game = AlienInvasion()

    game.handle_action("play")
    assert game.current_screen == "game"
    assert game.ship.rect.centerx == game.screen.get_rect().centerx
    assert game.aliens
    assert game.game_stats["game_active"]

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

    game._handle_gameplay_key(pygame.K_d, True)
    game._update(0.1)

    assert game.ship.rect.centerx > game.screen.get_rect().centerx

    game._handle_gameplay_key(pygame.K_d, False)
    assert not game.ship.movement["right"]
    pygame.quit()


def test_spacebar_fires_with_cooldown() -> None:
    game = AlienInvasion()
    game.handle_action("play")

    game._handle_gameplay_key(pygame.K_SPACE, True)
    assert len(game.bullets) == 1

    game._update(0.1)
    assert len(game.bullets) == 1

    game._update(0.16)
    assert len(game.bullets) == 2
    pygame.quit()


def test_active_bullet_limit_and_reset() -> None:
    game = AlienInvasion()
    game.handle_action("play")

    for _ in range(5):
        game.fire_cooldown_remaining = 0
        game._try_fire_bullet()

    assert len(game.bullets) == 3

    game.handle_action("menu")
    assert game.bullets == []
    assert game.aliens == []
    assert not game.firing
    pygame.quit()


def test_bullet_collision_removes_one_alien_and_bullet() -> None:
    game = AlienInvasion()
    game.handle_action("play")
    original_alien_count = len(game.aliens)
    game._try_fire_bullet()
    game.bullets[0].rect.center = game.aliens[0].rect.center

    game._resolve_bullet_collisions()

    assert len(game.aliens) == original_alien_count - 1
    assert game.bullets == []
    assert game.game_stats["score"] == 50
    assert game.game_stats["high_score"] == 50
    pygame.quit()


def test_empty_fleet_is_recreated_after_final_hit() -> None:
    game = AlienInvasion()
    game.handle_action("play")
    final_alien = game.aliens[0]
    game.aliens = [final_alien]
    game._try_fire_bullet()
    game.bullets[0].rect.center = final_alien.rect.center

    game._resolve_bullet_collisions()

    assert len(game.aliens) > 1
    assert game.bullets == []
    assert game.fleet_direction == 1
    assert game.game_stats["score"] == 300
    assert game.game_stats["level"] == 2
    pygame.quit()


def test_alien_ship_collision_removes_one_ship_then_resets_fleet() -> None:
    game = AlienInvasion()
    game.handle_action("play")
    original_fleet_size = len(game.aliens)
    colliding_alien = game.aliens[0]
    colliding_alien.rect.center = game.ship.rect.center

    game._check_alien_threats()

    assert game.game_stats["ships_left"] == 3
    assert game.aliens == []
    assert game.explosion is not None

    game._update(0.65)
    assert game.game_stats["ships_left"] == 2
    assert game.recovery_remaining > 0

    game._update(0.35)
    assert len(game.aliens) == original_fleet_size
    assert colliding_alien not in game.aliens
    pygame.quit()


def test_alien_reaching_earth_resets_fleet() -> None:
    game = AlienInvasion()
    game.handle_action("play")
    invading_alien = game.aliens[0]
    invading_alien.rect.bottom = game.screen.get_rect().bottom

    game._check_alien_threats()

    assert game.game_stats["ships_left"] == 3
    assert game.aliens == []
    assert game.explosion is not None

    game._update(0.65)
    game._update(0.35)
    assert invading_alien not in game.aliens
    assert len(game.aliens) == 48
    assert game.fleet_direction == 1
    pygame.quit()


def test_multiple_threat_checks_during_recovery_remove_only_one_ship() -> None:
    game = AlienInvasion()
    game.handle_action("play")

    game._handle_ship_hit()
    game._handle_ship_hit()

    assert game.game_stats["ships_left"] == 3
    game._update(0.65)
    assert game.game_stats["ships_left"] == 2

    game._handle_ship_hit()
    assert game.game_stats["ships_left"] == 2
    pygame.quit()


def test_final_ship_loss_ends_game() -> None:
    game = AlienInvasion()
    game.handle_action("play")
    game.game_stats["ships_left"] = 1

    game._handle_ship_hit()

    assert game.game_stats["game_active"]
    assert game.explosion is not None

    game._update(0.65)
    assert not game.game_stats["game_active"]
    assert game.game_stats["ships_left"] == 0
    assert set(game.buttons) == {"play_again", "menu"}
    pygame.quit()


def test_pause_freezes_gameplay_and_time_attack_timer() -> None:
    game = AlienInvasion()
    game.game_options["mode"] = "Time Attack"
    game.handle_action("play")
    ship_x = game.ship.x

    game.ship.set_movement("right", True)
    game._handle_escape()
    game._update(1.0)

    assert game.paused
    assert game.ship.x == ship_x
    assert game.game_stats["time_remaining"] == 120
    assert set(game.buttons) == {"resume", "restart", "menu"}

    game.handle_action("resume")
    assert not game.paused
    assert game.buttons == {}
    pygame.quit()


def test_weapon_charge_tracks_firing_cooldown() -> None:
    game = AlienInvasion()
    game.handle_action("play")
    assert game._weapon_charge() == 1.0

    game._try_fire_bullet()
    assert game._weapon_charge() == 0.0

    game.fire_cooldown_remaining /= 2
    assert game._weapon_charge() == 0.5
    pygame.quit()


def test_keyboard_can_navigate_and_activate_menu_buttons() -> None:
    game = AlienInvasion()
    assert game.selected_button_index == 0

    assert game._handle_ui_key(pygame.K_DOWN)
    assert game.selected_button_index == 1

    assert game._handle_ui_key(pygame.K_RETURN)
    assert game.current_screen == "settings"
    pygame.quit()


def test_play_again_resets_game_but_preserves_high_score() -> None:
    game = AlienInvasion()
    game.handle_action("play")
    game._add_score(1_250)
    game.game_stats["level"] = 4
    game.game_stats["ships_left"] = 0
    game._end_game()

    game.handle_action("play_again")

    assert game.game_stats["score"] == 0
    assert game.game_stats["high_score"] == 1_250
    assert game.game_stats["level"] == 1
    assert game.game_stats["ships_left"] == 3
    assert game.game_stats["game_active"]
    assert game.game_stats["time_remaining"] is None
    pygame.quit()
