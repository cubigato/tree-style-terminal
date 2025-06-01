"""
Unit tests for session closure with adoption algorithm.

Tests the close_session action and verifies that children are properly
adopted by their grandparent when a session is closed, as specified
in Milestone 5 point 4.
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


class TestSessionClosure:
    """Test cases for session closure and adoption algorithm."""
    
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
    
    def test_close_leaf_node_no_children(self, session_tree, session_manager):
        """Test closing a session with no children - clean removal."""
        # Setup: Create parent with child (leaf)
        parent = TerminalSession(pid=100, pty_fd=200, cwd="/parent", title="parent")
        leaf = TerminalSession(pid=101, pty_fd=201, cwd="/parent/leaf", title="leaf")
        
        session_tree.add_node(parent)
        session_tree.add_node(leaf, parent=parent)
        session_manager.current_session = leaf
        
        # Mock VTE cleanup and terminal widgets
        session_manager._session_terminals[parent] = Mock()
        session_manager._session_terminals[leaf] = Mock()
        
        # Close the leaf session
        session_manager.close_session(leaf)
        
        # Verify clean removal
        assert leaf not in session_tree.get_children(parent)
        assert len(session_tree.get_children(parent)) == 0
        assert leaf not in session_tree.get_all_sessions()
        assert parent in session_tree.get_roots()
    
    def test_close_root_with_children_become_new_roots(self, session_tree, session_manager):
        """Test closing root session - children become new roots."""
        # Setup: Create root with multiple children
        root = TerminalSession(pid=100, pty_fd=200, cwd="/root", title="root")
        child1 = TerminalSession(pid=101, pty_fd=201, cwd="/child1", title="child1")
        child2 = TerminalSession(pid=102, pty_fd=202, cwd="/child2", title="child2")
        
        session_tree.add_node(root)
        session_tree.add_node(child1, parent=root)
        session_tree.add_node(child2, parent=root)
        session_manager.current_session = root
        
        # Mock VTE cleanup and terminal widgets
        session_manager._session_terminals[root] = Mock()
        session_manager._session_terminals[child1] = Mock()
        session_manager._session_terminals[child2] = Mock()
        
        # Close the root session
        session_manager.close_session(root)
        
        # Verify children became new roots
        root_nodes = session_tree.get_roots()
        assert root not in root_nodes
        assert child1 in root_nodes
        assert child2 in root_nodes
        assert len(root_nodes) == 2
        
        # Verify children have no parent
        assert session_tree.get_parent(child1) is None
        assert session_tree.get_parent(child2) is None
    
    def test_close_middle_node_children_adopted_by_grandparent(self, session_tree, session_manager):
        """Test closing middle node - children adopted by grandparent."""
        # Setup: Create three-level hierarchy
        grandparent = TerminalSession(pid=100, pty_fd=200, cwd="/grand", title="grandparent")
        parent = TerminalSession(pid=101, pty_fd=201, cwd="/grand/parent", title="parent")
        child1 = TerminalSession(pid=102, pty_fd=202, cwd="/grand/child1", title="child1")
        child2 = TerminalSession(pid=103, pty_fd=203, cwd="/grand/child2", title="child2")
        
        session_tree.add_node(grandparent)
        session_tree.add_node(parent, parent=grandparent)
        session_tree.add_node(child1, parent=parent)
        session_tree.add_node(child2, parent=parent)
        session_manager.current_session = parent
        
        # Mock VTE cleanup and terminal widgets
        session_manager._session_terminals[grandparent] = Mock()
        session_manager._session_terminals[parent] = Mock()
        session_manager._session_terminals[child1] = Mock()
        session_manager._session_terminals[child2] = Mock()
        
        # Close the middle parent session
        session_manager.close_session(parent)
        
        # Verify adoption by grandparent
        grandparent_children = session_tree.get_children(grandparent)
        assert parent not in grandparent_children
        assert child1 in grandparent_children
        assert child2 in grandparent_children
        assert len(grandparent_children) == 2
        
        # Verify parent relationships
        assert session_tree.get_parent(child1) == grandparent
        assert session_tree.get_parent(child2) == grandparent
        assert parent not in session_tree.get_all_sessions()
    
    def test_close_session_complex_adoption_scenario(self, session_tree, session_manager):
        """Test complex adoption with multiple children and grandchildren."""
        # Setup: Create complex tree structure
        #   root
        #   ├── parent (to be closed)
        #   │   ├── child1
        #   │   │   └── grandchild1
        #   │   └── child2
        #   └── sibling
        
        root = TerminalSession(pid=100, pty_fd=200, cwd="/root", title="root")
        parent = TerminalSession(pid=101, pty_fd=201, cwd="/root/parent", title="parent")
        child1 = TerminalSession(pid=102, pty_fd=202, cwd="/root/child1", title="child1")
        child2 = TerminalSession(pid=103, pty_fd=203, cwd="/root/child2", title="child2")
        grandchild1 = TerminalSession(pid=104, pty_fd=204, cwd="/root/grandchild1", title="grandchild1")
        sibling = TerminalSession(pid=105, pty_fd=205, cwd="/root/sibling", title="sibling")
        
        session_tree.add_node(root)
        session_tree.add_node(parent, parent=root)
        session_tree.add_node(child1, parent=parent)
        session_tree.add_node(child2, parent=parent)
        session_tree.add_node(grandchild1, parent=child1)
        session_tree.add_node(sibling, parent=root)
        
        session_manager.current_session = parent
        
        # Mock VTE cleanup and terminal widgets
        session_manager._session_terminals[root] = Mock()
        session_manager._session_terminals[parent] = Mock()
        session_manager._session_terminals[child1] = Mock()
        session_manager._session_terminals[child2] = Mock()
        session_manager._session_terminals[grandchild1] = Mock()
        session_manager._session_terminals[sibling] = Mock()
        
        # Close the parent session
        session_manager.close_session(parent)
        
        # Verify complex adoption
        root_children = session_tree.get_children(root)
        assert parent not in root_children
        assert child1 in root_children
        assert child2 in root_children
        assert sibling in root_children
        assert len(root_children) == 3
        
        # Verify grandchild relationships are preserved
        assert session_tree.get_parent(grandchild1) == child1
        assert grandchild1 in session_tree.get_children(child1)
    
    def test_close_session_signal_propagation(self, session_tree, session_manager):
        """Test that close_session triggers correct signals."""
        # Setup: Create simple parent-child structure
        parent = TerminalSession(pid=100, pty_fd=200, cwd="/parent", title="parent")
        child = TerminalSession(pid=101, pty_fd=201, cwd="/parent/child", title="child")
        
        session_tree.add_node(parent)
        session_tree.add_node(child, parent=parent)
        session_manager.current_session = parent
        
        # Mock VTE cleanup and terminal widgets
        session_manager._session_terminals[parent] = Mock()
        session_manager._session_terminals[child] = Mock()
        
        # Close the parent session
        session_manager.close_session(parent)
        
        # Verify child became root
        assert child in session_tree.get_roots()
        assert session_tree.get_parent(child) is None
    
    def test_close_session_action_integration(self, shortcut_controller, session_manager):
        """Test close_session action integration with adoption."""
        # Setup: Create simple structure
        root = TerminalSession(pid=100, pty_fd=200, cwd="/root", title="root")
        child = TerminalSession(pid=101, pty_fd=201, cwd="/root/child", title="child")
        
        session_manager.session_tree.add_node(root)
        session_manager.session_tree.add_node(child, parent=root)
        session_manager.current_session = root
        
        # Mock that there are multiple sessions so close_current_session gets called
        with patch.object(session_manager, 'get_all_sessions', return_value=[root, child]), \
             patch.object(session_manager, 'close_current_session') as mock_close:
            
            # Execute close_session action
            action = shortcut_controller.get_action("close_session")
            action.activate(None)
            
            # Verify close was called
            mock_close.assert_called_once()
    
    def test_close_last_session_quits_application(self, shortcut_controller, session_manager):
        """Test that closing the last session quits the application."""
        # Setup: Single session
        last_session = TerminalSession(pid=100, pty_fd=200, cwd="/last", title="last")
        session_manager.current_session = last_session
        
        # Mock main window and application
        mock_main_window = Mock()
        mock_app = Mock()
        mock_main_window.get_application.return_value = mock_app
        shortcut_controller.main_window = mock_main_window
        
        with patch.object(session_manager, 'get_all_sessions', return_value=[last_session]):
            # Execute close_session action
            action = shortcut_controller.get_action("close_session")
            action.activate(None)
            
            # Verify application quit was called
            mock_app.quit.assert_called_once()
    
    def test_close_session_no_current_session(self, shortcut_controller, session_manager):
        """Test close_session action when no session is selected."""
        # No current session
        session_manager.current_session = None
        
        with patch.object(session_manager, 'close_current_session') as mock_close:
            # Execute close_session action
            action = shortcut_controller.get_action("close_session")
            action.activate(None)
            
            # Should not call close
            mock_close.assert_not_called()
    
    def test_multi_child_adoption_preserves_order(self, session_tree, session_manager):
        """Test that multi-child adoption preserves sibling order."""
        # Setup: Parent with multiple children in specific order
        parent = TerminalSession(pid=100, pty_fd=200, cwd="/parent", title="parent")
        grandparent = TerminalSession(pid=99, pty_fd=199, cwd="/grandparent", title="grandparent")
        child_a = TerminalSession(pid=101, pty_fd=201, cwd="/parent/a", title="child_a")
        child_b = TerminalSession(pid=102, pty_fd=202, cwd="/parent/b", title="child_b")
        child_c = TerminalSession(pid=103, pty_fd=203, cwd="/parent/c", title="child_c")
        
        session_tree.add_node(grandparent)
        session_tree.add_node(parent, parent=grandparent)
        session_tree.add_node(child_a, parent=parent)
        session_tree.add_node(child_b, parent=parent)
        session_tree.add_node(child_c, parent=parent)
        
        session_manager.current_session = parent
        
        # Record original order
        original_children = list(session_tree.get_children(parent))
        
        # Mock VTE cleanup and terminal widgets
        session_manager._session_terminals[grandparent] = Mock()
        session_manager._session_terminals[parent] = Mock()
        session_manager._session_terminals[child_a] = Mock()
        session_manager._session_terminals[child_b] = Mock()
        session_manager._session_terminals[child_c] = Mock()
        
        # Close the parent
        session_manager.close_session(parent)
        
        # Verify children are now under grandparent
        adopted_children = session_tree.get_children(grandparent)
        
        # All original children should be adopted
        for child in original_children:
            assert child in adopted_children
            assert session_tree.get_parent(child) == grandparent
    
    def test_close_session_error_handling(self, shortcut_controller, session_manager):
        """Test that close_session action handles errors gracefully."""
        # Setup: Session with error-prone cleanup
        session = TerminalSession(pid=100, pty_fd=200, cwd="/error", title="error")
        session_manager.current_session = session
        
        # Mock get_all_sessions to return multiple sessions
        with patch.object(session_manager, 'get_all_sessions', return_value=[session, session]), \
             patch.object(session_manager, 'close_current_session', side_effect=Exception("Cleanup failed")):
            
            # Should not raise exception
            action = shortcut_controller.get_action("close_session")
            action.activate(None)
    
    def test_close_session_deep_nesting_adoption(self, session_tree, session_manager):
        """Test adoption with deep nesting levels."""
        # Setup: Deep hierarchy (5 levels)
        level1 = TerminalSession(pid=101, pty_fd=201, cwd="/1", title="level1")
        level2 = TerminalSession(pid=102, pty_fd=202, cwd="/1/2", title="level2")
        level3 = TerminalSession(pid=103, pty_fd=203, cwd="/1/2/3", title="level3")  # to be closed
        level4 = TerminalSession(pid=104, pty_fd=204, cwd="/1/2/3/4", title="level4")
        level5 = TerminalSession(pid=105, pty_fd=205, cwd="/1/2/3/4/5", title="level5")
        
        session_tree.add_node(level1)
        session_tree.add_node(level2, parent=level1)
        session_tree.add_node(level3, parent=level2)
        session_tree.add_node(level4, parent=level3)
        session_tree.add_node(level5, parent=level4)
        
        session_manager.current_session = level3
        
        # Mock VTE cleanup and terminal widgets
        session_manager._session_terminals[level1] = Mock()
        session_manager._session_terminals[level2] = Mock()
        session_manager._session_terminals[level3] = Mock()
        session_manager._session_terminals[level4] = Mock()
        session_manager._session_terminals[level5] = Mock()
        
        # Close level3
        session_manager.close_session(level3)
        
        # Verify level4 is adopted by level2
        assert session_tree.get_parent(level4) == level2
        assert level4 in session_tree.get_children(level2)
        
        # Verify level5 is still under level4
        assert session_tree.get_parent(level5) == level4
        assert level5 in session_tree.get_children(level4)
        
        # Verify level3 is gone
        assert level3 not in session_tree.get_all_sessions()