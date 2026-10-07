"""Original pixel-art icons used by the game HUD."""

import pygame

PIXEL_PATTERNS = {
    "ship": (
        "...B...",
        "..WBW..",
        "..WWW..",
        ".WWWWW.",
        "WWWBWWW",
        "WW...WW",
        ".B...B.",
    ),
    "alien": (
        "..GGG..",
        ".GCGCG.",
        "GGGGGGG",
        "G.G.G.G",
        ".G...G.",
    ),
    "crown": (
        "Y..Y..Y",
        "YY.Y.YY",
        ".YYYYY.",
        ".YYYYY.",
        "..YYY..",
    ),
    "flag": (
        ".RRRRR.",
        ".R...R.",
        ".RRRRR.",
        ".R.....",
        ".R.....",
        ".R.....",
        "RRR....",
    ),
    "clock": (
        "..CCC..",
        ".C...C.",
        "C..C..C",
        "C..CC.C",
        "C.....C",
        ".C...C.",
        "..CCC..",
    ),
}

PIXEL_PALETTE = {
    "W": (225, 238, 255),
    "B": (58, 151, 255),
    "G": (79, 205, 143),
    "C": (185, 251, 255),
    "Y": (255, 207, 72),
    "R": (255, 106, 117),
}


def create_pixel_icon(name: str, pixel_size: int) -> pygame.Surface:
    """Render a named pattern using crisp square pixels."""
    pattern = PIXEL_PATTERNS[name]
    width = max(len(row) for row in pattern) * pixel_size
    height = len(pattern) * pixel_size
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    for row_index, row in enumerate(pattern):
        for column_index, symbol in enumerate(row):
            color = PIXEL_PALETTE.get(symbol)
            if color is None:
                continue
            pixel = pygame.Rect(
                column_index * pixel_size,
                row_index * pixel_size,
                pixel_size,
                pixel_size,
            )
            pygame.draw.rect(surface, color, pixel)
    return surface
