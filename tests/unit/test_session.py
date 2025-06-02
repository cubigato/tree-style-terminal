"""
Unit tests for TerminalSession dataclass.

Tests basic instantiation, title auto-generation, hash/equality behavior,
and edge cases for cwd handling.
"""

import pytest
from tree_style_terminal.models.session import TerminalSession


class TestTerminalSession:
    """Test cases for TerminalSession dataclass."""

    def test_session_creation_with_title(self):
        """Test creating a session with an explicit title."""
        session = TerminalSession(
            pid=123,
            pty_fd=456,
            cwd="/home/user/projects",
            title="My Terminal"
        )
        
        assert session.pid == 123
        assert session.pty_fd == 456
        assert session.cwd == "/home/user/projects"
        assert session.title == "My Terminal"
        assert session.children == []

    def test_session_creation_without_title(self):
        """Test creating a session without title - should auto-generate from cwd."""
        session = TerminalSession(
            pid=123,
            pty_fd=456,
            cwd="/home/user/projects"
        )
        
        assert session.title == "user/projects"

    def test_session_title_auto_generation_root_dir(self):
        """Test title generation for root directory."""
        session = TerminalSession(
            pid=123,
            pty_fd=456,
            cwd="/"
        )
        
        assert session.title == "/"

    def test_session_title_auto_generation_empty_cwd(self):
        """Test title generation for empty cwd."""
        session = TerminalSession(
            pid=123,
            pty_fd=456,
            cwd=""
        )
        
        assert session.title == ""

    def test_session_hash_and_equality(self):
        """Test that sessions with same pid/pty_fd are equal and have same hash."""
        session1 = TerminalSession(pid=123, pty_fd=456, cwd="/path1")
        session2 = TerminalSession(pid=123, pty_fd=456, cwd="/path2")  # Different cwd
        session3 = TerminalSession(pid=124, pty_fd=456, cwd="/path1")  # Different pid
        
        # Same pid/pty_fd should be equal regardless of other fields
        assert session1 == session2
        assert hash(session1) == hash(session2)
        
        # Different pid should not be equal
        assert session1 != session3
        assert hash(session1) != hash(session3)

    def test_session_equality_with_non_session(self):
        """Test equality comparison with non-TerminalSession objects."""
        session = TerminalSession(pid=123, pty_fd=456, cwd="/home")
        
        assert session != "not a session"
        assert session != 123
        assert session != None

    def test_session_children_default_factory(self):
        """Test that each session gets its own children list."""
        session1 = TerminalSession(pid=123, pty_fd=456, cwd="/path1")
        session2 = TerminalSession(pid=124, pty_fd=457, cwd="/path2")
        
        # Modify one session's children
        dummy_child = TerminalSession(pid=999, pty_fd=999, cwd="/dummy")
        session1.children.append(dummy_child)
        
        # Other session should have empty children
        assert len(session1.children) == 1
        assert len(session2.children) == 0

    def test_session_cwd_edge_cases(self):
        """Test various edge cases for cwd and title generation."""
        # Trailing slash - gets normalized to show last two components
        session = TerminalSession(pid=123, pty_fd=456, cwd="/home/user/")
        assert session.title == "home/user"
        
        # No leading slash
        session = TerminalSession(pid=123, pty_fd=456, cwd="relative/path")
        assert session.title == "relative/path"
        
        # Single directory
        session = TerminalSession(pid=123, pty_fd=456, cwd="single")
        assert session.title == "single"