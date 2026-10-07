"""Score and game-status display."""

import math
from typing import Any, Optional

import pygame

from alien_invasion.settings import COLORS


class Scoreboard:
    """Render score, high score, level, and remaining ships."""

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
        self.last_values: Optional[tuple[Any, ...]] = None
        self.resize(screen)

    def resize(self, screen: pygame.Surface) -> None:
        """Rebuild fonts and positions for a resized display."""
        self.screen = screen
        width, height = screen.get_size()
        scale = max(0.75, min(width / 1200, height / 800))
        self.font = pygame.font.Font(None, round(30 * scale))
        self.small_font = pygame.font.Font(None, round(24 * scale))
        self.last_values = None
        self._prepare()

    def draw(self) -> None:
        """Draw the cached status labels, refreshing changed values."""
        self._prepare()
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
        """Render status labels only when their values change."""
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

        width, height = self.screen.get_size()
        scale = max(0.75, min(width / 1200, height / 800))
        margin = round(16 * scale)

        ships = self.font.render(
            f"SHIPS  {values[3]}",
            True,
            COLORS["text"],
        )
        high_score = self.font.render(
            f"HIGH  {self.format_score(values[1])}",
            True,
            COLORS["text"],
        )
        score = self.font.render(
            f"SCORE  {self.format_score(values[0])}",
            True,
            COLORS["text"],
        )
        level = self.small_font.render(
            f"LEVEL  {values[2]}",
            True,
            COLORS["muted_text"],
        )

        ships_rect = ships.get_rect(topleft=(margin, margin))
        high_score_x = width // 2 if values[4] is None else round(width * 0.56)
        high_score_rect = high_score.get_rect(midtop=(high_score_x, margin))
        score_rect = score.get_rect(topright=(width - margin, margin))
        level_rect = level.get_rect(
            topright=(width - margin, score_rect.bottom + round(3 * scale))
        )
        self.images = [
            (ships, ships_rect),
            (high_score, high_score_rect),
            (score, score_rect),
            (level, level_rect),
        ]
        if values[4] is not None:
            timer = self.font.render(
                f"TIME  {self.format_time(values[4])}",
                True,
                COLORS["accent"],
            )
            timer_rect = timer.get_rect(midtop=(round(width * 0.29), margin))
            self.images.append((timer, timer_rect))

    def _display_seconds(self) -> Optional[int]:
        """Return timer seconds rounded up for a natural countdown display."""
        time_remaining = self.game_stats.get("time_remaining")
        if time_remaining is None:
            return None
        return math.ceil(time_remaining)
