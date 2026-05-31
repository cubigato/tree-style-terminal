"""Pytest configuration and fixtures for tree-style-terminal tests."""

import os
import sys

import pytest

# Add the src layout root so package imports work from a repository checkout.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope="session", autouse=True)
def setup_gi():
    """Setup GObject Introspection requirements for all tests."""
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Vte", "2.91")

@pytest.fixture
def mock_display(monkeypatch):
    """Mock display for tests that need GTK but don't need actual display."""
    monkeypatch.setenv("DISPLAY", ":99")
