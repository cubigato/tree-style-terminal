"""Import and dependency tests for tree-style-terminal."""

import pytest


def test_vte_import():
    """Ensure VTE can be imported (system dependency check)."""
    try:
        import gi
        gi.require_version("Vte", "2.91")
        from gi.repository import Vte
        assert Vte is not None
    except ImportError as e:
        pytest.fail(f"VTE import failed: {e}")


def test_gtk_import():
    """Ensure GTK can be imported (system dependency check)."""
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        assert Gtk is not None
    except ImportError as e:
        pytest.fail(f"GTK import failed: {e}")


def test_terminal_widget_import():
    """Ensure our terminal widget can be imported."""
    try:
        from src.tree_style_terminal.widgets.terminal import VteTerminal
        assert VteTerminal is not None
    except ImportError as e:
        pytest.fail(f"Terminal widget import failed: {e}")


def test_main_import():
    """Ensure main module can be imported."""
    try:
        # Test that we can import the module itself
        import src.tree_style_terminal.main
        assert src.tree_style_terminal.main is not None
    except ImportError as e:
        pytest.fail(f"Main module import failed: {e}")


def test_main_window_class_import():
    """Ensure MainWindow class can be imported."""
    try:
        from src.tree_style_terminal.main import MainWindow
        assert MainWindow is not None
    except ImportError as e:
        pytest.fail(f"MainWindow class import failed: {e}")


def test_app_class_import():
    """Ensure TreeStyleTerminalApp class can be imported."""
    try:
        from src.tree_style_terminal.main import TreeStyleTerminalApp
        assert TreeStyleTerminalApp is not None
    except ImportError as e:
        pytest.fail(f"TreeStyleTerminalApp class import failed: {e}")