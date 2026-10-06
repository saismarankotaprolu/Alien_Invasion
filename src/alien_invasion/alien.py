"""Alien drawing and movement."""

from typing import Any

import pygame


class Alien:
    """A single alien that moves as part of the fleet."""

    def __init__(
        self,
        position: tuple[int, int],
        settings: dict[str, Any],
        display_size: tuple[int, int],
    ) -> None:
        display_width, display_height = display_size
        scale = max(0.75, min(display_width / 1200, display_height / 800))
        width = round(settings["width"] * scale)
        height = round(settings["height"] * scale)

        self.image = self._create_image(width, height)
        self.rect = self.image.get_rect(topleft=position)
        self.x = float(self.rect.x)
        self.speed = (
            settings["horizontal_speed"] * display_width / settings["reference_width"]
        )

    def update(self, direction: int, delta_time: float) -> None:
        """Move horizontally in the fleet's shared direction."""
        self.x += self.speed * direction * delta_time
        self.rect.x = round(self.x)

    def drop(self, distance: int) -> None:
        """Move downward when the fleet changes direction."""
        self.rect.y += distance

    def reached_edge(self, screen_rect: pygame.Rect) -> bool:
        """Return whether the alien touches either horizontal edge."""
        reached_left = self.rect.left <= screen_rect.left
        reached_right = self.rect.right >= screen_rect.right
        return reached_left or reached_right

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the alien at its current position."""
        surface.blit(self.image, self.rect)

    @staticmethod
    def _create_image(width: int, height: int) -> pygame.Surface:
        """Create a compact alien sprite from Pygame shapes."""
        image = pygame.Surface((width, height), pygame.SRCALPHA)

        body_rect = pygame.Rect(
            round(width * 0.10),
            round(height * 0.28),
            round(width * 0.80),
            round(height * 0.52),
        )
        pygame.draw.ellipse(image, (79, 205, 143), body_rect)
        pygame.draw.ellipse(image, (159, 255, 209), body_rect, width=2)

        dome_rect = pygame.Rect(
            round(width * 0.27),
            round(height * 0.08),
            round(width * 0.46),
            round(height * 0.50),
        )
        pygame.draw.ellipse(image, (45, 129, 119), dome_rect)
        pygame.draw.arc(
            image,
            (146, 246, 218),
            dome_rect,
            0,
            3.15,
            width=2,
        )

        eye_y = round(height * 0.45)
        eye_radius = max(2, round(width * 0.045))
        for eye_x in (round(width * 0.39), round(width * 0.61)):
            pygame.draw.circle(image, (8, 28, 40), (eye_x, eye_y), eye_radius)
            pygame.draw.circle(
                image,
                (185, 251, 255),
                (eye_x, eye_y),
                max(1, eye_radius // 2),
            )

        leg_y = round(height * 0.71)
        foot_y = height - 1
        leg_color = (111, 225, 166)
        pygame.draw.line(
            image,
            leg_color,
            (round(width * 0.27), leg_y),
            (round(width * 0.17), foot_y),
            width=2,
        )
        pygame.draw.line(
            image,
            leg_color,
            (round(width * 0.73), leg_y),
            (round(width * 0.83), foot_y),
            width=2,
        )
        return image
