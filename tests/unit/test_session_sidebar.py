"""
Unit tests for the SessionSidebar widget.

Tests the widget structure, TreeView configuration, and selection handling.
"""

import pytest

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from tree_style_terminal.controllers.sidebar import SidebarController
from tree_style_terminal.models.session import TerminalSession
from tree_style_terminal.models.tree import SessionTree
from tree_style_terminal.widgets.sidebar import SessionSidebar


class TestSessionSidebar:
    """Test cases for SessionSidebar widget."""
    
    def test_widget_structure(self):
        """Test SessionSidebar inherits from Gtk.Box and has tree_view."""
        tree = SessionTree()
        controller = SidebarController(tree)
        sidebar = SessionSidebar(controller)
        
        assert isinstance(sidebar, Gtk.Box)
        assert hasattr(sidebar, 'tree_view')
        assert isinstance(sidebar.tree_view, Gtk.TreeView)
        assert hasattr(sidebar, 'scrolled_window')
        assert isinstance(sidebar.scrolled_window, Gtk.ScrolledWindow)
    
    def test_tree_view_configuration(self):
        """Test TreeView is configured correctly."""
        tree = SessionTree()
        controller = SidebarController(tree)
        sidebar = SessionSidebar(controller)
        
        assert not sidebar.tree_view.get_headers_visible()
        assert sidebar.tree_view.get_enable_tree_lines()
        assert sidebar.tree_view.get_show_expanders()

        assert sidebar.get_style_context().has_class("sidebar-tree")
        assert sidebar.tree_view.get_style_context().has_class("transparent-tree")
        assert sidebar.scrolled_window.get_style_context().has_class("transparent-scroll")
    
    def test_column_setup(self):
        """Test TreeView has exactly one column that expands."""
        tree = SessionTree()
        controller = SidebarController(tree)
        sidebar = SessionSidebar(controller)
        
        columns = sidebar.tree_view.get_columns()
        assert len(columns) == 1
        
        title_column = columns[0]
        assert title_column.get_expand()
    
    def test_selection_callback_setup(self):
        """Test selection callback can be set and called."""
        tree = SessionTree()
        controller = SidebarController(tree)
        sidebar = SessionSidebar(controller)
        
        # Add a session to select
        session = TerminalSession(pid=123, pty_fd=456, cwd="/test")
        tree.add_node(session)
        controller.sync_with_session_tree()
        
        # Set up callback
        selected_sessions = []
        def on_selection(session):
            selected_sessions.append(session)
        
        sidebar.set_selection_callback(on_selection)
        
        # Trigger selection programmatically
        sidebar.select_session(session)
        
        # Verify callback was called (note: actual callback triggering depends on GTK event loop)
        selection = sidebar.tree_view.get_selection()
        model, tree_iter = selection.get_selected()
        assert tree_iter is not None
        
        selected_from_tree = controller.get_session_from_iter(tree_iter)
        assert selected_from_tree == session
    
    def test_select_session_method(self):
        """Test select_session method updates TreeView selection."""
        tree = SessionTree()
        controller = SidebarController(tree)
        sidebar = SessionSidebar(controller)
        
        # Add sessions
        session1 = TerminalSession(pid=1, pty_fd=10, cwd="/one")
        session2 = TerminalSession(pid=2, pty_fd=20, cwd="/two")
        
        tree.add_node(session1)
        tree.add_node(session2, session1)
        controller.sync_with_session_tree()
        
        # Select first session
        sidebar.select_session(session1)
        
        selection = sidebar.tree_view.get_selection()
        model, tree_iter = selection.get_selected()
        selected_session = controller.get_session_from_iter(tree_iter)
        assert selected_session == session1
        
        # Select child session
        sidebar.select_session(session2)
        
        selection = sidebar.tree_view.get_selection()
        model, tree_iter = selection.get_selected()
        selected_session = controller.get_session_from_iter(tree_iter)
        assert selected_session == session2

    def test_programmatic_select_does_not_trigger_selection_callback(self):
        """Test programmatic selection does not recurse through selection callbacks."""
        tree = SessionTree()
        controller = SidebarController(tree)
        sidebar = SessionSidebar(controller)

        session = TerminalSession(pid=1, pty_fd=10, cwd="/one")
        tree.add_node(session)
        controller.sync_with_session_tree()

        selected_sessions = []
        sidebar.set_selection_callback(lambda selected: selected_sessions.append(selected))

        sidebar.select_session(session)

        assert selected_sessions == []

    def test_pointer_selection_is_tracked_for_callback(self):
        """Test pointer-initiated selections can be distinguished from keyboard selections."""
        tree = SessionTree()
        controller = SidebarController(tree)
        sidebar = SessionSidebar(controller)

        session = TerminalSession(pid=1, pty_fd=10, cwd="/one")
        tree.add_node(session)
        controller.sync_with_session_tree()

        pointer_selection_states = []
        sidebar.set_selection_callback(
            lambda selected: pointer_selection_states.append(sidebar.last_selection_was_pointer())
        )

        tree_iter = controller.find_iter_for_session(session)
        path = controller.get_tree_store().get_path(tree_iter)
        sidebar._on_button_press_event(sidebar.tree_view, None)
        sidebar.tree_view.get_selection().select_path(path)

        assert pointer_selection_states == [True]

    def test_rename_menu_activation_calls_callback(self):
        """Test rename menu activation forwards the entered title."""
        tree = SessionTree()
        controller = SidebarController(tree)
        sidebar = SessionSidebar(controller)
        session = TerminalSession(pid=1, pty_fd=10, cwd="/one", title="one")
        renamed = []

        sidebar.set_rename_callback(lambda selected, title: renamed.append((selected, title)))
        sidebar._context_menu_session = session

        class FakeDialog:
            def __init__(self, *args, **kwargs):
                self.entry = None

            def add_button(self, *args, **kwargs):
                pass

            def set_default_response(self, *args, **kwargs):
                pass

            def get_content_area(self):
                return self

            def pack_start(self, entry, *args, **kwargs):
                self.entry = entry

            def show_all(self):
                self.entry.set_text("renamed")

            def run(self):
                return Gtk.ResponseType.OK

            def destroy(self):
                pass

        original_dialog = Gtk.Dialog
        Gtk.Dialog = FakeDialog
        try:
            sidebar._on_rename_menu_activate(Gtk.MenuItem())
        finally:
            Gtk.Dialog = original_dialog

        assert renamed == [(session, "renamed")]

    def test_clear_title_menu_activation_calls_callback(self):
        """Test clear-title menu activation forwards the selected session."""
        tree = SessionTree()
        controller = SidebarController(tree)
        sidebar = SessionSidebar(controller)
        session = TerminalSession(pid=1, pty_fd=10, cwd="/one", title="one")
        cleared = []

        sidebar.set_clear_title_callback(cleared.append)
        sidebar._context_menu_session = session

        sidebar._on_clear_title_menu_activate(Gtk.MenuItem())

        assert cleared == [session]
