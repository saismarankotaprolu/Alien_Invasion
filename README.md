# Alien Invasion

A classic arcade-style alien invasion game built with Python and Pygame.

## Requirements

- Python 3.9 or newer

## Local setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project and development tools:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pre-commit install
```

Run the current application:

```bash
alien-invasion
```

The main menu provides Play, Settings, and Quit options. Settings can change the
window resolution and switch between three procedural space backgrounds. Press
Escape from settings to return to the menu.

During gameplay, move the player ship with the Left/Right Arrow keys or `A`/`D`.
Press or hold Space to fire up to three bullets at a time.
Destroy the complete alien fleet before it reaches the ship or the bottom edge.
Each alien awards points, clearing a fleet adds a bonus and advances the level,
and the game ends after all three player ships are lost.

Press Escape during gameplay to pause. Menus support the mouse or keyboard:
use the Arrow keys or Tab to move focus and Enter or Space to select.

Before starting, choose Easy, Normal, or Hard difficulty and either Classic or
two-minute Time Attack mode. Later fleets become faster, with a safe speed cap.

The Phase 7 arcade HUD uses original pixel-art icons, ship icons for remaining
lives, and a segmented blaster recharge meter. Ship impacts play a non-blocking
pixel explosion before a life is removed or the game-over screen appears.

Display preferences, the last selected game options, and high scores are saved
automatically. On macOS, the save file is stored at
`~/Library/Application Support/Alien Invasion/settings.json`; equivalent local
application-data folders are used on Windows and Linux.

Run the checks:

```bash
ruff check .
ruff format --check .
pytest
```

## Project structure

```text
.
├── src/alien_invasion/  # Game source code
├── tests/               # Automated tests
├── main.py              # Convenience entry point for development
└── pyproject.toml       # Project metadata and tool configuration
```

## Planning documents

- [Phase 1: Game Foundation and Settings](docs/phase-1-foundation.md)
