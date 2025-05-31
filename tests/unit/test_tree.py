"""
Unit tests for SessionTree class.

Tests node addition, the adoption algorithm, basic queries, and edge cases.
Focus on the complex adoption behavior when nodes are removed.
"""

import pytest
from tree_style_terminal.models.session import TerminalSession
from tree_style_terminal.models.tree import SessionTree


class TestSessionTree:
    """Test cases for SessionTree class."""

    def test_add_root_node(self):
        """Test adding a session as a root node."""
        tree = SessionTree()
        session = TerminalSession(pid=123, pty_fd=456, cwd="/home")
        
        tree.add_node(session)
        
        assert len(tree.get_roots()) == 1
        assert tree.get_roots()[0] == session
        assert tree.get_parent(session) is None
        assert not tree.is_empty()

    def test_add_child_node(self):
        """Test adding a session as a child of another session."""
        tree = SessionTree()
        parent = TerminalSession(pid=123, pty_fd=456, cwd="/home")
        child = TerminalSession(pid=124, pty_fd=457, cwd="/home/child")
        
        tree.add_node(parent)
        tree.add_node(child, parent)
        
        assert len(tree.get_roots()) == 1
        assert tree.get_parent(child) == parent
        assert child in parent.children
        assert child in tree.get_children(parent)

    def test_remove_leaf_node(self):
        """Test removing a leaf node (no children) has no side effects."""
        tree = SessionTree()
        parent = TerminalSession(pid=123, pty_fd=456, cwd="/home")
        child = TerminalSession(pid=124, pty_fd=457, cwd="/home/child")
        
        tree.add_node(parent)
        tree.add_node(child, parent)
        
        # Remove the leaf
        tree.remove_node(child)
        
        assert len(tree.get_roots()) == 1
        assert tree.get_roots()[0] == parent
        assert child not in parent.children
        assert child not in tree.get_all_sessions()
        assert len(tree.get_all_sessions()) == 1

    def test_remove_root_with_children(self):
        """Test adoption: removing root with children makes children new roots."""
        tree = SessionTree()
        root = TerminalSession(pid=123, pty_fd=456, cwd="/root")
        child1 = TerminalSession(pid=124, pty_fd=457, cwd="/root/child1")
        child2 = TerminalSession(pid=125, pty_fd=458, cwd="/root/child2")
        
        tree.add_node(root)
        tree.add_node(child1, root)
        tree.add_node(child2, root)
        
        # Remove root - children should become new roots
        tree.remove_node(root)
        
        roots = tree.get_roots()
        assert len(roots) == 2
        assert child1 in roots
        assert child2 in roots
        assert tree.get_parent(child1) is None
        assert tree.get_parent(child2) is None
        assert root not in tree.get_all_sessions()

    def test_remove_middle_node_with_children(self):
        """Test adoption: removing middle node with children adopts children to parent."""
        tree = SessionTree()
        root = TerminalSession(pid=123, pty_fd=456, cwd="/root")
        middle = TerminalSession(pid=124, pty_fd=457, cwd="/root/middle")
        grandchild1 = TerminalSession(pid=125, pty_fd=458, cwd="/root/middle/gc1")
        grandchild2 = TerminalSession(pid=126, pty_fd=459, cwd="/root/middle/gc2")
        
        tree.add_node(root)
        tree.add_node(middle, root)
        tree.add_node(grandchild1, middle)
        tree.add_node(grandchild2, middle)
        
        # Remove middle - grandchildren should be adopted by root
        tree.remove_node(middle)
        
        assert len(tree.get_roots()) == 1
        assert tree.get_roots()[0] == root
        assert tree.get_parent(grandchild1) == root
        assert tree.get_parent(grandchild2) == root
        assert grandchild1 in root.children
        assert grandchild2 in root.children
        assert middle not in root.children
        assert middle not in tree.get_all_sessions()

    def test_complex_adoption_scenario(self):
        """Test complex scenario with deep nesting and adoption."""
        tree = SessionTree()
        root = TerminalSession(pid=1, pty_fd=10, cwd="/root")
        child1 = TerminalSession(pid=2, pty_fd=20, cwd="/root/child1")
        child2 = TerminalSession(pid=3, pty_fd=30, cwd="/root/child2")
        grandchild = TerminalSession(pid=4, pty_fd=40, cwd="/root/child1/gc")
        great_grandchild = TerminalSession(pid=5, pty_fd=50, cwd="/root/child1/gc/ggc")
        
        tree.add_node(root)
        tree.add_node(child1, root)
        tree.add_node(child2, root)
        tree.add_node(grandchild, child1)
        tree.add_node(great_grandchild, grandchild)
        
        # Remove grandchild - great_grandchild should be adopted by child1
        tree.remove_node(grandchild)
        
        assert tree.get_parent(great_grandchild) == child1
        assert great_grandchild in child1.children
        assert len(child1.children) == 1  # only great_grandchild now
        assert grandchild not in tree.get_all_sessions()

    def test_basic_queries(self):
        """Test basic query methods."""
        tree = SessionTree()
        assert tree.is_empty()
        assert len(tree.get_roots()) == 0
        assert len(tree.get_all_sessions()) == 0
        
        session = TerminalSession(pid=123, pty_fd=456, cwd="/home")
        tree.add_node(session)
        
        assert not tree.is_empty()
        assert len(tree.get_all_sessions()) == 1
        assert session in tree.get_all_sessions()

    def test_find_session_by_pid(self):
        """Test finding sessions by process ID."""
        tree = SessionTree()
        session1 = TerminalSession(pid=123, pty_fd=456, cwd="/home")
        session2 = TerminalSession(pid=124, pty_fd=457, cwd="/home2")
        
        tree.add_node(session1)
        tree.add_node(session2)
        
        found = tree.find_session_by_pid(123)
        assert found == session1
        
        found = tree.find_session_by_pid(124)
        assert found == session2
        
        found = tree.find_session_by_pid(999)
        assert found is None

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        tree = SessionTree()
        session = TerminalSession(pid=123, pty_fd=456, cwd="/home")
        
        # Remove non-existent session should not crash
        tree.remove_node(session)
        assert tree.is_empty()
        
        # Get parent of non-existent session
        assert tree.get_parent(session) is None
        
        # Get children of session returns copy
        tree.add_node(session)
        children = tree.get_children(session)
        children.append(TerminalSession(pid=999, pty_fd=999, cwd="/dummy"))
        assert len(session.children) == 0  # Original not modified

    def test_get_methods_return_copies(self):
        """Test that get methods return copies to prevent external modification."""
        tree = SessionTree()
        session1 = TerminalSession(pid=123, pty_fd=456, cwd="/home")
        session2 = TerminalSession(pid=124, pty_fd=457, cwd="/home2")
        
        tree.add_node(session1)
        tree.add_node(session2, session1)
        
        # Modify returned lists should not affect tree
        roots = tree.get_roots()
        roots.clear()
        assert len(tree.get_roots()) == 1
        
        children = tree.get_children(session1)
        children.clear()
        assert len(session1.children) == 1