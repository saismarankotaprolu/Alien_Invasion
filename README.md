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

The main menu provides Play, Settings, and Quit options. The Phase 1 settings
screen can change the window resolution and switch between three procedural
space backgrounds. Press Escape from gameplay or settings to return to the menu.

During gameplay, move the player ship with the Left/Right Arrow keys or `A`/`D`.
Press or hold Space to fire up to three bullets at a time.
Destroy the complete alien fleet before it reaches the ship or the bottom edge.
Each alien awards points, clearing a fleet adds a bonus and advances the level,
and the game ends after all three player ships are lost.

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

Gameplay and architecture will be defined in the project plan before implementation.

## Planning documents

- [Phase 1: Game Foundation and Settings](docs/phase-1-foundation.md)
