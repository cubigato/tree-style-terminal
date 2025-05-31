"""
Unit tests for the SidebarController.

Tests the TreeStore setup, session management, and synchronization
with the SessionTree model.
"""

import pytest
from unittest.mock import Mock

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from tree_style_terminal.controllers.sidebar import SidebarController
from tree_style_terminal.models.session import TerminalSession
from tree_style_terminal.models.tree import SessionTree


class TestSidebarController:
    """Test cases for SidebarController."""
    
    def test_init_creates_tree_store_with_correct_columns(self):
        """Test that initialization creates TreeStore with object and title columns."""
        session_tree = SessionTree()
        controller = SidebarController(session_tree)
        
        # Verify TreeStore was created
        assert controller.tree_store is not None
        assert isinstance(controller.tree_store, Gtk.TreeStore)
        
        # Verify column count (should be 2: object, title)
        assert controller.tree_store.get_n_columns() == 2
        
        # Verify column indices are defined
        assert controller.COL_OBJECT == 0
        assert controller.COL_TITLE == 1
    
    def test_empty_session_tree_creates_empty_tree_store(self):
        """Test that an empty SessionTree results in an empty TreeStore."""
        session_tree = SessionTree()
        controller = SidebarController(session_tree)
        
        # TreeStore should be empty
        assert len(controller.tree_store) == 0
        assert controller.tree_store.get_iter_first() is None
    
    def test_populate_from_session_tree_with_single_root(self):
        """Test populating TreeStore from SessionTree with one root session."""
        session_tree = SessionTree()
        session = TerminalSession(pid=123, pty_fd=456, cwd="/home/user")
        session_tree.add_node(session)
        
        controller = SidebarController(session_tree)
        
        # TreeStore should have one item
        assert len(controller.tree_store) == 1
        
        # Get the first (and only) item
        tree_iter = controller.tree_store.get_iter_first()
        assert tree_iter is not None
        
        # Verify the stored values
        stored_session = controller.tree_store.get_value(tree_iter, controller.COL_OBJECT)
        stored_title = controller.tree_store.get_value(tree_iter, controller.COL_TITLE)
        
        assert stored_session == session
        assert stored_title == session.title
    
    def test_populate_from_session_tree_with_nested_structure(self):
        """Test populating TreeStore from SessionTree with nested sessions."""
        session_tree = SessionTree()
        
        # Create a nested structure: root -> child1, child2 -> grandchild
        root = TerminalSession(pid=1, pty_fd=10, cwd="/root")
        child1 = TerminalSession(pid=2, pty_fd=20, cwd="/child1")
        child2 = TerminalSession(pid=3, pty_fd=30, cwd="/child2")
        grandchild = TerminalSession(pid=4, pty_fd=40, cwd="/grandchild")
        
        session_tree.add_node(root)
        session_tree.add_node(child1, root)
        session_tree.add_node(child2, root)
        session_tree.add_node(grandchild, child2)
        
        controller = SidebarController(session_tree)
        
        # TreeStore should have one root item
        assert len(controller.tree_store) == 1
        
        # Get root iter and verify it's the root session
        root_iter = controller.tree_store.get_iter_first()
        stored_root = controller.tree_store.get_value(root_iter, controller.COL_OBJECT)
        assert stored_root == root
        
        # Root should have 2 children
        assert controller.tree_store.iter_n_children(root_iter) == 2
        
        # Get first child
        child1_iter = controller.tree_store.iter_children(root_iter)
        stored_child1 = controller.tree_store.get_value(child1_iter, controller.COL_OBJECT)
        assert stored_child1 == child1
        
        # Get second child
        child2_iter = controller.tree_store.iter_next(child1_iter)
        stored_child2 = controller.tree_store.get_value(child2_iter, controller.COL_OBJECT)
        assert stored_child2 == child2
        
        # Child2 should have one grandchild
        assert controller.tree_store.iter_n_children(child2_iter) == 1
        grandchild_iter = controller.tree_store.iter_children(child2_iter)
        stored_grandchild = controller.tree_store.get_value(grandchild_iter, controller.COL_OBJECT)
        assert stored_grandchild == grandchild
    
    def test_add_session_as_root(self):
        """Test adding a session as a root node."""
        session_tree = SessionTree()
        controller = SidebarController(session_tree)
        
        session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
        controller.add_session(session)
        
        # TreeStore should now have one item
        assert len(controller.tree_store) == 1
        
        # Verify the session is stored correctly
        tree_iter = controller.tree_store.get_iter_first()
        stored_session = controller.tree_store.get_value(tree_iter, controller.COL_OBJECT)
        stored_title = controller.tree_store.get_value(tree_iter, controller.COL_TITLE)
        
        assert stored_session == session
        assert stored_title == session.title
        
        # Verify mapping is maintained (check by verifying the session can be found)
        found_iter = controller.find_iter_for_session(session)
        found_session = controller.tree_store.get_value(found_iter, controller.COL_OBJECT)
        assert found_session == session
    
    def test_add_session_as_child(self):
        """Test adding a session as a child of an existing session."""
        session_tree = SessionTree()
        controller = SidebarController(session_tree)
        
        # Add parent first
        parent = TerminalSession(pid=1, pty_fd=10, cwd="/parent")
        controller.add_session(parent)
        
        # Add child
        child = TerminalSession(pid=2, pty_fd=20, cwd="/child")
        controller.add_session(child, parent)
        
        # Root should still have one item (the parent)
        assert len(controller.tree_store) == 1
        
        # Parent should have one child
        parent_iter = controller.tree_store.get_iter_first()
        assert controller.tree_store.iter_n_children(parent_iter) == 1
        
        # Verify child is stored correctly
        child_iter = controller.tree_store.iter_children(parent_iter)
        stored_child = controller.tree_store.get_value(child_iter, controller.COL_OBJECT)
        assert stored_child == child
    
    def test_remove_session(self):
        """Test removing a session from the TreeStore."""
        session_tree = SessionTree()
        controller = SidebarController(session_tree)
        
        # Add a session
        session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
        controller.add_session(session)
        
        # Verify it's there
        assert len(controller.tree_store) == 1
        assert session in controller._session_to_iter
        
        # Remove it
        controller.remove_session(session)
        
        # Verify it's gone
        assert len(controller.tree_store) == 0
        assert session not in controller._session_to_iter
    
    def test_update_session_title(self):
        """Test updating a session's title."""
        session_tree = SessionTree()
        controller = SidebarController(session_tree)
        
        # Add a session
        session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
        controller.add_session(session)
        
        # Update title
        new_title = "New Title"
        controller.update_session_title(session, new_title)
        
        # Verify title was updated in both session and TreeStore
        assert session.title == new_title
        
        tree_iter = controller.tree_store.get_iter_first()
        stored_title = controller.tree_store.get_value(tree_iter, controller.COL_TITLE)
        assert stored_title == new_title
    
    def test_get_session_from_iter(self):
        """Test retrieving a session object from a TreeIter."""
        session_tree = SessionTree()
        controller = SidebarController(session_tree)
        
        session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
        controller.add_session(session)
        
        tree_iter = controller.tree_store.get_iter_first()
        retrieved_session = controller.get_session_from_iter(tree_iter)
        
        assert retrieved_session == session
    
    def test_find_iter_for_session(self):
        """Test finding a TreeIter for a given session."""
        session_tree = SessionTree()
        controller = SidebarController(session_tree)
        
        session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
        controller.add_session(session)
        
        found_iter = controller.find_iter_for_session(session)
        expected_iter = controller.tree_store.get_iter_first()
        
        # TreeIter comparison might not work directly, so compare the stored objects
        found_session = controller.tree_store.get_value(found_iter, controller.COL_OBJECT)
        expected_session = controller.tree_store.get_value(expected_iter, controller.COL_OBJECT)
        
        assert found_session == expected_session == session
    
    def test_sync_with_session_tree(self):
        """Test full synchronization with SessionTree."""
        session_tree = SessionTree()
        
        # Add some sessions to the tree
        session1 = TerminalSession(pid=1, pty_fd=10, cwd="/one")
        session2 = TerminalSession(pid=2, pty_fd=20, cwd="/two")
        session_tree.add_node(session1)
        session_tree.add_node(session2, session1)
        
        # Create controller (should be populated)
        controller = SidebarController(session_tree)
        assert len(controller.tree_store) == 1  # One root
        
        # Modify the session tree directly
        session3 = TerminalSession(pid=3, pty_fd=30, cwd="/three")
        session_tree.add_node(session3)  # Add another root
        
        # TreeStore is out of sync
        assert len(controller.tree_store) == 1
        
        # Sync and verify
        controller.sync_with_session_tree()
        assert len(controller.tree_store) == 2  # Now has both roots
    
    def test_bind_session_tree_events_placeholder(self):
        """Test that bind_session_tree_events exists but doesn't crash."""
        session_tree = SessionTree()
        controller = SidebarController(session_tree)
        
        # Should not raise an exception
        controller.bind_session_tree_events()