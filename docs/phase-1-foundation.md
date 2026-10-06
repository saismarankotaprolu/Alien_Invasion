# Phase 1: Game Foundation and Settings

**Status:** Complete

## Goal

Create the visual and technical foundation for Alien Invasion. This phase covers
the Pygame window, canvas, space-themed background, navigation, and basic display
settings. It does not include the player ship, bullets, or aliens.

## Packages and initialization

### Runtime dependency

- `pygame` for the window, drawing, input, text, and frame timing.

### Development tools

- `pytest` for automated tests.
- `ruff` for formatting and code-quality checks.
- `pre-commit` for checks before Git commits.

Pygame must initialize when the application starts and shut down cleanly when
the player exits.

## Screen and canvas

Default display configuration:

```python
DEFAULT_RESOLUTION = (1200, 800)
FPS = 60
TITLE = "Alien Invasion"
```

The application will use:

- A Pygame display surface as the main canvas.
- A Pygame clock to maintain 60 frames per second.
- A main loop for processing input, updating state, and drawing frames.
- Safe handling of window-close events and the Escape key.

Supported resolutions will be stored as a list of tuples:

```python
RESOLUTIONS = [
    (800, 600),
    (1200, 800),
    (1600, 900),
]
```

Preset resolutions will keep the interface and future gameplay elements aligned
correctly.

## Default space theme

The default `Earth Orbit` background will be drawn programmatically instead of
using an external image. It will contain:

- A near-black or deep-navy space background.
- Small stars with subtle variations in size or brightness.
- A dim blue atmospheric glow along the bottom of the screen.
- A soft gradient that fades upward into space.
- Little or no animation, keeping the background unobtrusive.

The atmospheric effect will use several semi-transparent horizontal bands to
create a simple glow without drawing the entire Earth.

## Main menu

The opening screen will contain:

- The game title.
- A `Play` button.
- A `Settings` button.
- A `Quit` button.

For this phase, `Play` opens an empty gameplay canvas. Pressing Escape returns to
the main menu.

## Settings screen

The settings screen will allow the player to:

- Select a supported window resolution.
- Select a background theme.
- Apply the selected settings.
- Return to the main menu.

The initial theme choices will be stored in a dictionary:

```python
BACKGROUND_THEMES = {
    "Earth Orbit": {},
    "Deep Space": {},
    "Purple Nebula": {},
}
```

Theme intentions:

- **Earth Orbit:** dark space with the blue atmospheric glow.
- **Deep Space:** nearly black space with brighter stars.
- **Purple Nebula:** dark purple space with a subtle colored glow.

Selecting `Apply` will update the display during the current session.

## Proposed code organization

```text
src/alien_invasion/
├── game.py          # Main loop and screen switching
├── settings.py      # Resolutions, colors, themes, and FPS
├── screens.py       # Menu, settings, and gameplay canvas
└── ui.py            # Reusable button behavior
```

Application state will use simple values and data structures:

```python
current_screen = "menu"

user_settings = {
    "resolution": (1200, 800),
    "background": "Earth Orbit",
}
```

Persistent settings and custom background images are outside Phase 1. They may
be considered during the Phase 7 user-experience work.

## Completion criteria

Phase 1 is complete when:

- The application starts without errors.
- The space-themed main menu is displayed.
- The blue Earth-atmosphere glow appears in the default theme.
- `Play` opens an empty gameplay canvas.
- `Settings` opens the settings screen.
- All supported resolution changes work correctly.
- Background themes can be changed.
- Escape and `Quit` behave correctly.
- The interface remains usable at every supported resolution.
- Formatting, code-quality checks, and automated tests pass.

## Implementation result

Phase 1 was implemented with procedural backgrounds, responsive menus, and
session-only display settings. The main menu, settings screen, empty gameplay
canvas, Escape navigation, and Quit behavior are operational at all three
supported resolutions.
