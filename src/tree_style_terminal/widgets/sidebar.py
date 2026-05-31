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
from gi.repository import Gtk, Gdk

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
        self._rename_callback: Optional[Callable[[TerminalSession, str], None]] = None
        self._clear_title_callback: Optional[Callable[[TerminalSession], None]] = None
        self._selecting_programmatically = False
        self._selection_started_by_pointer = False
        self._last_selection_was_pointer = False
        self._context_menu_session: Optional[TerminalSession] = None

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
        self.tree_view.connect("button-press-event", self._on_button_press_event)

        # Create scrolled window
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.tree_view)

        # Pack into the box
        self.pack_start(self.scrolled_window, True, True, 0)

        # Add CSS classes for styling and remove view class for transparency
        ctx = self.get_style_context()
        ctx.add_class("sidebar-tree")
        ctx.remove_class("view")  # critical for transparency

        # Add specific CSS class to TreeView and remove view class (most important)
        tree_ctx = self.tree_view.get_style_context()
        tree_ctx.add_class("transparent-tree")  # specific class for TreeView transparency
        tree_ctx.remove_class("view")  # critical for TreeView transparency

        # Add CSS class to scrolled window for better targeting
        scrolled_ctx = self.scrolled_window.get_style_context()
        scrolled_ctx.add_class("transparent-scroll")
        scrolled_ctx.remove_class("view")  # remove if present

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
        if self._selecting_programmatically:
            return

        if tree_iter is not None:
            session = self.controller.get_session_from_iter(tree_iter)
            if session and self._selection_callback:
                logger.debug(f"Session selected: {session.title}")
                self._last_selection_was_pointer = self._selection_started_by_pointer
                try:
                    self._selection_callback(session)
                finally:
                    self._selection_started_by_pointer = False

    def _on_button_press_event(self, tree_view: Gtk.TreeView, _event: Gdk.EventButton) -> bool:
        """Track pointer selections and show the session menu on right click."""
        self._selection_started_by_pointer = True
        if _event is not None and _event.button == Gdk.BUTTON_SECONDARY:
            session = self._get_session_at_event(tree_view, _event)
            if session is not None:
                self._context_menu_session = session
                self._popup_context_menu(_event)
                return True
        return False

    def _get_session_at_event(
        self,
        tree_view: Gtk.TreeView,
        event: Gdk.EventButton,
    ) -> Optional[TerminalSession]:
        """Return the session under a pointer event."""
        path_info = tree_view.get_path_at_pos(int(event.x), int(event.y))
        if path_info is None:
            return None

        path = path_info[0]
        tree_view.get_selection().select_path(path)
        tree_iter = self.controller.get_tree_store().get_iter(path)
        return self.controller.get_session_from_iter(tree_iter)

    def _popup_context_menu(self, event: Gdk.EventButton) -> None:
        """Display the per-session context menu."""
        session = self._context_menu_session
        if session is None:
            return

        menu = Gtk.Menu()

        rename_item = Gtk.MenuItem(label="Rename")
        rename_item.connect("activate", self._on_rename_menu_activate)
        menu.append(rename_item)

        clear_item = Gtk.MenuItem(label="Use Automatic Title")
        clear_item.set_sensitive(session.custom_title is not None)
        clear_item.connect("activate", self._on_clear_title_menu_activate)
        menu.append(clear_item)

        menu.show_all()
        if hasattr(menu, "popup_at_pointer"):
            menu.popup_at_pointer(event)
        else:
            menu.popup(
                None,
                None,
                None,
                None,
                event.button,
                event.time,
            )

    def _on_rename_menu_activate(self, _menu_item: Gtk.MenuItem) -> None:
        """Open a small dialog for renaming the selected session."""
        session = self._context_menu_session
        if session is None:
            return

        dialog = Gtk.Dialog(title="Rename Session", transient_for=self.get_toplevel(), modal=True)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Rename", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)

        entry = Gtk.Entry()
        entry.set_text(session.custom_title or session.title or "")
        entry.set_activates_default(True)
        entry.set_margin_top(12)
        entry.set_margin_bottom(12)
        entry.set_margin_start(12)
        entry.set_margin_end(12)

        dialog.get_content_area().pack_start(entry, False, False, 0)
        dialog.show_all()
        response = dialog.run()
        title = entry.get_text()
        dialog.destroy()

        if response == Gtk.ResponseType.OK and self._rename_callback:
            self._rename_callback(session, title)

    def _on_clear_title_menu_activate(self, _menu_item: Gtk.MenuItem) -> None:
        """Clear the custom title for the selected session."""
        session = self._context_menu_session
        if session is not None and self._clear_title_callback:
            self._clear_title_callback(session)

    def last_selection_was_pointer(self) -> bool:
        """Return whether the most recent user selection started with a pointer event."""
        return self._last_selection_was_pointer

    def set_selection_callback(self, callback: Callable[[TerminalSession], None]) -> None:
        """
        Set the callback function to be called when a session is selected.

        Args:
            callback: Function to call with the selected TerminalSession
        """
        self._selection_callback = callback

    def set_rename_callback(self, callback: Callable[[TerminalSession, str], None]) -> None:
        """Set the callback for session rename requests."""
        self._rename_callback = callback

    def set_clear_title_callback(self, callback: Callable[[TerminalSession], None]) -> None:
        """Set the callback for clearing custom session titles."""
        self._clear_title_callback = callback

    def select_session(self, session: TerminalSession) -> None:
        """
        Programmatically select a session in the tree view.

        Args:
            session: The session to select
        """
        tree_iter = self.controller.find_iter_for_session(session)
        if tree_iter is None:
            return

        selection = self.tree_view.get_selection()
        path = self.controller.get_tree_store().get_path(tree_iter)

        self._selecting_programmatically = True
        try:
            self.tree_view.expand_to_path(path)
            selection.unselect_all()
            selection.select_path(path)
            self.tree_view.scroll_to_cell(path, None, False, 0.0, 0.0)
        finally:
            self._selecting_programmatically = False

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
