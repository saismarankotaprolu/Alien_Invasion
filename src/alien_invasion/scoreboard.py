"""Pixel-art score and game-status display."""

import math
from typing import Any, Optional

import pygame

from alien_invasion.pixel_art import create_pixel_icon
from alien_invasion.settings import COLORS


class Scoreboard:
    """Render a compact arcade HUD with icons and a blaster charge bar."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_stats: dict[str, Any],
    ) -> None:
        self.screen = screen
        self.game_stats = game_stats
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 24)
        self.images: list[tuple[pygame.Surface, pygame.Rect]] = []
        self.life_icon = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.last_values: Optional[tuple[Any, ...]] = None
        self.scale = 1.0
        self.margin = 16
        self.pixel_size = 3
        self.resize(screen)

    def resize(self, screen: pygame.Surface) -> None:
        """Rebuild fonts, icons, and positions for a resized display."""
        self.screen = screen
        width, height = screen.get_size()
        self.scale = max(0.75, min(width / 1200, height / 800))
        self.margin = round(16 * self.scale)
        self.pixel_size = max(2, round(3 * self.scale))
        self.font = pygame.font.Font(None, round(30 * self.scale))
        self.small_font = pygame.font.Font(None, round(24 * self.scale))
        self.life_icon = create_pixel_icon("ship", self.pixel_size)
        self.last_values = None
        self._prepare()

    def draw(self, weapon_charge: float = 1.0) -> None:
        """Draw cached statistics, ship lives, and weapon readiness."""
        self._prepare()
        self._draw_lives()
        self._draw_weapon_charge(weapon_charge)
        for image, rect in self.images:
            self.screen.blit(image, rect)

    @staticmethod
    def format_score(score: int) -> str:
        """Format a score with thousands separators."""
        return f"{score:,}"

    @staticmethod
    def format_time(seconds: int) -> str:
        """Format a number of seconds as minutes and seconds."""
        minutes, remaining_seconds = divmod(max(0, seconds), 60)
        return f"{minutes:02d}:{remaining_seconds:02d}"

    def _prepare(self) -> None:
        """Render labels only when their displayed values change."""
        values = (
            self.game_stats["score"],
            self.game_stats["high_score"],
            self.game_stats["level"],
            self.game_stats["ships_left"],
            self._display_seconds(),
        )
        if values == self.last_values:
            return
        self.last_values = values

        width = self.screen.get_width()
        high_score_x = width // 2 if values[4] is None else round(width * 0.56)
        self.images = [
            self._icon_label(
                "crown",
                self.format_score(values[1]),
                (high_score_x, self.margin),
                "midtop",
            ),
            self._icon_label(
                "alien",
                self.format_score(values[0]),
                (width - self.margin, self.margin),
                "topright",
            ),
            self._icon_label(
                "flag",
                str(values[2]),
                (width - self.margin, round(40 * self.scale)),
                "topright",
                small=True,
            ),
        ]
        if values[4] is not None:
            self.images.append(
                self._icon_label(
                    "clock",
                    self.format_time(values[4]),
                    (round(width * 0.29), self.margin),
                    "midtop",
                    color=COLORS["accent"],
                )
            )

    def _icon_label(
        self,
        icon_name: str,
        text: str,
        position: tuple[int, int],
        anchor: str,
        *,
        small: bool = False,
        color: tuple[int, int, int] = COLORS["text"],
    ) -> tuple[pygame.Surface, pygame.Rect]:
        """Compose one pixel icon and a text value into a cached surface."""
        icon = create_pixel_icon(icon_name, self.pixel_size)
        font = self.small_font if small else self.font
        label = font.render(text, True, color)
        gap = max(3, round(5 * self.scale))
        height = max(icon.get_height(), label.get_height())
        image = pygame.Surface(
            (icon.get_width() + gap + label.get_width(), height),
            pygame.SRCALPHA,
        )
        image.blit(icon, (0, (height - icon.get_height()) // 2))
        image.blit(
            label,
            (icon.get_width() + gap, (height - label.get_height()) // 2),
        )
        rect = image.get_rect()
        setattr(rect, anchor, position)
        return image, rect

    def _draw_lives(self) -> None:
        """Represent each remaining life as a pixel ship."""
        gap = max(2, round(4 * self.scale))
        for index in range(self.game_stats["ships_left"]):
            x = self.margin + index * (self.life_icon.get_width() + gap)
            self.screen.blit(self.life_icon, (x, self.margin))

    def _draw_weapon_charge(self, weapon_charge: float) -> None:
        """Draw a segmented bar beneath the life icons."""
        if self.game_stats["ships_left"] <= 0:
            return

        segments = 10
        segment_width = max(4, round(7 * self.scale))
        segment_height = max(4, round(6 * self.scale))
        gap = max(1, round(2 * self.scale))
        y = self.margin + self.life_icon.get_height() + round(5 * self.scale)
        filled_segments = round(max(0.0, min(1.0, weapon_charge)) * segments)

        for index in range(segments):
            rect = pygame.Rect(
                self.margin + index * (segment_width + gap),
                y,
                segment_width,
                segment_height,
            )
            color = COLORS["accent"] if index < filled_segments else COLORS["button"]
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, COLORS["button_border"], rect, width=1)

    def _display_seconds(self) -> Optional[int]:
        """Return timer seconds rounded up for a natural countdown display."""
        time_remaining = self.game_stats.get("time_remaining")
        if time_remaining is None:
            return None
        return math.ceil(time_remaining)
