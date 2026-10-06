"""Configuration values and helpers for Alien Invasion."""

from collections.abc import Sequence
from typing import Any, TypeVar

TITLE = "Alien Invasion"
FPS = 60

DEFAULT_RESOLUTION = (1200, 800)
RESOLUTIONS = [
    (800, 600),
    (1200, 800),
    (1600, 900),
]

BACKGROUND_THEMES = {
    "Earth Orbit": {
        "base_color": (3, 8, 24),
        "glow_color": (18, 92, 205),
        "star_colors": [(118, 151, 198), (184, 210, 242), (238, 247, 255)],
        "star_density": 0.00011,
    },
    "Deep Space": {
        "base_color": (1, 3, 10),
        "glow_color": (10, 17, 38),
        "star_colors": [(142, 155, 178), (211, 221, 238), (255, 255, 255)],
        "star_density": 0.00016,
    },
    "Purple Nebula": {
        "base_color": (13, 5, 28),
        "glow_color": (105, 35, 153),
        "star_colors": [(151, 126, 191), (211, 187, 235), (251, 236, 255)],
        "star_density": 0.00012,
    },
}

DEFAULT_USER_SETTINGS = {
    "resolution": DEFAULT_RESOLUTION,
    "background": "Earth Orbit",
}

SHIP_SETTINGS = {
    "width": 64,
    "height": 72,
    "speed": 420,
    "reference_width": 1200,
    "bottom_margin": 30,
}

BULLET_SETTINGS = {
    "width": 4,
    "height": 18,
    "speed": 700,
    "reference_height": 800,
    "color": (118, 224, 255),
    "glow_color": (42, 155, 255),
    "cooldown_ms": 250,
    "max_active": 3,
}

ALIEN_SETTINGS = {
    "width": 52,
    "height": 38,
    "horizontal_speed": 90,
    "reference_width": 1200,
    "drop_distance": 24,
    "horizontal_gap": 22,
    "vertical_gap": 20,
    "top_margin": 72,
    "side_margin": 52,
    "rows": 4,
    "columns": 12,
}

COLORS = {
    "text": (225, 238, 255),
    "muted_text": (143, 170, 205),
    "accent": (58, 151, 255),
    "button": (15, 37, 70),
    "button_hover": (25, 70, 122),
    "button_border": (80, 165, 255),
    "panel": (5, 16, 37, 220),
}

T = TypeVar("T")


def cycle_value(values: Sequence[T], current: T, step: int) -> T:
    """Return the next value in a sequence, wrapping at either end."""
    if not values:
        raise ValueError("values must not be empty")

    current_index = values.index(current)
    return values[(current_index + step) % len(values)]


def copy_user_settings(settings: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy of the simple user-settings dictionary."""
    return {
        "resolution": settings["resolution"],
        "background": settings["background"],
    }
