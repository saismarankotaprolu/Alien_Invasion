"""Player bullet drawing and movement."""

from typing import Any

import pygame


class Bullet:
    """A projectile that travels upward from the player ship."""

    def __init__(
        self,
        position: tuple[int, int],
        settings: dict[str, Any],
        display_size: tuple[int, int],
    ) -> None:
        width, height = display_size
        scale = max(0.75, min(width / 1200, height / 800))
        bullet_width = max(2, round(settings["width"] * scale))
        bullet_height = max(8, round(settings["height"] * scale))

        self.rect = pygame.Rect(0, 0, bullet_width, bullet_height)
        self.rect.midbottom = position
        self.y = float(self.rect.y)
        self.speed = settings["speed"] * height / settings["reference_height"]
        self.image = self._create_image(
            bullet_width,
            bullet_height,
            settings["color"],
            settings["glow_color"],
        )

    def update(self, delta_time: float) -> None:
        """Move the bullet upward using elapsed frame time."""
        self.y -= self.speed * delta_time
        self.rect.y = round(self.y)

    def is_off_screen(self) -> bool:
        """Return whether the bullet has passed the top edge."""
        return self.rect.bottom <= 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bullet and its subtle glow."""
        image_rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image, image_rect)

    @staticmethod
    def _create_image(
        width: int,
        height: int,
        color: tuple[int, int, int],
        glow_color: tuple[int, int, int],
    ) -> pygame.Surface:
        """Create a bright projectile with a translucent outer glow."""
        glow_padding = max(3, width)
        image = pygame.Surface(
            (width + glow_padding * 2, height + glow_padding * 2),
            pygame.SRCALPHA,
        )
        glow_rect = image.get_rect().inflate(-glow_padding, -glow_padding)
        pygame.draw.rect(
            image,
            (*glow_color, 75),
            glow_rect,
            border_radius=max(1, width),
        )

        core_rect = pygame.Rect(0, 0, width, height)
        core_rect.center = image.get_rect().center
        pygame.draw.rect(
            image,
            color,
            core_rect,
            border_radius=max(1, width // 2),
        )
        return image
