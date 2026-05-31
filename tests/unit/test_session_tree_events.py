"""
Unit tests for manual SessionTree synchronization.

Tests the sync path that connects SessionTree changes to TreeStore updates.
"""

import gi

gi.require_version('Gtk', '3.0')

from tree_style_terminal.controllers.sidebar import SidebarController
from tree_style_terminal.models.session import TerminalSession
from tree_style_terminal.models.tree import SessionTree


class TestSessionTreeEvents:
    """Test cases for SessionTree synchronization."""

    def test_controller_responds_to_tree_changes(self):
        """Test that SidebarController updates after explicit sync."""
        tree = SessionTree()
        controller = SidebarController(tree)

        # Initial state - empty
        assert len(controller.tree_store) == 0

        # Add session to tree
        session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
        tree.add_node(session)

        # Controller sync is explicit; SessionSidebar.refresh() calls this path.
        controller.sync_with_session_tree()
        assert len(controller.tree_store) == 1

        # Remove session
        tree.remove_node(session)
        controller.sync_with_session_tree()
        assert len(controller.tree_store) == 0

    def test_multiple_controllers_can_sync_to_same_tree(self):
        """Test that multiple controllers can manually sync to the same SessionTree."""
        tree = SessionTree()
        controller1 = SidebarController(tree)
        controller2 = SidebarController(tree)

        # Add session
        session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
        tree.add_node(session)

        # Both controllers should be able to sync
        controller1.sync_with_session_tree()
        controller2.sync_with_session_tree()

        assert len(controller1.tree_store) == 1
        assert len(controller2.tree_store) == 1
