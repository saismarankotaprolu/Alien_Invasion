"""Tests for settings data and helpers."""

import pytest

from alien_invasion.settings import (
    BACKGROUND_THEMES,
    DEFAULT_RESOLUTION,
    DEFAULT_USER_SETTINGS,
    RESOLUTIONS,
    cycle_value,
)


def test_default_settings_are_supported() -> None:
    assert DEFAULT_RESOLUTION in RESOLUTIONS
    assert DEFAULT_USER_SETTINGS["background"] in BACKGROUND_THEMES


def test_cycle_value_wraps_in_both_directions() -> None:
    values = ["first", "second", "third"]

    assert cycle_value(values, "third", 1) == "first"
    assert cycle_value(values, "first", -1) == "third"


def test_cycle_value_rejects_empty_collection() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        cycle_value([], "missing", 1)
