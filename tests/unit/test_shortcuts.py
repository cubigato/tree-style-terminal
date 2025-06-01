"""
Unit tests for ShortcutController.

Tests action creation, callback execution, and state management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib

from tree_style_terminal.controllers.shortcuts import ShortcutController
from tree_style_terminal.controllers.session_manager import SessionManager
from tree_style_terminal.models.tree import SessionTree
from tree_style_terminal.models.session import TerminalSession


class TestShortcutController:
    """Test cases for ShortcutController."""
    
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
    
    def test_initialization(self, shortcut_controller):
        """Test that ShortcutController initializes correctly."""
        assert shortcut_controller.session_manager is not None
        assert len(shortcut_controller._actions) == 8
    
    def test_actions_created(self, shortcut_controller):
        """Test that all required actions are created."""
        assert shortcut_controller.get_action("new_child") is not None
        assert shortcut_controller.get_action("new_sibling") is not None
        assert shortcut_controller.get_action("close_session") is not None
        
        # Verify they are Gio.SimpleAction instances
        assert isinstance(shortcut_controller.get_action("new_child"), Gio.SimpleAction)
        assert isinstance(shortcut_controller.get_action("new_sibling"), Gio.SimpleAction)
        assert isinstance(shortcut_controller.get_action("close_session"), Gio.SimpleAction)
    
    def test_actions_initially_enabled(self, shortcut_controller):
        """Test that actions are initially enabled."""
        assert shortcut_controller.get_action("new_child").get_enabled()
        assert shortcut_controller.get_action("new_sibling").get_enabled()
        assert shortcut_controller.get_action("close_session").get_enabled()
    
    def test_new_child_action_success(self, shortcut_controller, session_manager):
        """Test new_child action execution with successful session creation."""
        mock_session = TerminalSession(pid=123, pty_fd=456, cwd="/test", title="test")
        
        with patch.object(session_manager, 'new_child', return_value=mock_session) as mock_new_child:
            action = shortcut_controller.get_action("new_child")
            action.activate(None)
            
            mock_new_child.assert_called_once()
    
    def test_new_child_action_failure(self, shortcut_controller, session_manager):
        """Test new_child action execution with failed session creation."""
        with patch.object(session_manager, 'new_child', return_value=None) as mock_new_child:
            action = shortcut_controller.get_action("new_child")
            action.activate(None)
            
            mock_new_child.assert_called_once()
    
    def test_new_child_action_exception(self, shortcut_controller, session_manager):
        """Test new_child action handles exceptions gracefully."""
        with patch.object(session_manager, 'new_child', side_effect=Exception("Test error")) as mock_new_child:
            action = shortcut_controller.get_action("new_child")
            # Should not raise exception
            action.activate(None)
            
            mock_new_child.assert_called_once()
    
    def test_new_sibling_action_success(self, shortcut_controller, session_manager):
        """Test new_sibling action execution with successful session creation."""
        mock_session = TerminalSession(pid=123, pty_fd=456, cwd="/test", title="test")
        
        with patch.object(session_manager, 'new_sibling', return_value=mock_session) as mock_new_sibling:
            action = shortcut_controller.get_action("new_sibling")
            action.activate(None)
            
            mock_new_sibling.assert_called_once()
    
    def test_new_sibling_action_failure(self, shortcut_controller, session_manager):
        """Test new_sibling action execution with failed session creation."""
        with patch.object(session_manager, 'new_sibling', return_value=None) as mock_new_sibling:
            action = shortcut_controller.get_action("new_sibling")
            action.activate(None)
            
            mock_new_sibling.assert_called_once()
    
    def test_new_sibling_action_exception(self, shortcut_controller, session_manager):
        """Test new_sibling action handles exceptions gracefully."""
        with patch.object(session_manager, 'new_sibling', side_effect=Exception("Test error")) as mock_new_sibling:
            action = shortcut_controller.get_action("new_sibling")
            # Should not raise exception
            action.activate(None)
            
            mock_new_sibling.assert_called_once()
    
    def test_close_session_action_with_current_session(self, shortcut_controller, session_manager):
        """Test close_session action when there is a current session."""
        mock_session = TerminalSession(pid=123, pty_fd=456, cwd="/test", title="test")
        mock_session2 = TerminalSession(pid=124, pty_fd=457, cwd="/test2", title="test2")
        session_manager.current_session = mock_session
        
        # Mock get_all_sessions to return multiple sessions so close_current_session gets called
        with patch.object(session_manager, 'get_all_sessions', return_value=[mock_session, mock_session2]) as mock_get_all, \
             patch.object(session_manager, 'close_current_session') as mock_close:
            action = shortcut_controller.get_action("close_session")
            action.activate(None)
            
            mock_close.assert_called_once()
    
    def test_close_session_action_without_current_session(self, shortcut_controller, session_manager):
        """Test close_session action when there is no current session."""
        session_manager.current_session = None
        
        with patch.object(session_manager, 'close_current_session') as mock_close:
            action = shortcut_controller.get_action("close_session")
            action.activate(None)
            
            mock_close.assert_not_called()
    
    def test_close_session_action_exception(self, shortcut_controller, session_manager):
        """Test close_session action handles exceptions gracefully."""
        mock_session = TerminalSession(pid=123, pty_fd=456, cwd="/test", title="test")
        mock_session2 = TerminalSession(pid=124, pty_fd=457, cwd="/test2", title="test2")
        session_manager.current_session = mock_session
        
        # Mock get_all_sessions to return multiple sessions so close_current_session gets called
        with patch.object(session_manager, 'get_all_sessions', return_value=[mock_session, mock_session2]) as mock_get_all, \
             patch.object(session_manager, 'close_current_session', side_effect=Exception("Test error")) as mock_close:
            action = shortcut_controller.get_action("close_session")
            # Should not raise exception
            action.activate(None)
            
            mock_close.assert_called_once()
    
    def test_get_action_existing(self, shortcut_controller):
        """Test getting an existing action."""
        action = shortcut_controller.get_action("new_child")
        assert action is not None
        assert isinstance(action, Gio.SimpleAction)
    
    def test_get_action_nonexistent(self, shortcut_controller):
        """Test getting a non-existent action."""
        action = shortcut_controller.get_action("nonexistent")
        assert action is None
    
    def test_enable_action_existing(self, shortcut_controller):
        """Test enabling/disabling an existing action."""
        action_name = "new_child"
        action = shortcut_controller.get_action(action_name)
        
        # Initially enabled
        assert action.get_enabled()
        
        # Disable
        shortcut_controller.enable_action(action_name, False)
        assert not action.get_enabled()
        
        # Re-enable
        shortcut_controller.enable_action(action_name, True)
        assert action.get_enabled()
    
    def test_enable_action_nonexistent(self, shortcut_controller):
        """Test enabling a non-existent action."""
        # Should not raise exception
        shortcut_controller.enable_action("nonexistent", True)
    
    def test_add_actions_to_widget_with_support(self, shortcut_controller):
        """Test adding actions to a widget that supports actions."""
        mock_widget = Mock()
        mock_widget.add_action = Mock()
        mock_widget.__class__.__name__ = "MockWindow"
        
        shortcut_controller.add_actions_to_widget(mock_widget)
        
        # Should have called add_action for each action
        assert mock_widget.add_action.call_count == 8
    
    def test_add_actions_to_widget_without_support(self, shortcut_controller):
        """Test adding actions to a widget that doesn't support actions."""
        mock_widget = Mock(spec=[])  # No add_action method
        mock_widget.__class__.__name__ = "MockWidget"
        
        # Should not raise exception
        shortcut_controller.add_actions_to_widget(mock_widget)
    
    def test_update_action_states_with_current_session(self, shortcut_controller, session_manager):
        """Test updating action states when there is a current session."""
        mock_session = TerminalSession(pid=123, pty_fd=456, cwd="/test", title="test")
        mock_session2 = TerminalSession(pid=124, pty_fd=457, cwd="/test2", title="test2")
        session_manager.current_session = mock_session
        
        with patch.object(session_manager, 'get_all_sessions', return_value=[mock_session, mock_session2]):
            shortcut_controller.update_action_states()
        
        # All actions should be enabled
        assert shortcut_controller.get_action("new_child").get_enabled()
        assert shortcut_controller.get_action("new_sibling").get_enabled()
        assert shortcut_controller.get_action("close_session").get_enabled()
    
    def test_update_action_states_without_current_session(self, shortcut_controller, session_manager):
        """Test updating action states when there is no current session."""
        session_manager.current_session = None
        
        with patch.object(session_manager, 'get_all_sessions', return_value=[]):
            shortcut_controller.update_action_states()
        
        # new_child and new_sibling should be enabled, close_session should be disabled
        assert shortcut_controller.get_action("new_child").get_enabled()
        assert shortcut_controller.get_action("new_sibling").get_enabled()
        assert not shortcut_controller.get_action("close_session").get_enabled()
    
    def test_close_session_action_last_session(self, shortcut_controller, session_manager):
        """Test close_session action when it's the last session (should quit app)."""
        mock_session = TerminalSession(pid=123, pty_fd=456, cwd="/test", title="test")
        session_manager.current_session = mock_session
        
        # Mock main_window and get_all_sessions to simulate last session
        mock_main_window = Mock()
        mock_app = Mock()
        mock_main_window.get_application.return_value = mock_app
        shortcut_controller.main_window = mock_main_window
        
        with patch.object(session_manager, 'get_all_sessions', return_value=[mock_session]) as mock_get_all:
            action = shortcut_controller.get_action("close_session")
            action.activate(None)
            
            mock_app.quit.assert_called_once()
    
    def test_additional_actions_exist(self, shortcut_controller):
        """Test that all additional actions are created."""
        assert shortcut_controller.get_action("toggle_sidebar") is not None
        assert shortcut_controller.get_action("focus_terminal") is not None
        assert shortcut_controller.get_action("focus_sidebar") is not None
        assert shortcut_controller.get_action("next_session") is not None
        assert shortcut_controller.get_action("prev_session") is not None
        
        # Verify they are Gio.SimpleAction instances
        assert isinstance(shortcut_controller.get_action("toggle_sidebar"), Gio.SimpleAction)
        assert isinstance(shortcut_controller.get_action("focus_terminal"), Gio.SimpleAction)
        assert isinstance(shortcut_controller.get_action("focus_sidebar"), Gio.SimpleAction)
        assert isinstance(shortcut_controller.get_action("next_session"), Gio.SimpleAction)
        assert isinstance(shortcut_controller.get_action("prev_session"), Gio.SimpleAction)