"""
Controller for the sidebar tree navigator.

Manages the Gtk.TreeStore that displays the session tree structure and handles
synchronization between the SessionTree domain model and the GTK tree view.
"""

from __future__ import annotations

import logging
from typing import Optional

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

from ..models.session import TerminalSession
from ..models.tree import SessionTree

logger = logging.getLogger(__name__)


class SidebarController:
    """
    Controller for managing the sidebar tree view and its underlying TreeStore.
    
    This class maintains a Gtk.TreeStore with columns for the session object
    and title, and provides methods to synchronize with a SessionTree model.
    """
    
    # TreeStore column indices
    COL_OBJECT = 0
    COL_TITLE = 1
    
    def __init__(self, session_tree: SessionTree) -> None:
        """
        Initialize the sidebar controller.
        
        Args:
            session_tree: The SessionTree model to synchronize with
        """
        self.session_tree = session_tree
        
        # Create TreeStore with columns: [object, title]
        # COL_OBJECT: stores the TerminalSession object
        # COL_TITLE: stores the display title as string
        self.tree_store = Gtk.TreeStore(GObject.TYPE_PYOBJECT, str)
        
        # Map sessions to their TreeIter for efficient updates
        self._session_to_iter: dict[TerminalSession, Gtk.TreeIter] = {}
        
        # Initialize the tree store from current session tree state
        self._populate_from_session_tree()
        
        # Event binding: Currently implemented through manual sync via refresh() calls
        # The SessionSidebar widget calls controller.sync_with_session_tree() when needed
        # This approach works effectively for the current use case and avoids complexity
        # of adding signal emission to SessionTree
        
        logger.debug("SidebarController initialized")
    
    def _populate_from_session_tree(self) -> None:
        """Populate the TreeStore from the current SessionTree state."""
        self.tree_store.clear()
        self._session_to_iter.clear()
        
        # Add all root nodes and their children recursively
        for root_session in self.session_tree.get_roots():
            self._add_session_recursive(root_session, None)
    
    def _add_session_recursive(self, session: TerminalSession, parent_iter: Optional[Gtk.TreeIter]) -> Gtk.TreeIter:
        """
        Add a session and all its children to the TreeStore recursively.
        
        Args:
            session: The session to add
            parent_iter: Parent TreeIter, or None for root level
            
        Returns:
            The TreeIter for the added session
        """
        # Add the session to the tree store
        tree_iter = self.tree_store.append(parent_iter, [session, session.title])
        
        # Track the mapping
        self._session_to_iter[session] = tree_iter
        
        # Add all children recursively
        for child in session.children:
            self._add_session_recursive(child, tree_iter)
        
        return tree_iter
    
    def add_session(self, session: TerminalSession, parent: Optional[TerminalSession] = None) -> None:
        """
        Add a session to the TreeStore.
        
        Args:
            session: The session to add
            parent: Parent session, or None for root level
        """
        # Find parent TreeIter if parent is specified
        parent_iter = None
        if parent is not None:
            parent_iter = self._session_to_iter.get(parent)
            if parent_iter is None:
                logger.warning(f"Parent session not found in TreeStore: {parent}")
                return
        
        # Add the session
        tree_iter = self.tree_store.append(parent_iter, [session, session.title])
        self._session_to_iter[session] = tree_iter
        
        logger.debug(f"Added session to TreeStore: {session.title}")
    
    def remove_session(self, session: TerminalSession) -> None:
        """
        Remove a session from the TreeStore.
        
        Args:
            session: The session to remove
        """
        tree_iter = self._session_to_iter.get(session)
        if tree_iter is None:
            logger.warning(f"Session not found in TreeStore: {session}")
            return
        
        # Remove from TreeStore (this also removes all children)
        self.tree_store.remove(tree_iter)
        
        # Clean up mapping ONLY for this session (children will be moved separately)
        if session in self._session_to_iter:
            del self._session_to_iter[session]
        
        logger.debug(f"Removed session from TreeStore: {session.title}")
    
    def _cleanup_session_mapping(self, session: TerminalSession) -> None:
        """
        Recursively clean up the session-to-iter mapping for a session and its children.
        
        Args:
            session: The session to clean up
        """
        # Remove the session itself
        if session in self._session_to_iter:
            del self._session_to_iter[session]
        
        # Recursively clean up children
        for child in session.children:
            self._cleanup_session_mapping(child)
    
    def move_session(self, session: TerminalSession, new_parent: Optional[TerminalSession] = None) -> None:
        """
        Move a session to a new parent in the TreeStore.
        
        Args:
            session: The session to move
            new_parent: The new parent session, or None for root level
        """
        # Get current tree iterator
        current_iter = self._session_to_iter.get(session)
        if current_iter is None:
            logger.warning(f"Session not found in TreeStore for move: {session}")
            return
        
        # Get new parent iterator
        if new_parent is None:
            parent_iter = None
        else:
            parent_iter = self._session_to_iter.get(new_parent)
            if parent_iter is None:
                logger.warning(f"New parent session not found in TreeStore: {new_parent}")
                return
        
        # Create new tree iterator at new location
        new_iter = self.tree_store.append(parent_iter, [session, session.title])
        
        # Update mapping
        self._session_to_iter[session] = new_iter
        
        # Remove old iterator (but not children - they should be moved separately)
        self.tree_store.remove(current_iter)
        
        logger.debug(f"Moved session in TreeStore: {session.title}")

    def _extract_children_data(self, parent_iter: Gtk.TreeIter) -> list[tuple[TerminalSession, str]]:
        """
        Extract children data from TreeStore before parent removal.
        
        Args:
            parent_iter: TreeIter of the parent whose children to extract
            
        Returns:
            List of tuples containing (session, title) for each child
        """
        children_data = []
        
        # Get first child
        child_iter = self.tree_store.iter_children(parent_iter)
        
        while child_iter is not None:
            # Extract session object and title from the current child
            session = self.tree_store.get_value(child_iter, self.COL_OBJECT)
            title = self.tree_store.get_value(child_iter, self.COL_TITLE)
            children_data.append((session, title))
            
            # Move to next sibling
            child_iter = self.tree_store.iter_next(child_iter)
        
        return children_data

    def _restore_children_data(self, children_data: list[tuple[TerminalSession, str]], new_parent_iter: Optional[Gtk.TreeIter]) -> None:
        """
        Restore children data to TreeStore at new parent location.
        
        Args:
            children_data: List of (session, title) tuples to restore
            new_parent_iter: TreeIter of new parent, or None for root level
        """
        for session, title in children_data:
            # Add child at new location
            new_iter = self.tree_store.append(new_parent_iter, [session, title])
            
            # Update mapping
            self._session_to_iter[session] = new_iter
            
            logger.debug(f"Restored child session in TreeStore: {title}")

    def remove_session_with_adoption(self, session: TerminalSession, adopted_children: list[TerminalSession], new_parent: Optional[TerminalSession] = None) -> None:
        """
        Remove a session and handle adoption of its children.
        
        Args:
            session: The session to remove
            adopted_children: Children that need to be moved to new parent
            new_parent: The new parent session, or None for root level
        """
        tree_iter = self._session_to_iter.get(session)
        if tree_iter is None:
            logger.warning(f"Session not found in TreeStore: {session}")
            return
        
        # Extract children data before removal
        children_data = []
        for child_session in adopted_children:
            child_iter = self._session_to_iter.get(child_session)
            if child_iter is not None:
                title = self.tree_store.get_value(child_iter, self.COL_TITLE)
                children_data.append((child_session, title))
        
        # Remove from TreeStore (this removes all children too)
        self.tree_store.remove(tree_iter)
        
        # Clean up mapping for the removed session
        if session in self._session_to_iter:
            del self._session_to_iter[session]
        
        # Get new parent iterator
        if new_parent is None:
            new_parent_iter = None
        else:
            new_parent_iter = self._session_to_iter.get(new_parent)
            if new_parent_iter is None:
                logger.warning(f"New parent session not found in TreeStore: {new_parent}")
                new_parent_iter = None  # Fallback to root level
        
        # Restore children at new location
        self._restore_children_data(children_data, new_parent_iter)
        
        logger.debug(f"Removed session with adoption: {session.title}")

    def update_session_title(self, session: TerminalSession, new_title: str) -> None:
        """
        Update the title of a session in the TreeStore.
        
        Args:
            session: The session to update
            new_title: The new title
        """
        tree_iter = self._session_to_iter.get(session)
        if tree_iter is None:
            logger.warning(f"Session not found in TreeStore: {session}")
            return
        
        # Update the title in the session object and TreeStore
        session.title = new_title
        self.tree_store.set_value(tree_iter, self.COL_TITLE, new_title)
        
        logger.debug(f"Updated session title: {new_title}")
    
    def update_session(self, session: TerminalSession) -> None:
        """
        Update a session's display in the TreeStore (title and other properties).
        
        Args:
            session: The session to update
        """
        tree_iter = self._session_to_iter.get(session)
        if tree_iter is None:
            logger.warning(f"Session not found in TreeStore: {session}")
            return
        
        # Update the title in the TreeStore
        self.tree_store.set_value(tree_iter, self.COL_TITLE, session.title)
        
        logger.debug(f"Updated session: {session.title}")
    
    def get_tree_store(self) -> Gtk.TreeStore:
        """Get the underlying TreeStore."""
        return self.tree_store
    
    def get_session_from_iter(self, tree_iter: Gtk.TreeIter) -> Optional[TerminalSession]:
        """
        Get the TerminalSession object from a TreeIter.
        
        Args:
            tree_iter: The TreeIter to look up
            
        Returns:
            The TerminalSession object, or None if not found
        """
        try:
            return self.tree_store.get_value(tree_iter, self.COL_OBJECT)
        except Exception as e:
            logger.warning(f"Failed to get session from TreeIter: {e}")
            return None
    
    def find_iter_for_session(self, session: TerminalSession) -> Optional[Gtk.TreeIter]:
        """
        Find the TreeIter for a given session.
        
        Args:
            session: The session to find
            
        Returns:
            The TreeIter, or None if not found
        """
        return self._session_to_iter.get(session)
    
    def sync_with_session_tree(self) -> None:
        """
        Synchronize the TreeStore with the current state of the SessionTree.
        
        This is a full rebuild and should be used sparingly, typically only
        during initialization or after major structural changes.
        """
        logger.debug("Synchronizing TreeStore with SessionTree")
        self._populate_from_session_tree()
    
    def bind_session_tree_events(self) -> None:
        """
        Bind SessionTree events to TreeStore updates.
        
        NOTE: Event binding is currently implemented through the SessionManager and
        MainWindow integration, which calls refresh() on the SessionSidebar widget
        when sessions are created, closed, or selected. This approach provides the
        necessary synchronization without requiring complex signal emission in SessionTree.
        
        The current implementation is sufficient for Milestone 4 requirements and
        provides a clean separation of concerns between the domain model and UI.
        """
        logger.debug("Event binding handled through SessionManager callbacks and widget refresh")
        pass