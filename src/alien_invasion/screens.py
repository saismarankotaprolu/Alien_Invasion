"""Drawing helpers for the Phase 1 screens."""

import random
from typing import Any

import pygame

from alien_invasion.settings import BACKGROUND_THEMES, COLORS


def create_space_background(size: tuple[int, int], theme_name: str) -> pygame.Surface:
    """Create a deterministic star field and atmospheric glow."""
    width, height = size
    theme = BACKGROUND_THEMES[theme_name]
    surface = pygame.Surface(size).convert()
    base_color = theme["base_color"]
    glow_color = theme["glow_color"]
    surface.fill(base_color)

    _draw_stars(surface, theme_name, theme)
    _draw_bottom_glow(surface, base_color, glow_color)
    return surface


def _draw_stars(
    surface: pygame.Surface, theme_name: str, theme: dict[str, Any]
) -> None:
    """Draw a repeatable field of stars for the selected theme and size."""
    width, height = surface.get_size()
    density = theme["star_density"]
    star_count = max(45, round(width * height * density))
    generator = random.Random(f"{theme_name}:{width}x{height}")

    for _ in range(star_count):
        position = (generator.randrange(width), generator.randrange(height))
        radius = 2 if generator.random() > 0.88 else 1
        color = generator.choice(theme["star_colors"])
        pygame.draw.circle(surface, color, position, radius)


def _draw_bottom_glow(
    surface: pygame.Surface,
    base_color: tuple[int, int, int],
    glow_color: tuple[int, int, int],
) -> None:
    """Draw a dim gradient at the bottom to suggest Earth's atmosphere."""
    width, height = surface.get_size()
    glow_height = max(100, round(height * 0.22))
    glow_top = height - glow_height

    for offset in range(glow_height):
        strength = (offset / max(1, glow_height - 1)) ** 2
        color = tuple(
            round(base + (glow - base) * strength * 0.72)
            for base, glow in zip(base_color, glow_color)
        )
        pygame.draw.line(
            surface,
            color,
            (0, glow_top + offset),
            (width, glow_top + offset),
        )


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    center: tuple[int, int],
) -> pygame.Rect:
    """Draw centered text and return its rectangle."""
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=center)
    surface.blit(rendered_text, text_rect)
    return text_rect


def draw_panel(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Draw a translucent panel that keeps menu text readable."""
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, COLORS["panel"], panel.get_rect(), border_radius=20)
    pygame.draw.rect(
        panel,
        (*COLORS["button_border"], 110),
        panel.get_rect(),
        width=1,
        border_radius=20,
    )
    surface.blit(panel, rect)
