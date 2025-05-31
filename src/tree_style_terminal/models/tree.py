"""
Domain model for managing the tree structure of terminal sessions.

The SessionTree maintains the hierarchical relationships between terminal sessions
and implements the adoption algorithm when sessions are removed.
"""

from __future__ import annotations

from typing import List, Optional, Set
from .session import TerminalSession


class SessionTree:
    """
    Manages the tree structure of terminal sessions.
    
    Handles parent-child relationships and implements adoption when nodes are removed.
    When a session with children is removed, its children are adopted by the parent,
    or become new root nodes if the removed session was a root.
    """
    
    def __init__(self) -> None:
        """Initialize an empty session tree."""
        self.root_nodes: List[TerminalSession] = []
        self._parent_map: dict[TerminalSession, Optional[TerminalSession]] = {}
    
    def add_node(self, session: TerminalSession, parent: Optional[TerminalSession] = None) -> None:
        """
        Add a session to the tree.
        
        Args:
            session: The session to add
            parent: Parent session, or None to add as root
        """
        if parent is None:
            # Add as root node
            self.root_nodes.append(session)
            self._parent_map[session] = None
        else:
            # Add as child of parent
            if session not in parent.children:
                parent.children.append(session)
            self._parent_map[session] = parent
    
    def remove_node(self, session: TerminalSession) -> None:
        """
        Remove a session from the tree, implementing adoption algorithm.
        
        When a session is removed:
        - Its children are adopted by its parent (or become roots if no parent)
        - The session is removed from its parent's children list
        - All internal references are cleaned up
        
        Args:
            session: The session to remove
        """
        if session not in self._parent_map:
            return  # Session not in tree
        
        parent = self._parent_map[session]
        children = session.children.copy()  # Copy to avoid modification during iteration
        
        # Implement adoption: children are adopted by the parent
        for child in children:
            if parent is None:
                # Session was a root, so children become new roots
                self.root_nodes.append(child)
                self._parent_map[child] = None
            else:
                # Children are adopted by the grandparent
                parent.children.append(child)
                self._parent_map[child] = parent
        
        # Remove session from its parent's children list
        if parent is None:
            # Remove from roots
            if session in self.root_nodes:
                self.root_nodes.remove(session)
        else:
            # Remove from parent's children
            if session in parent.children:
                parent.children.remove(session)
        
        # Clear the session's children list and remove from parent map
        session.children.clear()
        del self._parent_map[session]
    
    def get_parent(self, session: TerminalSession) -> Optional[TerminalSession]:
        """Get the parent of a session, or None if it's a root."""
        return self._parent_map.get(session)
    
    def get_children(self, session: TerminalSession) -> List[TerminalSession]:
        """Get the direct children of a session."""
        return session.children.copy()
    
    def get_roots(self) -> List[TerminalSession]:
        """Get all root sessions."""
        return self.root_nodes.copy()
    
    def is_empty(self) -> bool:
        """Check if the tree has no sessions."""
        return len(self.root_nodes) == 0
    
    def get_all_sessions(self) -> Set[TerminalSession]:
        """Get all sessions in the tree."""
        return set(self._parent_map.keys())
    
    def find_session_by_pid(self, pid: int) -> Optional[TerminalSession]:
        """Find a session by its process ID."""
        for session in self._parent_map:
            if session.pid == pid:
                return session
        return None