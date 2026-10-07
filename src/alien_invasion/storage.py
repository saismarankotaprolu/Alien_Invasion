"""Safe JSON persistence for preferences and high scores."""

import json
import os
import sys
from pathlib import Path
from typing import Any


def default_save_path() -> Path:
    """Return a platform-appropriate location for the player save file."""
    if sys.platform == "darwin":
        data_directory = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        data_directory = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    else:
        data_directory = Path(
            os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        )
    return data_directory / "Alien Invasion" / "settings.json"


def load_game_data(path: Path) -> dict[str, Any]:
    """Load saved data, returning defaults for missing or damaged files."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_game_data(path: Path, data: dict[str, Any]) -> bool:
    """Atomically save data without leaving a partially written file."""
    temporary_path = path.with_suffix(".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path.write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary_path.replace(path)
    except (OSError, TypeError, ValueError):
        return False
    return True
