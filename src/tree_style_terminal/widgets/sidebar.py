"""
Sidebar widget for displaying the session tree navigator.

Contains the SessionSidebar widget which wraps a Gtk.TreeView
for displaying the hierarchical session structure.
"""

from __future__ import annotations

import logging
from typing import Optional, Callable

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ..models.session import TerminalSession
from ..controllers.sidebar import SidebarController

logger = logging.getLogger(__name__)


class SessionSidebar(Gtk.Box):
    """
    Sidebar widget containing a TreeView for session navigation.
    
    This widget wraps a Gtk.TreeView and provides methods for handling
    session selection and displaying the session tree structure.
    """
    
    def __init__(self, sidebar_controller: SidebarController) -> None:
        """
        Initialize the sidebar widget.
        
        Args:
            sidebar_controller: The controller managing the TreeStore
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        self.controller = sidebar_controller
        self._selection_callback: Optional[Callable[[TerminalSession], None]] = None
        
        # Create the tree view
        self.tree_view = Gtk.TreeView()
        self.tree_view.set_model(self.controller.get_tree_store())
        self.tree_view.set_headers_visible(False)
        self.tree_view.set_enable_tree_lines(True)
        self.tree_view.set_show_expanders(True)
        self.tree_view.set_level_indentation(16)
        
        # Set up the title column
        self._setup_columns()
        
        # Connect selection signal
        selection = self.tree_view.get_selection()
        selection.set_mode(Gtk.SelectionMode.SINGLE)
        selection.connect("changed", self._on_selection_changed)
        
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.tree_view)
        
        # Pack into the box
        self.pack_start(scrolled, True, True, 0)
        
        # Add CSS class for styling
        self.get_style_context().add_class("sidebar-tree")
        
        logger.debug("SessionSidebar initialized")
    
    def _setup_columns(self) -> None:
        """Set up the TreeView columns for displaying session titles."""
        # Create text renderer
        renderer = Gtk.CellRendererText()
        renderer.set_property("ellipsize", 3)  # PANGO_ELLIPSIZE_END
        
        # Create column for title
        column = Gtk.TreeViewColumn("Title", renderer)
        column.add_attribute(renderer, "text", self.controller.COL_TITLE)
        column.set_expand(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        
        # Add column to tree view
        self.tree_view.append_column(column)
    
    def _on_selection_changed(self, selection: Gtk.TreeSelection) -> None:
        """
        Handle tree view selection changes.
        
        Args:
            selection: The TreeSelection object
        """
        model, tree_iter = selection.get_selected()
        if tree_iter is not None:
            session = self.controller.get_session_from_iter(tree_iter)
            if session and self._selection_callback:
                logger.debug(f"Session selected: {session.title}")
                self._selection_callback(session)
    
    def set_selection_callback(self, callback: Callable[[TerminalSession], None]) -> None:
        """
        Set the callback function to be called when a session is selected.
        
        Args:
            callback: Function to call with the selected TerminalSession
        """
        self._selection_callback = callback
    
    def select_session(self, session: TerminalSession) -> None:
        """
        Programmatically select a session in the tree view.
        
        Args:
            session: The session to select
        """
        tree_iter = self.controller.find_iter_for_session(session)
        if tree_iter:
            selection = self.tree_view.get_selection()
            selection.select_iter(tree_iter)
            
            # Expand parent nodes and scroll to the selection
            path = self.controller.get_tree_store().get_path(tree_iter)
            self.tree_view.expand_to_path(path)
            self.tree_view.scroll_to_cell(path, None, False, 0.0, 0.0)
            
            logger.debug(f"Selected session: {session.title}")
    
    def expand_all(self) -> None:
        """Expand all nodes in the tree view."""
        self.tree_view.expand_all()
    
    def collapse_all(self) -> None:
        """Collapse all nodes in the tree view."""
        self.tree_view.collapse_all()
    
    def refresh(self) -> None:
        """Refresh the tree view by syncing with the controller."""
        self.controller.sync_with_session_tree()