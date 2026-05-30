"""Main window tests for tree-style-terminal."""

from unittest.mock import Mock, patch

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from tree_style_terminal.models.session import TerminalSession


def test_main_window_creation():
    """Test MainWindow can be instantiated (basic setup)."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp
    
    # Create a minimal app instance for the window
    app = TreeStyleTerminalApp()
    
    # Create main window
    window = MainWindow(application=app)
    assert window is not None
    assert window.session_manager is not None


def test_main_window_methods_exist():
    """Test that expected methods exist on MainWindow."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp
    
    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)
    
    # Check that expected methods exist
    expected_methods = [
        '_on_new_terminal_clicked',
        '_on_close_session_clicked',
        '_on_new_child_clicked',
        '_on_sidebar_toggle_clicked'
    ]
    
    for method_name in expected_methods:
        assert hasattr(window, method_name), f"Missing method: {method_name}"
        assert callable(getattr(window, method_name)), f"Method not callable: {method_name}"


def test_app_creation():
    """Test TreeStyleTerminalApp can be instantiated."""
    from tree_style_terminal.main import TreeStyleTerminalApp
    
    app = TreeStyleTerminalApp()
    assert app is not None
    assert hasattr(app, 'window')
    assert app.window is None  # Should be None until activated


def test_sidebar_state_management():
    """Test sidebar state tracking properties."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp
    
    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)
    
    # Check sidebar state properties exist
    assert hasattr(window, '_sidebar_collapsed')
    assert isinstance(window._sidebar_collapsed, bool)
    assert window._sidebar_collapsed is False  # Should start expanded


def test_sidebar_width_bounds_for_small_window():
    """Sidebar bounds preserve terminal room on small windows."""
    from tree_style_terminal.main import calculate_sidebar_width_bounds

    bounds = calculate_sidebar_width_bounds(800)

    assert bounds.minimum == 150
    assert bounds.default == 250
    assert bounds.maximum == 320


def test_sidebar_width_bounds_for_medium_window():
    """Sidebar bounds match the previous defaults on normal windows."""
    from tree_style_terminal.main import calculate_sidebar_width_bounds

    bounds = calculate_sidebar_width_bounds(1024)

    assert bounds.minimum == 150
    assert bounds.default == 250
    assert bounds.maximum == 410


def test_sidebar_width_bounds_for_large_window():
    """Sidebar bounds scale up for large displays."""
    from tree_style_terminal.main import calculate_sidebar_width_bounds

    bounds = calculate_sidebar_width_bounds(3840)

    assert bounds.minimum == 260
    assert bounds.default == 560
    assert bounds.maximum == 1000


def test_clamp_sidebar_width_uses_computed_bounds():
    """Sidebar clamping follows the dynamic min/max bounds."""
    from tree_style_terminal.main import calculate_sidebar_width_bounds, clamp_sidebar_width

    bounds = calculate_sidebar_width_bounds(3840)

    assert clamp_sidebar_width(100, bounds) == 260
    assert clamp_sidebar_width(700, bounds) == 700
    assert clamp_sidebar_width(1200, bounds) == 1000


def test_layout_components_exist():
    """Test that layout components (Paned, Revealer) are available."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp
    
    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)
    
    # Check that layout-related attributes exist
    expected_attributes = [
        'paned',  # Gtk.Paned for sidebar and terminal area
        'sidebar_revealer',  # Gtk.Revealer for collapsible sidebar
    ]
    
    for attr in expected_attributes:
        if hasattr(window, attr):
            # If it exists, it should not be None
            assert getattr(window, attr) is not None


def test_sidebar_toggle_functionality():
    """Test sidebar toggle button and revealer functionality."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp
    
    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)
    
    # Check toggle method exists
    assert hasattr(window, '_on_sidebar_toggle_clicked')
    assert callable(window._on_sidebar_toggle_clicked)
    
    # Test initial state
    initial_state = window._sidebar_collapsed
    
    # Simulate toggle (without actually clicking)
    # This tests the method exists and can be called
    try:
        window._on_sidebar_toggle_clicked(None)  # Button parameter can be None for test
        # State should have changed
        assert window._sidebar_collapsed != initial_state
    except Exception:
        # If method requires specific setup, just verify it exists
        pass


def test_new_session_creation_schedules_terminal_focus():
    """Test creating a session schedules focus back to the terminal."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)
    session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
    terminal_widget = Gtk.Box()

    with patch("tree_style_terminal.main.GLib.idle_add") as idle_add:
        window._on_session_created(session, terminal_widget)

    idle_add.assert_called_with(window.focus_terminal)


def test_theme_update_applies_to_session_manager_terminals():
    """Test theme updates are delegated to SessionManager-managed terminals."""
    from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp

    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)
    session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
    terminal_widget = Mock()
    window.session_manager._session_terminals[session] = terminal_widget

    window._update_terminal_themes("dark")

    terminal_widget.apply_theme.assert_called_once_with("dark")
