"""Application and entry point for Alien Invasion."""

from typing import Optional

import pygame

from alien_invasion.alien import Alien
from alien_invasion.bullet import Bullet
from alien_invasion.fleet import create_fleet, update_fleet
from alien_invasion.screens import create_space_background, draw_panel, draw_text
from alien_invasion.settings import (
    ALIEN_SETTINGS,
    BACKGROUND_THEMES,
    BULLET_SETTINGS,
    COLORS,
    DEFAULT_USER_SETTINGS,
    FPS,
    RESOLUTIONS,
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
        if self.current_screen != "game":
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
        if self.current_screen == "game":
            self.ship.update(delta_time)
            self.fire_cooldown_remaining = max(
                0.0,
                self.fire_cooldown_remaining - delta_time,
            )
            if self.firing:
                self._try_fire_bullet()

            for bullet in self.bullets:
                bullet.update(delta_time)
            self.bullets = [
                bullet for bullet in self.bullets if not bullet.is_off_screen()
            ]

            self.fleet_direction = update_fleet(
                self.aliens,
                self.fleet_direction,
                self.screen.get_rect(),
                ALIEN_SETTINGS,
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

        if not self.aliens:
            self._start_new_fleet()

    def _check_alien_threats(self) -> None:
        """Reset the round if aliens hit the ship or reach Earth."""
        ship_was_hit = any(
            alien.rect.colliderect(self.ship.rect) for alien in self.aliens
        )
        earth_was_reached = any(
            alien.rect.bottom >= self.screen.get_rect().bottom for alien in self.aliens
        )
        if ship_was_hit or earth_was_reached:
            self._start_new_fleet()

    def _start_new_fleet(self) -> None:
        """Reset the play area and create a full, same-speed fleet."""
        self._clear_bullets()
        self.ship.stop()
        self.ship.center()
        self.fleet_direction = 1
        self.aliens = create_fleet(self.screen.get_rect(), ALIEN_SETTINGS)

    def _clear_aliens(self) -> None:
        """Remove the current fleet and reset its direction."""
        self.aliens.clear()
        self.fleet_direction = 1

    def _try_fire_bullet(self) -> None:
        """Create a bullet when the cooldown and active-bullet limit allow it."""
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
            "play": self._show_game,
            "settings": self._show_settings,
            "quit": self._quit,
            "menu": self._show_menu,
            "resolution_previous": lambda: self._cycle_resolution(-1),
            "resolution_next": lambda: self._cycle_resolution(1),
            "background_previous": lambda: self._cycle_background(-1),
            "background_next": lambda: self._cycle_background(1),
            "apply": self._apply_settings,
        }
        action_handler = actions.get(action)
        if action_handler is not None:
            action_handler()

    def _show_game(self) -> None:
        self.ship.stop()
        self.ship.center()
        self._clear_bullets()
        self._start_new_fleet()
        self.current_screen = "game"
        self.status_message = ""
        self._build_interface()

    def _show_settings(self) -> None:
        self.ship.stop()
        self._clear_bullets()
        self._clear_aliens()
        self.current_screen = "settings"
        self.pending_settings = copy_user_settings(self.user_settings)
        self.status_message = ""
        self._build_interface()

    def _show_menu(self) -> None:
        self.ship.stop()
        self._clear_bullets()
        self._clear_aliens()
        self.current_screen = "menu"
        self.pending_settings = copy_user_settings(self.user_settings)
        self.status_message = ""
        self._build_interface()

    def _quit(self) -> None:
        self.running = False

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

    def _build_menu_buttons(self, width: int, height: int, scale: float) -> None:
        button_width = min(round(330 * scale), width - 80)
        button_height = round(58 * scale)
        gap = round(18 * scale)
        first_y = round(height * 0.48)

        for index, (action, label) in enumerate(
            [("play", "PLAY"), ("settings", "SETTINGS"), ("quit", "QUIT")]
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
        width, height = self.screen.get_size()
        draw_text(
            self.screen,
            "A / D OR ARROWS: MOVE   •   SPACE: FIRE   •   ESC: MENU",
            self.fonts["small"],
            COLORS["muted_text"],
            (width // 2, round(height * 0.035)),
        )
        for alien in self.aliens:
            alien.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        self.ship.draw(self.screen)

    def _draw_buttons(self) -> None:
        mouse_position = pygame.mouse.get_pos()
        for button in self.buttons.values():
            button.draw(self.screen, mouse_position)


def main() -> int:
    """Start the Alien Invasion application."""
    game = AlienInvasion()
    return game.run()
