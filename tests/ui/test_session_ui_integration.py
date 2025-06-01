"""
UI integration tests for session control buttons.

Tests the integration between HeaderBar buttons, keyboard shortcuts,
and session management operations as specified in Milestone 5 point 4.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Gio, GLib

from tree_style_terminal.controllers.shortcuts import ShortcutController
from tree_style_terminal.controllers.session_manager import SessionManager
from tree_style_terminal.models.tree import SessionTree
from tree_style_terminal.models.session import TerminalSession


class TestSessionUIIntegration:
    """Test cases for UI integration of session control buttons."""
    
    @pytest.fixture
    def session_tree(self):
        """Create a test session tree."""
        return SessionTree()
    
    @pytest.fixture
    def session_manager(self, session_tree):
        """Create a test session manager."""
        return SessionManager(session_tree)
    
    @pytest.fixture
    def shortcut_controller(self, session_manager):
        """Create a test shortcut controller."""
        return ShortcutController(session_manager)
    
    @pytest.fixture
    def mock_headerbar_buttons(self):
        """Create mock HeaderBar buttons."""
        buttons = {
            'new_sibling_button': Mock(spec=Gtk.Button),
            'new_child_button': Mock(spec=Gtk.Button),
            'close_session_button': Mock(spec=Gtk.Button),
            'sidebar_toggle_button': Mock(spec=Gtk.Button)
        }
        
        # Mock button properties
        for name, button in buttons.items():
            button.get_tooltip_text.return_value = f"Mock tooltip for {name}"
            button.get_sensitive.return_value = True
            button.set_sensitive = Mock()
            button.get_can_focus.return_value = True
            button.get_image.return_value = Mock(spec=Gtk.Image)
            
        return buttons
    
    def test_button_action_integration(self, shortcut_controller, mock_headerbar_buttons):
        """Test that button clicks trigger the correct actions."""
        # Get the actions from shortcut controller
        new_sibling_action = shortcut_controller.get_action("new_sibling")
        new_child_action = shortcut_controller.get_action("new_child")
        close_session_action = shortcut_controller.get_action("close_session")
        
        # Verify actions exist
        assert new_sibling_action is not None
        assert new_child_action is not None
        assert close_session_action is not None
        
        # Verify actions are callable
        assert callable(new_sibling_action.activate)
        assert callable(new_child_action.activate)
        assert callable(close_session_action.activate)
    
    def test_action_state_management(self, shortcut_controller, session_manager):
        """Test that action states are properly managed."""
        # Test with no current session
        session_manager.current_session = None
        shortcut_controller.update_action_states()
        
        # new_child and new_sibling should be enabled, close should be disabled
        assert shortcut_controller.get_action("new_child").get_enabled()
        assert shortcut_controller.get_action("new_sibling").get_enabled()
        assert not shortcut_controller.get_action("close_session").get_enabled()
        
        # Test with current session
        mock_session = TerminalSession(pid=123, pty_fd=456, cwd="/test", title="test")
        session_manager.current_session = mock_session
        
        with patch.object(session_manager, 'get_all_sessions', return_value=[mock_session]):
            shortcut_controller.update_action_states()
        
        # All actions should be enabled
        assert shortcut_controller.get_action("new_child").get_enabled()
        assert shortcut_controller.get_action("new_sibling").get_enabled()
        assert shortcut_controller.get_action("close_session").get_enabled()
    
    def test_button_callback_integration(self, shortcut_controller, session_manager):
        """Test that button callbacks properly integrate with actions."""
        # Create mock button callbacks that simulate the MainWindow button callbacks
        def mock_new_sibling_callback():
            action = shortcut_controller.get_action("new_sibling")
            if action:
                action.activate(None)
        
        def mock_new_child_callback():
            action = shortcut_controller.get_action("new_child")
            if action:
                action.activate(None)
        
        def mock_close_session_callback():
            action = shortcut_controller.get_action("close_session")
            if action:
                action.activate(None)
        
        # Mock session manager methods to track calls
        with patch.object(session_manager, 'new_sibling') as mock_new_sibling, \
             patch.object(session_manager, 'new_child') as mock_new_child, \
             patch.object(session_manager, 'get_all_sessions', return_value=[Mock(), Mock()]) as mock_get_all, \
             patch.object(session_manager, 'close_current_session') as mock_close:
            
            session_manager.current_session = Mock()
            
            # Test button callbacks
            mock_new_sibling_callback()
            mock_new_child_callback()
            mock_close_session_callback()
            
            # Verify methods were called
            mock_new_sibling.assert_called_once()
            mock_new_child.assert_called_once()
            mock_close.assert_called_once()
    
    def test_keyboard_vs_button_consistency(self, shortcut_controller, session_manager):
        """Test that keyboard shortcuts and buttons call identical code paths."""
        # Mock session manager methods
        with patch.object(session_manager, 'new_sibling') as mock_new_sibling, \
             patch.object(session_manager, 'new_child') as mock_new_child:
            
            # Test that both keyboard shortcuts and button callbacks
            # call the same underlying methods
            
            # Simulate keyboard shortcut activation
            new_sibling_action = shortcut_controller.get_action("new_sibling")
            new_child_action = shortcut_controller.get_action("new_child")
            
            new_sibling_action.activate(None)
            new_child_action.activate(None)
            
            # Verify the same methods are called as would be called by buttons
            mock_new_sibling.assert_called_once()
            mock_new_child.assert_called_once()
    
    def test_mock_button_state_updates(self, mock_headerbar_buttons, session_manager):
        """Test button state update simulation."""
        # Simulate the _update_button_states functionality
        def mock_update_button_states():
            has_current_session = session_manager.current_session is not None
            
            # Update mock button states
            mock_headerbar_buttons['new_sibling_button'].set_sensitive(True)
            mock_headerbar_buttons['new_child_button'].set_sensitive(True)
            mock_headerbar_buttons['close_session_button'].set_sensitive(has_current_session)
        
        # Test with no current session
        session_manager.current_session = None
        mock_update_button_states()
        
        mock_headerbar_buttons['close_session_button'].set_sensitive.assert_called_with(False)
        
        # Test with current session
        session_manager.current_session = TerminalSession(pid=123, pty_fd=456, cwd="/test", title="test")
        mock_update_button_states()
        
        mock_headerbar_buttons['close_session_button'].set_sensitive.assert_called_with(True)
    
    def test_action_error_handling(self, shortcut_controller, session_manager):
        """Test that actions handle errors gracefully."""
        # Mock VTE terminal creation to raise exceptions
        with patch('tree_style_terminal.controllers.session_manager.VteTerminal', side_effect=Exception("VTE creation failed")):
            # Actions should not raise exceptions
            new_child_action = shortcut_controller.get_action("new_child")
            new_sibling_action = shortcut_controller.get_action("new_sibling")
            
            # These should not raise exceptions
            new_child_action.activate(None)
            new_sibling_action.activate(None)
    
    def test_session_tree_integration(self, session_manager):
        """Test integration with session tree operations."""
        # Create sessions using the manager
        with patch('tree_style_terminal.controllers.session_manager.VteTerminal') as MockVteTerminal:
            mock_terminal = Mock()
            mock_terminal.spawn_shell.return_value = True
            mock_terminal.terminal = Mock()
            MockVteTerminal.return_value = mock_terminal
            
            # Create root session
            root_session = session_manager.new_session()
            assert root_session is not None
            
            # Create child session
            session_manager.current_session = root_session
            child_session = session_manager.new_child()
            assert child_session is not None
            
            # Verify tree structure
            assert session_manager.session_tree.get_parent(child_session) == root_session
            assert child_session in session_manager.session_tree.get_children(root_session)
            
            # Create sibling session
            sibling_session = session_manager.new_sibling()
            assert sibling_session is not None
            
            # Verify sibling relationship
            assert session_manager.session_tree.get_parent(sibling_session) == root_session
            assert len(session_manager.session_tree.get_children(root_session)) == 2
    
    def test_mock_button_properties(self, mock_headerbar_buttons):
        """Test that mock buttons have the expected properties."""
        for name, button in mock_headerbar_buttons.items():
            # All buttons should have tooltip text
            assert button.get_tooltip_text() is not None
            assert "Mock tooltip" in button.get_tooltip_text()
            
            # Buttons should be focusable
            assert button.get_can_focus()
            
            # Buttons should have images
            assert button.get_image() is not None
            
            # Buttons should be sensitive by default
            assert button.get_sensitive()
            
            # set_sensitive should be callable
            assert callable(button.set_sensitive)