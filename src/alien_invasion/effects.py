"""Time-based visual effects for gameplay events."""

import math
import random
from typing import Any

import pygame


class ShipExplosion:
    """A short, non-blocking pixel-particle ship explosion."""

    COLORS = [
        (236, 248, 255),
        (91, 191, 255),
        (255, 199, 74),
        (255, 99, 83),
    ]

    def __init__(
        self,
        center: tuple[int, int],
        duration: float,
        scale: float,
    ) -> None:
        self.center = center
        self.duration = duration
        self.elapsed = 0.0
        self.scale = scale
        self.particles = self._create_particles()

    @property
    def finished(self) -> bool:
        """Return whether the animation has completed."""
        return self.elapsed >= self.duration - 1e-9

    def update(self, delta_time: float) -> None:
        """Advance the animation without blocking the game loop."""
        self.elapsed = min(self.duration, self.elapsed + delta_time)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw expanding square fragments and the initial impact flash."""
        progress = min(1.0, self.elapsed / self.duration)
        center_x, center_y = self.center

        if progress < 0.24:
            flash_size = round((1.0 - progress / 0.24) * 42 * self.scale)
            flash_size = max(4, flash_size)
            flash = pygame.Rect(0, 0, flash_size, flash_size)
            flash.center = self.center
            pygame.draw.rect(surface, (235, 249, 255), flash)

        for particle in self.particles:
            distance = particle["speed"] * self.elapsed
            x = center_x + math.cos(particle["angle"]) * distance
            y = (
                center_y
                + math.sin(particle["angle"]) * distance
                + 90 * self.elapsed * self.elapsed * self.scale
            )
            size = max(1, round(particle["size"] * (1.0 - progress * 0.65)))
            fragment = pygame.Rect(round(x), round(y), size, size)
            pygame.draw.rect(surface, particle["color"], fragment)

    def _create_particles(self) -> list[dict[str, Any]]:
        """Create a repeatable set of pixel fragments."""
        generator = random.Random(self.center[0] * 1009 + self.center[1])
        particles = []
        for index in range(28):
            particles.append(
                {
                    "angle": generator.uniform(math.pi, math.tau),
                    "speed": generator.uniform(75, 220) * self.scale,
                    "size": generator.choice([3, 4, 5, 6]) * self.scale,
                    "color": self.COLORS[index % len(self.COLORS)],
                }
            )
        return particles
