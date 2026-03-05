"""Unit tests for main module."""

from __future__ import annotations

from src.main import greet


def test_greet_returns_hello_world() -> None:
    """Test that greet() returns 'Hello, World!'."""
    result = greet()
    assert result == "Hello, World!"


def test_greet_returns_string() -> None:
    """Test that greet() returns a string."""
    result = greet()
    assert isinstance(result, str)


def test_greet_not_empty() -> None:
    """Test that greet() returns a non-empty string."""
    result = greet()
    assert len(result) > 0
