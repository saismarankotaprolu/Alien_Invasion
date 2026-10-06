"""Player ship drawing and movement."""

from typing import Any

import pygame


class Ship:
    """A player-controlled ship that moves horizontally."""

    def __init__(
        self,
        screen_rect: pygame.Rect,
        settings: dict[str, Any],
    ) -> None:
        self.settings = settings
        self.screen_rect = screen_rect.copy()
        self.movement = {
            "left": False,
            "right": False,
        }

        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.x = 0.0
        self.speed = 0.0
        self.bottom_margin = 0
        self.resize(screen_rect)

    def set_movement(self, direction: str, active: bool) -> None:
        """Start or stop movement in a named horizontal direction."""
        if direction not in self.movement:
            raise ValueError(f"Unknown movement direction: {direction}")
        self.movement[direction] = active

    def stop(self) -> None:
        """Stop all horizontal movement."""
        for direction in self.movement:
            self.movement[direction] = False

    def update(self, delta_time: float) -> None:
        """Move the ship while keeping it inside the screen."""
        direction = int(self.movement["right"]) - int(self.movement["left"])
        self.x += direction * self.speed * delta_time

        minimum_x = float(self.screen_rect.left)
        maximum_x = float(self.screen_rect.right - self.rect.width)
        self.x = max(minimum_x, min(self.x, maximum_x))
        self.rect.x = round(self.x)

    def center(self) -> None:
        """Return the ship to its starting position at the bottom center."""
        self.rect.midbottom = (
            self.screen_rect.centerx,
            self.screen_rect.bottom - self.bottom_margin,
        )
        self.x = float(self.rect.x)

    def resize(self, screen_rect: pygame.Rect) -> None:
        """Scale and recenter the ship for a new display size."""
        self.screen_rect = screen_rect.copy()
        scale = min(self.screen_rect.width / 1200, self.screen_rect.height / 800)
        scale = max(0.75, scale)

        width = round(self.settings["width"] * scale)
        height = round(self.settings["height"] * scale)
        self.speed = (
            self.settings["speed"]
            * self.screen_rect.width
            / self.settings["reference_width"]
        )
        self.bottom_margin = round(self.settings["bottom_margin"] * scale)
        self.image = self._create_image(width, height)
        self.rect = self.image.get_rect()
        self.stop()
        self.center()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the ship at its current position."""
        surface.blit(self.image, self.rect)

    @staticmethod
    def _create_image(width: int, height: int) -> pygame.Surface:
        """Create a simple spaceship from Pygame shapes."""
        image = pygame.Surface((width, height), pygame.SRCALPHA)

        wing_points = [
            (round(width * 0.06), round(height * 0.82)),
            (round(width * 0.30), round(height * 0.43)),
            (round(width * 0.42), round(height * 0.78)),
            (round(width * 0.58), round(height * 0.78)),
            (round(width * 0.70), round(height * 0.43)),
            (round(width * 0.94), round(height * 0.82)),
        ]
        pygame.draw.polygon(image, (88, 122, 163), wing_points)
        pygame.draw.polygon(image, (151, 184, 218), wing_points, width=2)

        flame_points = [
            (round(width * 0.39), round(height * 0.73)),
            (round(width * 0.50), height - 1),
            (round(width * 0.61), round(height * 0.73)),
        ]
        pygame.draw.polygon(image, (41, 139, 255, 120), flame_points)
        inner_flame = [
            (round(width * 0.45), round(height * 0.75)),
            (round(width * 0.50), round(height * 0.91)),
            (round(width * 0.55), round(height * 0.75)),
        ]
        pygame.draw.polygon(image, (147, 224, 255), inner_flame)

        body_points = [
            (width // 2, 0),
            (round(width * 0.69), round(height * 0.66)),
            (round(width * 0.61), round(height * 0.83)),
            (round(width * 0.39), round(height * 0.83)),
            (round(width * 0.31), round(height * 0.66)),
        ]
        pygame.draw.polygon(image, (218, 231, 244), body_points)
        pygame.draw.polygon(image, (93, 165, 226), body_points, width=2)

        cockpit = pygame.Rect(
            round(width * 0.40),
            round(height * 0.25),
            round(width * 0.20),
            round(height * 0.27),
        )
        pygame.draw.ellipse(image, (42, 139, 219), cockpit)
        pygame.draw.ellipse(image, (154, 224, 255), cockpit, width=2)

        return image
