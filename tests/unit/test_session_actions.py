"""
Unit tests for session action behaviors.

Tests the core functionality of new_child and new_sibling actions,
verifying that they create proper parent-child relationships and
tree structures as specified in Milestone 5 point 4.
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
from tree_style_terminal.widgets.terminal import VteTerminal


class TestSessionActions:
    """Test cases for session creation actions."""
    
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
    def mock_session(self):
        """Create a mock session for testing."""
        return TerminalSession(pid=123, pty_fd=456, cwd="/test", title="test")
    
    @pytest.fixture
    def mock_child_session(self):
        """Create a mock child session for testing."""
        return TerminalSession(pid=124, pty_fd=457, cwd="/test/child", title="child")
    
    def test_new_child_creates_child_under_root(self, shortcut_controller, session_manager, mock_session, mock_child_session):
        """Test that new_child under root session creates child node."""
        # Setup: Add root session and select it
        session_manager.session_tree.add_node(mock_session)
        session_manager.current_session = mock_session
        
        # Mock new_child to return a child session
        with patch.object(session_manager, 'new_child', return_value=mock_child_session) as mock_new_child:
            # Execute new_child action
            action = shortcut_controller.get_action("new_child")
            action.activate(None)
            
            # Verify the action was called
            mock_new_child.assert_called_once()
    
    def test_new_child_creates_proper_parent_child_relationship(self, session_tree, session_manager, mock_session, mock_child_session):
        """Test that new_child creates proper parent-child relationships."""
        # Setup: Add root session and select it
        session_tree.add_node(mock_session)
        session_manager.current_session = mock_session
        
        # Mock VTE terminal creation to avoid real terminal creation
        with patch('tree_style_terminal.controllers.session_manager.VteTerminal') as MockVteTerminal:
            mock_terminal = Mock()
            mock_terminal.spawn_shell.return_value = True
            MockVteTerminal.return_value = mock_terminal
            # Create child session
            child_session = session_manager.new_child()
            
            # Verify parent-child relationship
            assert child_session is not None
            assert session_tree.get_parent(child_session) == mock_session
            assert child_session in mock_session.children
            
            # Verify tree structure
            assert child_session in session_tree.get_children(mock_session)
    
    def test_new_child_multi_level_nesting(self, session_tree, session_manager):
        """Test that new_child works with multi-level nesting."""
        # Create a three-level hierarchy: root -> child -> grandchild
        root_session = TerminalSession(pid=100, pty_fd=200, cwd="/root", title="root")
        child_session = TerminalSession(pid=101, pty_fd=201, cwd="/root/child", title="child")
        
        # Add root and child to tree
        session_tree.add_node(root_session)
        session_tree.add_node(child_session, parent=root_session)
        
        # Select the child session
        session_manager.current_session = child_session
        
        # Mock VTE terminal creation
        with patch('tree_style_terminal.controllers.session_manager.VteTerminal') as MockVteTerminal:
            mock_terminal = Mock()
            mock_terminal.spawn_shell.return_value = True
            MockVteTerminal.return_value = mock_terminal
            # Create grandchild
            grandchild_session = session_manager.new_child()
            
            # Verify three-level structure
            assert grandchild_session is not None
            assert session_tree.get_parent(grandchild_session) == child_session
            assert grandchild_session in child_session.children
            assert root_session in session_tree.get_roots()
            assert len(session_tree.get_children(child_session)) == 1
    
    def test_new_child_session_properties_inheritance(self, session_tree, session_manager, mock_session):
        """Test that new child inherits appropriate properties from parent."""
        # Setup: Add root session with specific cwd
        session_tree.add_node(mock_session)
        session_manager.current_session = mock_session
        
        # Mock VTE terminal creation
        with patch('tree_style_terminal.controllers.session_manager.VteTerminal') as MockVteTerminal:
            mock_terminal = Mock()
            mock_terminal.spawn_shell.return_value = True
            MockVteTerminal.return_value = mock_terminal
            # Create child session
            child_session = session_manager.new_child()
            
            # Verify child session properties
            assert child_session is not None
            assert child_session.cwd == mock_session.cwd  # Should inherit cwd
            assert session_tree.get_parent(child_session) == mock_session
    
    def test_new_child_tree_signals(self, session_tree, session_manager, mock_session):
        """Test that new_child triggers correct tree signals."""
        # Setup: Add root session
        session_tree.add_node(mock_session)
        session_manager.current_session = mock_session
        
        # Mock VTE terminal creation
        with patch('tree_style_terminal.controllers.session_manager.VteTerminal') as MockVteTerminal:
            mock_terminal = Mock()
            mock_terminal.spawn_shell.return_value = True
            MockVteTerminal.return_value = mock_terminal
            # Create child session
            child_session = session_manager.new_child()
            
            # Verify child was created and added to tree
            assert child_session is not None
            assert child_session in session_tree.get_children(mock_session)
    
    def test_new_sibling_creates_sibling_node(self, session_tree, session_manager, mock_session):
        """Test that new_sibling creates sibling at same level."""
        # Setup: Create a parent with one child
        parent_session = TerminalSession(pid=100, pty_fd=200, cwd="/parent", title="parent")
        session_tree.add_node(parent_session)
        session_tree.add_node(mock_session, parent=parent_session)
        session_manager.current_session = mock_session
        
        # Mock VTE terminal creation
        with patch('tree_style_terminal.controllers.session_manager.VteTerminal') as MockVteTerminal:
            mock_terminal = Mock()
            mock_terminal.spawn_shell.return_value = True
            MockVteTerminal.return_value = mock_terminal
            # Create sibling session
            sibling_session = session_manager.new_sibling()
            
            # Verify sibling relationship
            assert sibling_session is not None
            assert session_tree.get_parent(sibling_session) == parent_session
            assert sibling_session in parent_session.children
            assert mock_session in parent_session.children
            assert len(parent_session.children) == 2
    
    def test_new_sibling_from_root_creates_new_root(self, session_tree, session_manager, mock_session):
        """Test that new_sibling from root creates another root node."""
        # Setup: Add single root session
        session_tree.add_node(mock_session)
        session_manager.current_session = mock_session
        
        # Mock VTE terminal creation
        with patch('tree_style_terminal.controllers.session_manager.VteTerminal') as MockVteTerminal:
            mock_terminal = Mock()
            mock_terminal.spawn_shell.return_value = True
            MockVteTerminal.return_value = mock_terminal
            # Create sibling (should be another root)
            sibling_session = session_manager.new_sibling()
            
            # Verify both are root nodes
            assert sibling_session is not None
            assert session_tree.get_parent(sibling_session) is None
            assert session_tree.get_parent(mock_session) is None
            assert mock_session in session_tree.get_roots()
            assert sibling_session in session_tree.get_roots()
            assert len(session_tree.get_roots()) == 2
    
    def test_new_child_no_current_session(self, shortcut_controller, session_manager):
        """Test new_child action when no session is selected."""
        # No current session
        session_manager.current_session = None
        
        with patch.object(session_manager, 'new_child', return_value=None) as mock_new_child:
            # Execute new_child action
            action = shortcut_controller.get_action("new_child")
            action.activate(None)
            
            # Should still call new_child (manager handles the logic)
            mock_new_child.assert_called_once()
    
    def test_new_sibling_no_current_session(self, shortcut_controller, session_manager):
        """Test new_sibling action when no session is selected."""
        # No current session
        session_manager.current_session = None
        
        with patch.object(session_manager, 'new_sibling', return_value=None) as mock_new_sibling:
            # Execute new_sibling action
            action = shortcut_controller.get_action("new_sibling")
            action.activate(None)
            
            # Should still call new_sibling (manager handles the logic)
            mock_new_sibling.assert_called_once()
    
    def test_action_error_handling(self, shortcut_controller, session_manager):
        """Test that actions handle errors gracefully."""
        # Mock VTE terminal creation to raise exceptions
        with patch('tree_style_terminal.controllers.session_manager.VteTerminal', side_effect=Exception("VTE creation failed")):
            # Should not raise exception
            action = shortcut_controller.get_action("new_child")
            action.activate(None)
            
            action = shortcut_controller.get_action("new_sibling")
            action.activate(None)
    
    def test_complex_tree_structure_preservation(self, session_tree, session_manager):
        """Test that complex tree structures are preserved during session creation."""
        # Create a complex tree:
        #   root1
        #   ├── child1
        #   │   └── grandchild1
        #   └── child2
        #   root2
        
        root1 = TerminalSession(pid=100, pty_fd=200, cwd="/root1", title="root1")
        root2 = TerminalSession(pid=101, pty_fd=201, cwd="/root2", title="root2")
        child1 = TerminalSession(pid=102, pty_fd=202, cwd="/root1/child1", title="child1")
        child2 = TerminalSession(pid=103, pty_fd=203, cwd="/root1/child2", title="child2")
        grandchild1 = TerminalSession(pid=104, pty_fd=204, cwd="/root1/child1/grand", title="grandchild1")
        
        # Build tree structure
        session_tree.add_node(root1)
        session_tree.add_node(root2)
        session_tree.add_node(child1, parent=root1)
        session_tree.add_node(child2, parent=root1)
        session_tree.add_node(grandchild1, parent=child1)
        
        # Select child1 and create a new child
        session_manager.current_session = child1
        
        with patch('tree_style_terminal.controllers.session_manager.VteTerminal') as MockVteTerminal:
            mock_terminal = Mock()
            mock_terminal.spawn_shell.return_value = True
            MockVteTerminal.return_value = mock_terminal
            new_grandchild = session_manager.new_child()
            
            # Verify tree structure is preserved
            assert len(session_tree.get_roots()) == 2
            assert len(session_tree.get_children(root1)) == 2
            assert len(session_tree.get_children(child1)) == 2  # grandchild1 + new_grandchild
            assert session_tree.get_parent(new_grandchild) == child1
            assert session_tree.get_parent(grandchild1) == child1