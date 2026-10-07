"""Small reusable user-interface components."""

import pygame

from alien_invasion.settings import COLORS


class Button:
    """A text button with simple hover feedback."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        *,
        compact: bool = False,
    ) -> None:
        self.rect = rect
        self.text = text
        self.font = font
        self.compact = compact

    def contains(self, position: tuple[int, int]) -> bool:
        """Return whether a screen position is inside the button."""
        return self.rect.collidepoint(position)

    def draw(
        self,
        surface: pygame.Surface,
        mouse_position: tuple[int, int],
        *,
        focused: bool = False,
    ) -> None:
        """Draw the button, highlighting it when the pointer is over it."""
        hovered = self.contains(mouse_position)
        highlighted = hovered or focused
        fill_color = COLORS["button_hover"] if highlighted else COLORS["button"]
        border_radius = 8 if self.compact else 12

        pygame.draw.rect(surface, fill_color, self.rect, border_radius=border_radius)
        pygame.draw.rect(
            surface,
            COLORS["button_border"],
            self.rect,
            width=3 if focused else 2,
            border_radius=border_radius,
        )

        label = self.font.render(self.text, True, COLORS["text"])
        surface.blit(label, label.get_rect(center=self.rect.center))
