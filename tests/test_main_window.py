"""Main window tests for tree-style-terminal."""

import pytest


def test_main_window_creation():
    """Test MainWindow can be instantiated (basic setup)."""
    from src.tree_style_terminal.main import MainWindow, TreeStyleTerminalApp
    
    # Create a minimal app instance for the window
    app = TreeStyleTerminalApp()
    
    # Create main window
    window = MainWindow(application=app)
    assert window is not None
    assert hasattr(window, 'terminals')
    assert hasattr(window, 'terminal_counter')
    assert hasattr(window, 'active_terminal_id')


def test_terminal_management_dict():
    """Test terminal storage/retrieval from terminals dict."""
    from src.tree_style_terminal.main import MainWindow, TreeStyleTerminalApp
    
    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)
    
    # Check initial state
    assert isinstance(window.terminals, dict)
    assert len(window.terminals) == 0
    assert window.terminal_counter == 0
    assert window.active_terminal_id is None


def test_main_window_methods_exist():
    """Test that expected methods exist on MainWindow."""
    from src.tree_style_terminal.main import MainWindow, TreeStyleTerminalApp
    
    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)
    
    # Check that expected methods exist
    expected_methods = [
        '_create_new_terminal',
        '_switch_to_terminal',
        '_close_terminal',
        '_on_new_terminal_clicked',
        '_on_sidebar_toggle_clicked'
    ]
    
    for method_name in expected_methods:
        assert hasattr(window, method_name), f"Missing method: {method_name}"
        assert callable(getattr(window, method_name)), f"Method not callable: {method_name}"


def test_app_creation():
    """Test TreeStyleTerminalApp can be instantiated."""
    from src.tree_style_terminal.main import TreeStyleTerminalApp
    
    app = TreeStyleTerminalApp()
    assert app is not None
    assert hasattr(app, 'window')
    assert app.window is None  # Should be None until activated


def test_sidebar_state_management():
    """Test sidebar state tracking properties."""
    from src.tree_style_terminal.main import MainWindow, TreeStyleTerminalApp
    
    app = TreeStyleTerminalApp()
    window = MainWindow(application=app)
    
    # Check sidebar state properties exist
    assert hasattr(window, '_sidebar_collapsed')
    assert isinstance(window._sidebar_collapsed, bool)
    assert window._sidebar_collapsed is False  # Should start expanded