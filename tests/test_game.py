"""Tests for the application entry point."""

from alien_invasion.game import main


def test_main_returns_success(capsys: object) -> None:
    """The placeholder application exits successfully."""
    assert main() == 0

    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert captured.out == "Alien Invasion project is ready.\n"
