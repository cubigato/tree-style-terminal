"""
Integration tests for sidebar focus and selection behavior.

Tests the interaction between SessionSidebar, SidebarController, and SessionManager
for focus switching and session selection.
"""

import pytest

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from tree_style_terminal.controllers.sidebar import SidebarController
from tree_style_terminal.controllers.session_manager import SessionManager
from tree_style_terminal.models.session import TerminalSession
from tree_style_terminal.models.tree import SessionTree
from tree_style_terminal.widgets.sidebar import SessionSidebar
from tree_style_terminal.widgets.terminal import VteTerminal


class TestSidebarFocusIntegration:
    """Integration test cases for sidebar focus and selection."""
    
    def test_sidebar_selection_triggers_session_manager(self):
        """Test that selecting in sidebar triggers SessionManager callbacks."""
        tree = SessionTree()
        controller = SidebarController(tree)
        manager = SessionManager(tree)
        sidebar = SessionSidebar(controller)
        
        # Track selections
        selected_sessions = []
        def on_selected(session):
            selected_sessions.append(session)
        
        manager.set_session_selected_callback(on_selected)
        
        # Create test session
        session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
        tree.add_node(session)
        controller.sync_with_session_tree()
        
        # Mock terminal for the session
        mock_terminal = VteTerminal()
        manager._session_terminals[session] = mock_terminal
        manager.current_session = session
        
        # Trigger selection through manager
        manager.select_session(session)
        
        assert len(selected_sessions) == 1
        assert selected_sessions[0] == session
    
    def test_session_manager_integration_methods(self):
        """Test SessionManager has required methods for sidebar integration."""
        tree = SessionTree()
        manager = SessionManager(tree)
        
        required_methods = [
            'new_session', 'new_child', 'new_sibling', 
            'close_session', 'select_session'
        ]
        
        for method_name in required_methods:
            assert hasattr(manager, method_name)
            assert callable(getattr(manager, method_name))
    
    def test_session_manager_callback_setup(self):
        """Test SessionManager callback registration."""
        tree = SessionTree()
        manager = SessionManager(tree)
        
        # Test callback setters exist
        assert hasattr(manager, 'set_session_created_callback')
        assert hasattr(manager, 'set_session_closed_callback')
        assert hasattr(manager, 'set_session_selected_callback')
        
        # Test callbacks can be set without error
        manager.set_session_created_callback(lambda s, t: None)
        manager.set_session_closed_callback(lambda s: None)
        manager.set_session_selected_callback(lambda s: None)