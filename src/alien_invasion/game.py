"""Application and entry point for Alien Invasion."""

from typing import Any, Optional

import pygame

from alien_invasion.alien import Alien
from alien_invasion.bullet import Bullet
from alien_invasion.fleet import create_fleet, update_fleet
from alien_invasion.scoreboard import Scoreboard
from alien_invasion.screens import create_space_background, draw_panel, draw_text
from alien_invasion.settings import (
    ALIEN_SETTINGS,
    BACKGROUND_THEMES,
    BULLET_SETTINGS,
    COLORS,
    DEFAULT_GAME_OPTIONS,
    DEFAULT_USER_SETTINGS,
    DIFFICULTIES,
    FPS,
    GAME_MODES,
    GAMEPLAY_SETTINGS,
    RESOLUTIONS,
    SCORING_SETTINGS,
    SHIP_SETTINGS,
    TITLE,
    copy_user_settings,
    cycle_value,
)
from alien_invasion.ship import Ship
from alien_invasion.ui import Button


class AlienInvasion:
    """Manage application state, events, and screen drawing."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.user_settings = copy_user_settings(DEFAULT_USER_SETTINGS)
        self.pending_settings = copy_user_settings(self.user_settings)
        self.screen = pygame.display.set_mode(self.user_settings["resolution"])
        self.clock = pygame.time.Clock()
        self.ship = Ship(self.screen.get_rect(), SHIP_SETTINGS)
        self.bullets: list[Bullet] = []
        self.aliens: list[Alien] = []
        self.fleet_direction = 1
        self.firing = False
        self.fire_cooldown_remaining = 0.0
        self.recovery_remaining = 0.0
        self.game_options = dict(DEFAULT_GAME_OPTIONS)
        self.high_scores = {
            (mode, difficulty): 0 for mode in GAME_MODES for difficulty in DIFFICULTIES
        }
        self.game_stats = {
            "score": 0,
            "high_score": 0,
            "level": 1,
            "ships_left": DIFFICULTIES[DEFAULT_GAME_OPTIONS["difficulty"]][
                "starting_ships"
            ],
            "game_active": False,
            "time_remaining": None,
            "end_reason": "",
        }
        self.active_alien_settings = dict(ALIEN_SETTINGS)
        self.scoreboard = Scoreboard(self.screen, self.game_stats)
        self.current_screen = "menu"
        self.running = True
        self.status_message = ""

        self.fonts: dict[str, pygame.font.Font] = {}
        self.buttons: dict[str, Button] = {}
        self.backgrounds: dict[tuple[tuple[int, int], str], pygame.Surface] = {}
        self._build_interface()

    def run(self, max_frames: Optional[int] = None) -> int:
        """Run the main loop until the player quits."""
        frame_count = 0
        try:
            while self.running:
                delta_time = min(self.clock.tick(FPS) / 1000, 0.05)
                self._process_events()
                self._update(delta_time)
                self._draw_current_screen()
                pygame.display.flip()

                frame_count += 1
                if max_frames is not None and frame_count >= max_frames:
                    self.running = False
        finally:
            pygame.quit()
        return 0

    def _process_events(self) -> None:
        """Handle window, keyboard, and pointer events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._handle_escape()
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                self._handle_gameplay_key(event.key, event.type == pygame.KEYDOWN)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._handle_click(event.pos)

    def _handle_gameplay_key(self, key: int, active: bool) -> None:
        """Update ship movement and firing from keyboard controls."""
        if (
            self.current_screen != "game"
            or not self.game_stats["game_active"]
            or self.recovery_remaining > 0
        ):
            return
        if key in (pygame.K_LEFT, pygame.K_a):
            self.ship.set_movement("left", active)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.ship.set_movement("right", active)
        elif key == pygame.K_SPACE:
            was_firing = self.firing
            self.firing = active
            if active and not was_firing:
                self._try_fire_bullet()

    def _update(self, delta_time: float) -> None:
        """Update active gameplay objects."""
        if self.current_screen != "game" or not self.game_stats["game_active"]:
            return

        if self.recovery_remaining > 0:
            self.recovery_remaining = max(0.0, self.recovery_remaining - delta_time)
            if self.recovery_remaining == 0:
                self._start_new_fleet()
            return

        if self._update_timer(delta_time):
            return

        self.ship.update(delta_time)
        self.fire_cooldown_remaining = max(
            0.0,
            self.fire_cooldown_remaining - delta_time,
        )
        if self.firing:
            self._try_fire_bullet()

        for bullet in self.bullets:
            bullet.update(delta_time)
        self.bullets = [bullet for bullet in self.bullets if not bullet.is_off_screen()]

        self.fleet_direction = update_fleet(
            self.aliens,
            self.fleet_direction,
            self.screen.get_rect(),
            self.active_alien_settings,
            delta_time,
        )
        self._resolve_bullet_collisions()
        self._check_alien_threats()

    def _resolve_bullet_collisions(self) -> None:
        """Remove bullets and aliens that collide with each other."""
        hit_bullets: list[Bullet] = []
        hit_aliens: list[Alien] = []

        for bullet in self.bullets:
            for alien in self.aliens:
                if alien in hit_aliens:
                    continue
                if bullet.rect.colliderect(alien.rect):
                    hit_bullets.append(bullet)
                    hit_aliens.append(alien)
                    break

        if not hit_aliens:
            return

        self.bullets = [bullet for bullet in self.bullets if bullet not in hit_bullets]
        self.aliens = [alien for alien in self.aliens if alien not in hit_aliens]
        level = self.game_stats["level"]
        difficulty = DIFFICULTIES[self.game_options["difficulty"]]
        alien_points = round(
            SCORING_SETTINGS["alien_points"] * level * difficulty["score_multiplier"]
        )
        self._add_score(len(hit_aliens) * alien_points)

        if not self.aliens:
            fleet_bonus = round(
                SCORING_SETTINGS["fleet_bonus"] * level * difficulty["score_multiplier"]
            )
            self._add_score(fleet_bonus)
            self.game_stats["level"] += 1
            self._start_new_fleet()

    def _add_score(self, points: int) -> None:
        """Add points and update the session high score."""
        self.game_stats["score"] += points
        self.game_stats["high_score"] = max(
            self.game_stats["high_score"],
            self.game_stats["score"],
        )
        score_key = (
            self.game_options["mode"],
            self.game_options["difficulty"],
        )
        self.high_scores[score_key] = self.game_stats["high_score"]

    def _update_timer(self, delta_time: float) -> bool:
        """Advance Time Attack and end the game when time expires."""
        time_remaining = self.game_stats["time_remaining"]
        if time_remaining is None:
            return False

        self.game_stats["time_remaining"] = max(0.0, time_remaining - delta_time)
        if self.game_stats["time_remaining"] == 0:
            self._end_game("Time expired")
            return True
        return False

    def _check_alien_threats(self) -> None:
        """Remove a ship if aliens hit the player or reach Earth."""
        if self.recovery_remaining > 0 or not self.game_stats["game_active"]:
            return
        ship_was_hit = any(
            alien.rect.colliderect(self.ship.rect) for alien in self.aliens
        )
        earth_was_reached = any(
            alien.rect.bottom >= self.screen.get_rect().bottom for alien in self.aliens
        )
        if ship_was_hit or earth_was_reached:
            self._handle_ship_hit()

    def _handle_ship_hit(self) -> None:
        """Remove one ship and begin recovery or end the game."""
        if self.recovery_remaining > 0 or not self.game_stats["game_active"]:
            return

        self.game_stats["ships_left"] -= 1
        self._clear_bullets()
        self._clear_aliens()
        self.ship.stop()
        self.ship.center()

        if self.game_stats["ships_left"] <= 0:
            self._end_game("No ships remaining")
            return

        self.recovery_remaining = GAMEPLAY_SETTINGS["ship_recovery_ms"] / 1000

    def _end_game(self, reason: str = "Game ended") -> None:
        """Stop gameplay and show the game-over controls."""
        self.game_stats["game_active"] = False
        self.game_stats["end_reason"] = reason
        self.recovery_remaining = 0.0
        self._clear_bullets()
        self._clear_aliens()
        self.ship.stop()
        self._build_interface()

    def _start_new_fleet(self) -> None:
        """Reset the play area and create a full fleet for the current level."""
        self._clear_bullets()
        self.ship.stop()
        self.ship.center()
        self.fleet_direction = 1
        self.active_alien_settings = self._alien_settings_for_level()
        self.aliens = create_fleet(
            self.screen.get_rect(),
            self.active_alien_settings,
        )

    def _alien_settings_for_level(self) -> dict[str, Any]:
        """Build alien settings for the selected difficulty and level."""
        difficulty = DIFFICULTIES[self.game_options["difficulty"]]
        level = self.game_stats["level"]
        fleet_speed = min(
            difficulty["alien_base_speed"] * difficulty["speed_growth"] ** (level - 1),
            difficulty["alien_max_speed"],
        )
        settings: dict[str, Any] = dict(ALIEN_SETTINGS)
        settings["horizontal_speed"] = fleet_speed
        settings["drop_distance"] = difficulty["drop_distance"]
        return settings

    def _clear_aliens(self) -> None:
        """Remove the current fleet and reset its direction."""
        self.aliens.clear()
        self.fleet_direction = 1

    def _try_fire_bullet(self) -> None:
        """Create a bullet when the cooldown and active-bullet limit allow it."""
        if not self.game_stats["game_active"] or self.recovery_remaining > 0:
            return
        if self.fire_cooldown_remaining > 0:
            return
        if len(self.bullets) >= BULLET_SETTINGS["max_active"]:
            return

        self.bullets.append(
            Bullet(
                self.ship.rect.midtop,
                BULLET_SETTINGS,
                self.screen.get_size(),
            )
        )
        self.fire_cooldown_remaining = BULLET_SETTINGS["cooldown_ms"] / 1000

    def _clear_bullets(self) -> None:
        """Remove active projectiles and reset the firing state."""
        self.bullets.clear()
        self.firing = False
        self.fire_cooldown_remaining = 0.0

    def _handle_escape(self) -> None:
        """Return to the menu, or exit when already on the menu."""
        if self.current_screen == "menu":
            self.running = False
        else:
            self.ship.stop()
            self._clear_bullets()
            self._clear_aliens()
            self.game_stats["game_active"] = False
            self.recovery_remaining = 0.0
            self.current_screen = "menu"
            self.pending_settings = copy_user_settings(self.user_settings)
            self.status_message = ""
            self._build_interface()

    def _handle_click(self, position: tuple[int, int]) -> None:
        """Run the action belonging to the clicked button."""
        for action, button in self.buttons.items():
            if button.contains(position):
                self.handle_action(action)
                break

    def handle_action(self, action: str) -> None:
        """Apply a named menu action."""
        actions = {
            "game_options": self._show_game_options,
            "play": self._show_game,
            "play_again": self._show_game,
            "start_game": self._show_game,
            "settings": self._show_settings,
            "quit": self._quit,
            "menu": self._show_menu,
            "resolution_previous": lambda: self._cycle_resolution(-1),
            "resolution_next": lambda: self._cycle_resolution(1),
            "background_previous": lambda: self._cycle_background(-1),
            "background_next": lambda: self._cycle_background(1),
            "apply": self._apply_settings,
            "mode_previous": lambda: self._cycle_game_option("mode", -1),
            "mode_next": lambda: self._cycle_game_option("mode", 1),
            "difficulty_previous": lambda: self._cycle_game_option("difficulty", -1),
            "difficulty_next": lambda: self._cycle_game_option("difficulty", 1),
        }
        action_handler = actions.get(action)
        if action_handler is not None:
            action_handler()

    def _show_game(self) -> None:
        score_key = (
            self.game_options["mode"],
            self.game_options["difficulty"],
        )
        mode_settings = GAME_MODES[self.game_options["mode"]]
        difficulty = DIFFICULTIES[self.game_options["difficulty"]]
        self.game_stats.update(
            {
                "score": 0,
                "high_score": self.high_scores[score_key],
                "level": 1,
                "ships_left": difficulty["starting_ships"],
                "game_active": True,
                "time_remaining": mode_settings["time_limit_seconds"],
                "end_reason": "",
            }
        )
        self.recovery_remaining = 0.0
        self.ship.stop()
        self.ship.center()
        self._clear_bullets()
        self._start_new_fleet()
        self.current_screen = "game"
        self.status_message = ""
        self._build_interface()

    def _show_game_options(self) -> None:
        """Open mode and difficulty selection before a new game."""
        self.ship.stop()
        self._clear_bullets()
        self._clear_aliens()
        self.game_stats["game_active"] = False
        self.recovery_remaining = 0.0
        self.current_screen = "game_options"
        self.status_message = ""
        self._build_interface()

    def _show_settings(self) -> None:
        self.ship.stop()
        self._clear_bullets()
        self._clear_aliens()
        self.game_stats["game_active"] = False
        self.recovery_remaining = 0.0
        self.current_screen = "settings"
        self.pending_settings = copy_user_settings(self.user_settings)
        self.status_message = ""
        self._build_interface()

    def _show_menu(self) -> None:
        self.ship.stop()
        self._clear_bullets()
        self._clear_aliens()
        self.game_stats["game_active"] = False
        self.recovery_remaining = 0.0
        self.current_screen = "menu"
        self.pending_settings = copy_user_settings(self.user_settings)
        self.status_message = ""
        self._build_interface()

    def _quit(self) -> None:
        self.running = False

    def _cycle_game_option(self, option: str, step: int) -> None:
        """Cycle a mode or difficulty while gameplay is inactive."""
        if self.game_stats["game_active"]:
            return
        values = list(GAME_MODES if option == "mode" else DIFFICULTIES)
        self.game_options[option] = cycle_value(
            values,
            self.game_options[option],
            step,
        )

    def _cycle_resolution(self, step: int) -> None:
        self.pending_settings["resolution"] = cycle_value(
            RESOLUTIONS,
            self.pending_settings["resolution"],
            step,
        )
        self.status_message = "Select Apply to use these settings"

    def _cycle_background(self, step: int) -> None:
        theme_names = list(BACKGROUND_THEMES)
        self.pending_settings["background"] = cycle_value(
            theme_names,
            self.pending_settings["background"],
            step,
        )
        self.status_message = "Select Apply to use these settings"

    def _apply_settings(self) -> None:
        self.user_settings = copy_user_settings(self.pending_settings)
        self.screen = pygame.display.set_mode(self.user_settings["resolution"])
        pygame.display.set_caption(TITLE)
        self.ship.resize(self.screen.get_rect())
        self.scoreboard.resize(self.screen)
        self._clear_bullets()
        self._clear_aliens()
        self.status_message = "Settings applied"
        self._build_interface()

    def _build_interface(self) -> None:
        """Create fonts and buttons sized for the current display."""
        width, height = self.screen.get_size()
        scale = min(width / 1200, height / 800)
        scale = max(0.75, scale)

        self.fonts = {
            "title": pygame.font.Font(None, round(92 * scale)),
            "heading": pygame.font.Font(None, round(50 * scale)),
            "button": pygame.font.Font(None, round(36 * scale)),
            "body": pygame.font.Font(None, round(28 * scale)),
            "small": pygame.font.Font(None, round(22 * scale)),
        }

        self.buttons = {}
        if self.current_screen == "menu":
            self._build_menu_buttons(width, height, scale)
        elif self.current_screen == "settings":
            self._build_settings_buttons(width, height, scale)
        elif self.current_screen == "game_options":
            self._build_game_options_buttons(width, height, scale)
        elif self.current_screen == "game" and not self.game_stats["game_active"]:
            self._build_game_over_buttons(width, height, scale)

    def _build_menu_buttons(self, width: int, height: int, scale: float) -> None:
        button_width = min(round(330 * scale), width - 80)
        button_height = round(58 * scale)
        gap = round(18 * scale)
        first_y = round(height * 0.48)

        for index, (action, label) in enumerate(
            [
                ("game_options", "PLAY"),
                ("settings", "SETTINGS"),
                ("quit", "QUIT"),
            ]
        ):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = (width // 2, first_y + index * (button_height + gap))
            self.buttons[action] = Button(rect, label, self.fonts["button"])

    def _build_settings_buttons(self, width: int, height: int, scale: float) -> None:
        arrow_size = round(48 * scale)
        center_x = width // 2
        value_width = min(round(360 * scale), width - (2 * arrow_size) - 100)
        left_x = center_x - value_width // 2 - arrow_size - round(18 * scale)
        right_x = center_x + value_width // 2 + round(18 * scale)
        row_positions = [round(height * 0.40), round(height * 0.59)]

        arrow_definitions = [
            ("resolution_previous", "<", left_x, row_positions[0]),
            ("resolution_next", ">", right_x, row_positions[0]),
            ("background_previous", "<", left_x, row_positions[1]),
            ("background_next", ">", right_x, row_positions[1]),
        ]
        for action, label, x_position, y_position in arrow_definitions:
            rect = pygame.Rect(0, 0, arrow_size, arrow_size)
            rect.midleft = (x_position, y_position)
            self.buttons[action] = Button(
                rect,
                label,
                self.fonts["button"],
                compact=True,
            )

        action_width = round(190 * scale)
        action_height = round(55 * scale)
        action_y = round(height * 0.78)
        for action, label, x_offset in [
            ("apply", "APPLY", -action_width // 2 - 12),
            ("menu", "BACK", action_width // 2 + 12),
        ]:
            rect = pygame.Rect(0, 0, action_width, action_height)
            rect.center = (center_x + x_offset, action_y)
            self.buttons[action] = Button(rect, label, self.fonts["button"])

    def _build_game_over_buttons(self, width: int, height: int, scale: float) -> None:
        button_width = min(round(280 * scale), width - 100)
        button_height = round(56 * scale)
        gap = round(18 * scale)
        first_y = round(height * 0.63)

        for index, (action, label) in enumerate(
            [("play_again", "PLAY AGAIN"), ("menu", "MAIN MENU")]
        ):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = (width // 2, first_y + index * (button_height + gap))
            self.buttons[action] = Button(rect, label, self.fonts["button"])

    def _build_game_options_buttons(
        self, width: int, height: int, scale: float
    ) -> None:
        arrow_size = round(48 * scale)
        center_x = width // 2
        value_width = min(round(360 * scale), width - (2 * arrow_size) - 100)
        left_x = center_x - value_width // 2 - arrow_size - round(18 * scale)
        right_x = center_x + value_width // 2 + round(18 * scale)
        row_positions = [round(height * 0.35), round(height * 0.57)]

        arrow_definitions = [
            ("mode_previous", "<", left_x, row_positions[0]),
            ("mode_next", ">", right_x, row_positions[0]),
            ("difficulty_previous", "<", left_x, row_positions[1]),
            ("difficulty_next", ">", right_x, row_positions[1]),
        ]
        for action, label, x_position, y_position in arrow_definitions:
            rect = pygame.Rect(0, 0, arrow_size, arrow_size)
            rect.midleft = (x_position, y_position)
            self.buttons[action] = Button(
                rect,
                label,
                self.fonts["button"],
                compact=True,
            )

        action_width = round(190 * scale)
        action_height = round(55 * scale)
        action_y = round(height * 0.80)
        for action, label, x_offset in [
            ("start_game", "START", -action_width // 2 - 12),
            ("menu", "BACK", action_width // 2 + 12),
        ]:
            rect = pygame.Rect(0, 0, action_width, action_height)
            rect.center = (center_x + x_offset, action_y)
            self.buttons[action] = Button(rect, label, self.fonts["button"])

    def _background(self) -> pygame.Surface:
        theme_name = self.user_settings["background"]
        if self.current_screen == "settings":
            theme_name = self.pending_settings["background"]

        key = (self.screen.get_size(), theme_name)
        if key not in self.backgrounds:
            self.backgrounds[key] = create_space_background(*key)
        return self.backgrounds[key]

    def _draw_current_screen(self) -> None:
        self.screen.blit(self._background(), (0, 0))
        if self.current_screen == "menu":
            self._draw_menu()
        elif self.current_screen == "settings":
            self._draw_settings()
        elif self.current_screen == "game_options":
            self._draw_game_options()
        else:
            self._draw_game_canvas()

    def _draw_menu(self) -> None:
        width, height = self.screen.get_size()
        scale = min(width / 1200, height / 800)
        panel_width = min(round(680 * max(0.75, scale)), width - 50)
        panel = pygame.Rect(0, 0, panel_width, round(height * 0.72))
        panel.center = (width // 2, height // 2)
        draw_panel(self.screen, panel)

        draw_text(
            self.screen,
            "ALIEN INVASION",
            self.fonts["title"],
            COLORS["text"],
            (width // 2, round(height * 0.27)),
        )
        draw_text(
            self.screen,
            "EARTH DEFENCE COMMAND",
            self.fonts["small"],
            COLORS["accent"],
            (width // 2, round(height * 0.35)),
        )
        self._draw_buttons()

    def _draw_settings(self) -> None:
        width, height = self.screen.get_size()
        panel = pygame.Rect(0, 0, min(700, width - 40), round(height * 0.84))
        panel.center = (width // 2, height // 2)
        draw_panel(self.screen, panel)

        draw_text(
            self.screen,
            "SETTINGS",
            self.fonts["heading"],
            COLORS["text"],
            (width // 2, round(height * 0.16)),
        )
        draw_text(
            self.screen,
            "RESOLUTION",
            self.fonts["small"],
            COLORS["muted_text"],
            (width // 2, round(height * 0.31)),
        )
        resolution = self.pending_settings["resolution"]
        draw_text(
            self.screen,
            f"{resolution[0]} x {resolution[1]}",
            self.fonts["body"],
            COLORS["text"],
            (width // 2, round(height * 0.40)),
        )
        draw_text(
            self.screen,
            "BACKGROUND",
            self.fonts["small"],
            COLORS["muted_text"],
            (width // 2, round(height * 0.50)),
        )
        draw_text(
            self.screen,
            self.pending_settings["background"].upper(),
            self.fonts["body"],
            COLORS["text"],
            (width // 2, round(height * 0.59)),
        )
        if self.status_message:
            draw_text(
                self.screen,
                self.status_message,
                self.fonts["small"],
                COLORS["accent"],
                (width // 2, round(height * 0.69)),
            )
        self._draw_buttons()

    def _draw_game_canvas(self) -> None:
        if self.game_stats["game_active"]:
            for alien in self.aliens:
                alien.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            self.ship.draw(self.screen)

        self.scoreboard.draw()
        if self.recovery_remaining > 0:
            self._draw_recovery_message()
        elif not self.game_stats["game_active"]:
            self._draw_game_over()

    def _draw_game_options(self) -> None:
        """Draw mode and difficulty selection."""
        width, height = self.screen.get_size()
        panel = pygame.Rect(0, 0, min(720, width - 40), round(height * 0.88))
        panel.center = (width // 2, height // 2)
        draw_panel(self.screen, panel)

        draw_text(
            self.screen,
            "MISSION SELECT",
            self.fonts["heading"],
            COLORS["text"],
            (width // 2, round(height * 0.13)),
        )
        self._draw_option_row(
            "MODE",
            self.game_options["mode"],
            GAME_MODES[self.game_options["mode"]]["description"],
            round(height * 0.35),
        )
        self._draw_option_row(
            "DIFFICULTY",
            self.game_options["difficulty"],
            DIFFICULTIES[self.game_options["difficulty"]]["description"],
            round(height * 0.57),
        )
        self._draw_buttons()

    def _draw_option_row(
        self,
        label: str,
        value: str,
        description: str,
        center_y: int,
    ) -> None:
        """Draw one value and its supporting description."""
        width = self.screen.get_width()
        draw_text(
            self.screen,
            label,
            self.fonts["small"],
            COLORS["muted_text"],
            (width // 2, center_y - round(self.screen.get_height() * 0.08)),
        )
        draw_text(
            self.screen,
            value.upper(),
            self.fonts["body"],
            COLORS["text"],
            (width // 2, center_y),
        )
        draw_text(
            self.screen,
            description,
            self.fonts["small"],
            COLORS["accent"],
            (width // 2, center_y + round(self.screen.get_height() * 0.07)),
        )

    def _draw_recovery_message(self) -> None:
        """Explain the short pause after the player loses a ship."""
        width, height = self.screen.get_size()
        draw_text(
            self.screen,
            "SHIP LOST",
            self.fonts["heading"],
            COLORS["text"],
            (width // 2, round(height * 0.47)),
        )
        draw_text(
            self.screen,
            f"{self.game_stats['ships_left']} ships remaining",
            self.fonts["body"],
            COLORS["accent"],
            (width // 2, round(height * 0.53)),
        )

    def _draw_game_over(self) -> None:
        """Draw final statistics and restart controls."""
        width, height = self.screen.get_size()
        scale = max(0.75, min(width / 1200, height / 800))
        panel_width = min(round(600 * scale), width - 50)
        panel = pygame.Rect(0, 0, panel_width, round(height * 0.72))
        panel.center = (width // 2, height // 2)
        draw_panel(self.screen, panel)

        draw_text(
            self.screen,
            "GAME OVER",
            self.fonts["title"],
            COLORS["text"],
            (width // 2, round(height * 0.27)),
        )
        draw_text(
            self.screen,
            f"FINAL SCORE  {Scoreboard.format_score(self.game_stats['score'])}",
            self.fonts["body"],
            COLORS["accent"],
            (width // 2, round(height * 0.40)),
        )
        draw_text(
            self.screen,
            f"LEVEL REACHED  {self.game_stats['level']}",
            self.fonts["small"],
            COLORS["muted_text"],
            (width // 2, round(height * 0.47)),
        )
        draw_text(
            self.screen,
            f"{self.game_options['mode']}  •  {self.game_options['difficulty']}",
            self.fonts["small"],
            COLORS["muted_text"],
            (width // 2, round(height * 0.53)),
        )
        draw_text(
            self.screen,
            self.game_stats["end_reason"],
            self.fonts["small"],
            COLORS["accent"],
            (width // 2, round(height * 0.57)),
        )
        self._draw_buttons()

    def _draw_buttons(self) -> None:
        mouse_position = pygame.mouse.get_pos()
        for button in self.buttons.values():
            button.draw(self.screen, mouse_position)


def main() -> int:
    """Start the Alien Invasion application."""
    game = AlienInvasion()
    return game.run()
