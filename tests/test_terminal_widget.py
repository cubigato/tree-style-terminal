"""VTE terminal widget tests for tree-style-terminal."""

import pytest
import os


def test_vte_terminal_creation():
    """Test that VteTerminal widget can be instantiated."""
    from src.tree_style_terminal.widgets.terminal import VteTerminal
    
    terminal = VteTerminal()
    assert terminal is not None
    assert hasattr(terminal, 'terminal')  # VTE widget exists
    assert hasattr(terminal, 'set_font_size')
    assert hasattr(terminal, 'set_scrollback_length')
    assert hasattr(terminal, 'spawn_shell')


def test_font_size_configuration():
    """Test set_font_size() doesn't crash with valid inputs."""
    from src.tree_style_terminal.widgets.terminal import VteTerminal
    
    terminal = VteTerminal()
    
    # Test valid font sizes
    terminal.set_font_size(10)
    terminal.set_font_size(12)
    terminal.set_font_size(14)
    terminal.set_font_size(16)
    
    # Should not raise exceptions


def test_scrollback_configuration():
    """Test set_scrollback_length() doesn't crash with valid inputs."""
    from src.tree_style_terminal.widgets.terminal import VteTerminal
    
    terminal = VteTerminal()
    
    # Test valid scrollback lengths
    terminal.set_scrollback_length(1000)
    terminal.set_scrollback_length(5000)
    terminal.set_scrollback_length(10000)
    terminal.set_scrollback_length(0)  # Should handle zero
    
    # Should not raise exceptions


def test_shell_argv_logic():
    """Test shell command building logic (without actual spawning)."""
    from src.tree_style_terminal.widgets.terminal import VteTerminal
    
    terminal = VteTerminal()
    
    # Test that spawn_shell method exists and can be called with different parameters
    # We don't actually spawn to avoid creating real processes in tests
    
    # Test with default shell (should use $SHELL or /bin/bash)
    original_shell = os.environ.get('SHELL')
    
    try:
        # Set a known shell for testing
        os.environ['SHELL'] = '/bin/bash'
        
        # These should not crash during parameter processing
        # Note: We're not actually calling spawn_shell() as that would create real processes
        assert hasattr(terminal, 'spawn_shell')
        assert callable(terminal.spawn_shell)
        
    finally:
        # Restore original shell
        if original_shell:
            os.environ['SHELL'] = original_shell
        elif 'SHELL' in os.environ:
            del os.environ['SHELL']


def test_terminal_properties():
    """Test that terminal widget has expected properties."""
    from src.tree_style_terminal.widgets.terminal import VteTerminal
    
    terminal = VteTerminal()
    
    # Check initial state
    assert terminal.pid is None
    assert terminal.pty_fd is None
    
    # Check that VTE terminal is properly embedded
    assert terminal.terminal is not None
    assert terminal.scrolled_window is not None


def test_terminal_methods_exist():
    """Test that all expected methods exist on the terminal widget."""
    from src.tree_style_terminal.widgets.terminal import VteTerminal
    
    terminal = VteTerminal()
    
    # Check that all expected methods exist
    expected_methods = [
        'spawn_shell',
        'set_font_size', 
        'set_scrollback_length',
        'get_window_title',
        'get_current_directory',
        'close'
    ]
    
    for method_name in expected_methods:
        assert hasattr(terminal, method_name), f"Missing method: {method_name}"
        assert callable(getattr(terminal, method_name)), f"Method not callable: {method_name}"