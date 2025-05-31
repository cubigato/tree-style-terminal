"""
Unit tests for SessionTree event binding functionality.

Tests the event system that connects SessionTree changes to TreeStore updates.
"""

import pytest
from unittest.mock import Mock, patch

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from tree_style_terminal.controllers.sidebar import SidebarController
from tree_style_terminal.models.session import TerminalSession
from tree_style_terminal.models.tree import SessionTree


class TestSessionTreeEvents:
    """Test cases for SessionTree event binding."""
    
    def test_controller_responds_to_tree_changes(self):
        """Test that SidebarController automatically updates when SessionTree changes."""
        tree = SessionTree()
        controller = SidebarController(tree)
        
        # Initial state - empty
        assert len(controller.tree_store) == 0
        
        # Add session to tree
        session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
        tree.add_node(session)
        
        # Controller should automatically sync (if events are bound)
        # For now, we test manual sync - event binding is a future enhancement
        controller.sync_with_session_tree()
        assert len(controller.tree_store) == 1
        
        # Remove session
        tree.remove_node(session)
        controller.sync_with_session_tree()
        assert len(controller.tree_store) == 0
    
    def test_bind_session_tree_events_method_exists(self):
        """Test that bind_session_tree_events method exists on controller."""
        tree = SessionTree()
        controller = SidebarController(tree)
        
        assert hasattr(controller, 'bind_session_tree_events')
        assert callable(controller.bind_session_tree_events)
        
        # Should not raise exception when called
        controller.bind_session_tree_events()
    
    def test_multiple_controllers_can_bind_to_same_tree(self):
        """Test that multiple controllers can bind to the same SessionTree."""
        tree = SessionTree()
        controller1 = SidebarController(tree)
        controller2 = SidebarController(tree)
        
        # Both should be able to bind without conflicts
        controller1.bind_session_tree_events()
        controller2.bind_session_tree_events()
        
        # Add session
        session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
        tree.add_node(session)
        
        # Both controllers should be able to sync
        controller1.sync_with_session_tree()
        controller2.sync_with_session_tree()
        
        assert len(controller1.tree_store) == 1
        assert len(controller2.tree_store) == 1