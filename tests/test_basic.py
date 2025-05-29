"""
Basic smoke tests for tree-style-terminal application.
"""

import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

from tree_style_terminal import TreeStyleTerminalApp, MainWindow, main


class TestTreeStyleTerminalApp:
    """Test the main application class."""
    
    def test_app_creation(self):
        """Test that application can be created."""
        app = TreeStyleTerminalApp()
        assert app is not None
        assert isinstance(app, Gtk.Application)
        assert app.get_application_id() == "org.example.TreeStyleTerminal"
    
    def test_app_flags(self):
        """Test application flags are set correctly."""
        app = TreeStyleTerminalApp()
        assert app.get_flags() == Gio.ApplicationFlags.FLAGS_NONE


class TestMainWindow:
    """Test the main window class."""
    
    def test_window_creation(self):
        """Test that main window can be created."""
        app = TreeStyleTerminalApp()
        window = MainWindow(application=app)
        assert window is not None
        assert isinstance(window, Gtk.ApplicationWindow)
        assert window.get_title() == "Tree Style Terminal"
        assert window.get_default_size() == (1024, 768)
    
    def test_window_has_headerbar(self):
        """Test that window has a headerbar."""
        app = TreeStyleTerminalApp()
        window = MainWindow(application=app)
        headerbar = window.get_titlebar()
        assert headerbar is not None
        assert isinstance(headerbar, Gtk.HeaderBar)


class TestApplicationIntegration:
    """Test application integration."""
    
    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        assert callable(main)
    
    def test_package_imports(self):
        """Test that package imports work correctly."""
        from tree_style_terminal import __version__, __author__, __license__
        assert __version__ == "0.1.0"
        assert __author__ == "Tree Style Terminal Contributors"
        assert __license__ == "GPL-3.0"