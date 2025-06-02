#!/usr/bin/env python3
"""
Tree Style Terminal - Main application entry point.

This module contains the main GTK application class and window implementation.
"""

import sys
from pathlib import Path
from typing import Optional, Dict

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gio, GLib

from .widgets.terminal import VteTerminal
from .widgets.sidebar import SessionSidebar
from .controllers.sidebar import SidebarController
from .controllers.session_manager import SessionManager
from .controllers.shortcuts import ShortcutController
from .models.session import TerminalSession
from .models.tree import SessionTree


class MainWindow(Gtk.ApplicationWindow):
    """Main application window with tree-style terminal layout."""
    
    def __init__(self, application: "TreeStyleTerminalApp"):
        super().__init__(application=application)
        
        # Set up window properties
        self.set_title("Tree Style Terminal")
        self.set_default_size(1024, 768)
        
        # Initialize domain models
        self.session_tree = SessionTree()
        self.session_manager = SessionManager(self.session_tree)
        self.sidebar_controller = SidebarController(self.session_tree)
        
        # Initialize shortcut controller
        self.shortcut_controller = ShortcutController(self.session_manager, self)
        
        # Legacy terminal management (will be phased out)
        self.terminals: Dict[str, VteTerminal] = {}
        self.terminal_counter = 0
        self.active_terminal_id: Optional[str] = None
        
        # Sidebar state management
        self._sidebar_collapsed = False
        
        # Create header bar
        self._setup_headerbar()
        
        # Load the UI from the Glade file
        self._load_ui()
        
        # Set up session management callbacks
        self._setup_session_callbacks()
        
        # Don't create initial session in constructor to allow clean testing
        # Initial session will be created when needed
        
    def _setup_headerbar(self) -> None:
        """Set up the header bar."""
        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.set_title("Tree Style Terminal")
        self.set_titlebar(self.headerbar)
        
        # Add sidebar toggle button
        self.sidebar_toggle_button = Gtk.Button()
        self.sidebar_toggle_button.set_image(
            Gtk.Image.new_from_icon_name("view-sidebar-symbolic", Gtk.IconSize.BUTTON)
        )
        self.sidebar_toggle_button.set_tooltip_text("Toggle sidebar (F9)")
        self.sidebar_toggle_button.connect("clicked", self._on_sidebar_toggle_clicked)
        self.headerbar.pack_start(self.sidebar_toggle_button)
        
        # Create button container for session actions
        session_buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        session_buttons_box.get_style_context().add_class("linked")
        
        # Add new sibling button (was new_terminal_button)
        self.new_sibling_button = Gtk.Button()
        self.new_sibling_button.set_image(
            Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        )
        self.new_sibling_button.set_tooltip_text("New sibling session (Ctrl+Shift+T)")
        self.new_sibling_button.connect("clicked", self._on_new_terminal_clicked)  # Use existing callback
        session_buttons_box.pack_start(self.new_sibling_button, False, False, 0)
        
        # Add new child button  
        self.new_child_button = Gtk.Button()
        self.new_child_button.set_image(
            Gtk.Image.new_from_icon_name("go-down-symbolic", Gtk.IconSize.BUTTON)
        )
        self.new_child_button.set_tooltip_text("New child session (Ctrl+Alt+T)")
        self.new_child_button.connect("clicked", self._on_new_child_clicked)
        session_buttons_box.pack_start(self.new_child_button, False, False, 0)
        
        # Add close session button
        self.close_session_button = Gtk.Button()
        self.close_session_button.set_image(
            Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.BUTTON)
        )
        self.close_session_button.set_tooltip_text("Close session (Ctrl+Q)")
        self.close_session_button.connect("clicked", self._on_close_session_clicked)
        session_buttons_box.pack_start(self.close_session_button, False, False, 0)
        
        # Add the button box to header bar
        self.headerbar.pack_start(session_buttons_box)
        
        # Keep reference to old new_terminal_button for compatibility
        self.new_terminal_button = self.new_sibling_button
        
    def _load_ui(self) -> None:
        """Load the UI from the Glade file."""
        # Get the path to the UI file
        ui_path = self._get_ui_file_path()
        
        # Create a builder and load the UI
        builder = Gtk.Builder()
        try:
            builder.add_from_file(str(ui_path))
        except Exception as e:
            # Fallback to manual UI creation if file loading fails
            print(f"Warning: Could not load UI file {ui_path}: {e}")
            self._create_manual_ui()
            return
        
        # Get the main container from the UI
        main_container = builder.get_object("main_container")
        if main_container:
            self.add(main_container)
        else:
            self._create_manual_ui()
            return
        
        # Store references to important widgets
        self.sidebar_revealer = builder.get_object("sidebar_revealer")
        self.terminal_stack = builder.get_object("terminal_stack")
        
        # Create and integrate the session sidebar
        sidebar_container = builder.get_object("sidebar_scrolled")
        if sidebar_container:
            # Remove the existing tree view and replace with our SessionSidebar
            old_tree_view = builder.get_object("session_tree_view")
            if old_tree_view:
                sidebar_container.remove(old_tree_view)
            
            # Create our SessionSidebar widget
            self.session_sidebar = SessionSidebar(self.sidebar_controller)
            self.session_sidebar.set_selection_callback(self._on_session_selected)
            self.session_sidebar.show_all()
            sidebar_container.add(self.session_sidebar)
        else:
            self.session_sidebar = None
        
        # Connect signals from UI file
        new_terminal_ui = builder.get_object("new_terminal_button")
        if new_terminal_ui:
            new_terminal_ui.connect("clicked", self._on_new_terminal_clicked)
        
        welcome_new_terminal_ui = builder.get_object("welcome_new_terminal_button")
        if welcome_new_terminal_ui:
            welcome_new_terminal_ui.connect("clicked", self._on_new_terminal_clicked)
        
        # Connect sidebar toggle from UI file
        sidebar_toggle_ui = builder.get_object("sidebar_toggle_button")
        if sidebar_toggle_ui:
            sidebar_toggle_ui.connect("clicked", self._on_sidebar_toggle_clicked)
        
        # Hide header bar sidebar toggle since UI file has its own
        self.sidebar_toggle_button.set_visible(False)
    
    def _create_manual_ui(self) -> None:
        """Create a basic UI manually if Glade file is not available."""
        # Create main horizontal box
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        # Create sidebar area
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.set_size_request(250, -1)
        
        # Create sidebar revealer
        self.sidebar_revealer = Gtk.Revealer()
        self.sidebar_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
        self.sidebar_revealer.set_transition_duration(200)
        self.sidebar_revealer.set_reveal_child(True)
        self.sidebar_revealer.add(sidebar_box)
        
        # Create session sidebar widget
        self.session_sidebar = SessionSidebar(self.sidebar_controller)
        self.session_sidebar.set_selection_callback(self._on_session_selected)
        sidebar_box.pack_start(self.session_sidebar, True, True, 0)
        
        # Create terminal area
        terminal_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Create welcome page
        welcome_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        welcome_box.set_halign(Gtk.Align.CENTER)
        welcome_box.set_valign(Gtk.Align.CENTER)
        welcome_box.set_spacing(12)
        
        welcome_label = Gtk.Label("Welcome to Tree Style Terminal")
        welcome_label.set_markup("<big><b>Welcome to Tree Style Terminal</b></big>")
        welcome_box.pack_start(welcome_label, False, False, 0)
        
        subtitle_label = Gtk.Label("Create a new terminal session to get started")
        welcome_box.pack_start(subtitle_label, False, False, 0)
        
        welcome_button = Gtk.Button.new_with_label("New Terminal")
        welcome_button.connect("clicked", self._on_new_terminal_clicked)
        welcome_box.pack_start(welcome_button, False, False, 0)
        
        # Create stack for terminal switching
        self.terminal_stack = Gtk.Stack()
        self.terminal_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.terminal_stack.add_named(welcome_box, "welcome")
        self.terminal_stack.set_visible_child_name("welcome")
        terminal_area.pack_start(self.terminal_stack, True, True, 0)
        
        # Add separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        
        # Pack everything into main box
        main_box.pack_start(self.sidebar_revealer, False, False, 0)
        main_box.pack_start(separator, False, False, 0)
        main_box.pack_start(terminal_area, True, True, 0)
        
        self.add(main_box)
    
    def _get_ui_file_path(self) -> Path:
        """Get the path to the UI file."""
        # Get the directory where this module is located
        module_dir = Path(__file__).parent
        ui_file = module_dir / "ui" / "main_window.ui"
        return ui_file
    
    def _on_sidebar_toggle_clicked(self, button: Gtk.Button) -> None:
        """Handle sidebar toggle button click."""
        if hasattr(self, 'sidebar_revealer') and self.sidebar_revealer:
            print(f"Sidebar toggle: collapsed={self._sidebar_collapsed} -> {not self._sidebar_collapsed}")
            
            if not self._sidebar_collapsed:  # Currently expanded, so collapse
                # Simply force the revealer to collapse and take no space
                self.sidebar_revealer.set_reveal_child(False)
                self.sidebar_revealer.set_size_request(0, -1)
                self.sidebar_revealer.set_visible(False)
                
                self._sidebar_collapsed = True
                print("Sidebar collapsed (forced invisible)")
            else:  # Currently collapsed, so expand
                # Restore the revealer
                self.sidebar_revealer.set_visible(True)
                self.sidebar_revealer.set_size_request(-1, -1)
                self.sidebar_revealer.set_reveal_child(True)
                
                self._sidebar_collapsed = False
                print("Sidebar expanded (forced visible)")
            
            # Force immediate layout update
            GLib.idle_add(lambda: self.queue_resize())
    
    def _on_new_terminal_clicked(self, button: Gtk.Button) -> None:
        """Handle new terminal button click."""
        # Use shortcut controller action for consistency
        action = self.shortcut_controller.get_action("new_sibling")
        if action:
            action.activate(None)
    
    def _on_close_session_clicked(self, button: Gtk.Button) -> None:
        """Handle close session button click."""
        # Use shortcut controller action for consistency
        action = self.shortcut_controller.get_action("close_session")
        if action:
            action.activate(None)
    
    def _on_new_child_clicked(self, button: Gtk.Button) -> None:
        """Handle new child button click."""
        # Use shortcut controller action for consistency
        action = self.shortcut_controller.get_action("new_child")
        if action:
            action.activate(None)
    
    def _update_button_states(self) -> None:
        """Update button states based on current session state."""
        has_current_session = self.session_manager.current_session is not None
        
        # Update HeaderBar buttons if they exist
        if hasattr(self, 'new_sibling_button'):
            self.new_sibling_button.set_sensitive(True)  # Always available
        if hasattr(self, 'new_child_button'):
            self.new_child_button.set_sensitive(True)  # Always available  
        if hasattr(self, 'close_session_button'):
            self.close_session_button.set_sensitive(has_current_session)
        
        # Update shortcut controller action states
        self.shortcut_controller.update_action_states()
    
    def _create_new_terminal(self, cwd: Optional[str] = None) -> str:
        """
        Create a new terminal session.
        
        Args:
            cwd: Working directory for the new terminal.
            
        Returns:
            Terminal ID of the newly created terminal.
        """
        # Generate unique terminal ID
        self.terminal_counter += 1
        terminal_id = f"terminal_{self.terminal_counter}"
        
        try:
            # Create new VTE terminal widget
            terminal_widget = VteTerminal()
            
            # Spawn shell in the terminal
            if not terminal_widget.spawn_shell(cwd=cwd):
                print(f"Failed to spawn shell in terminal {terminal_id}")
                # Clean up failed terminal
                terminal_widget.destroy()
                return terminal_id
            
            # Store terminal reference
            self.terminals[terminal_id] = terminal_widget
            
            # Show only the terminal widget, not all children to avoid affecting sidebar
            terminal_widget.show()
            
            # Ensure sidebar state is not affected by new terminal
            if hasattr(self, 'sidebar_revealer') and self.sidebar_revealer:
                current_reveal_state = self.sidebar_revealer.get_reveal_child()
                # Re-apply the current state to ensure it's preserved
                GLib.idle_add(lambda: self.sidebar_revealer.set_reveal_child(current_reveal_state))
            
            # Add to stack
            self.terminal_stack.add_named(terminal_widget, terminal_id)
            
            # Switch to the new terminal  
            self._switch_to_terminal(terminal_id)
            
            print(f"Created new terminal: {terminal_id}")
            return terminal_id
            
        except Exception as e:
            print(f"Error creating terminal {terminal_id}: {e}")
            return terminal_id
    
    def _ensure_revealer_state(self, desired_state: bool) -> bool:
        """Ensure the revealer maintains its desired state."""
        if hasattr(self, 'sidebar_revealer') and self.sidebar_revealer:
            current_state = self.sidebar_revealer.get_reveal_child()
            if current_state != desired_state:
                print(f"Correcting revealer state: {current_state} -> {desired_state}")
                self.sidebar_revealer.set_reveal_child(desired_state)
        return False  # Don't repeat
    
    def _switch_to_terminal(self, terminal_id: str) -> None:
        """Switch to the specified terminal."""
        if terminal_id in self.terminals:
            self.terminal_stack.set_visible_child_name(terminal_id)
            self.active_terminal_id = terminal_id
            
            # Update window title with terminal info
            terminal = self.terminals[terminal_id]
            title = terminal.get_window_title()
            self.set_title(f"Tree Style Terminal - {title}")
            
            print(f"Switched to terminal: {terminal_id}")
        else:
            print(f"Terminal {terminal_id} not found")
    
    def _close_terminal(self, terminal_id: str) -> None:
        """Close the specified terminal."""
        if terminal_id in self.terminals:
            terminal = self.terminals[terminal_id]
            terminal.close()
            
            # Remove from stack and dict
            self.terminal_stack.remove(terminal)
            del self.terminals[terminal_id]
            
            # If this was the active terminal, switch to another or welcome
            if self.active_terminal_id == terminal_id:
                if self.terminals:
                    # Switch to the first available terminal
                    next_terminal_id = next(iter(self.terminals.keys()))
                    self._switch_to_terminal(next_terminal_id)
                else:
                    # No terminals left, show welcome page
                    self.terminal_stack.set_visible_child_name("welcome")
                    self.active_terminal_id = None
                    self.set_title("Tree Style Terminal")
            
            print(f"Closed terminal: {terminal_id}")
    
    def _setup_session_callbacks(self) -> None:
        """Set up callbacks for session management."""
        self.session_manager.set_session_created_callback(self._on_session_created)
        self.session_manager.set_session_closed_callback(self._on_session_closed)
        self.session_manager.set_session_selected_callback(self._on_session_selected_by_manager)
    
    def _on_session_created(self, session: TerminalSession, terminal_widget: VteTerminal) -> None:
        """
        Handle session creation.
        
        Args:
            session: The created session
            terminal_widget: The VTE terminal widget
        """
        # Add terminal to the stack
        terminal_id = f"session_{session.pid}"
        terminal_widget.show()
        self.terminal_stack.add_named(terminal_widget, terminal_id)
        
        # Switch to the new terminal
        self.terminal_stack.set_visible_child_name(terminal_id)
        
        # Update sidebar - ADD ONLY THE NEW SESSION instead of full refresh
        if self.session_sidebar:
            parent = self.session_manager.session_tree.get_parent(session)
            self.session_sidebar.controller.add_session(session, parent)
            # Select the new session in the sidebar
            self.session_sidebar.select_session(session)
        
        # Update button states
        self._update_button_states()
        
        print(f"Session created: {session.title}")
    
    def _on_session_closed(self, session: TerminalSession, children_to_adopt: list[TerminalSession], parent_session: Optional[TerminalSession]) -> None:
        """
        Handle session closure.
        
        Args:
            session: The closed session
            children_to_adopt: Children that were adopted during closure
            parent_session: The parent session that adopted the children (or None for root level)
        """
        
        # Remove from terminal stack
        terminal_id = f"session_{session.pid}"
        
        # Find and remove the terminal widget
        for child in self.terminal_stack.get_children():
            if self.terminal_stack.child_get_property(child, "name") == terminal_id:
                self.terminal_stack.remove(child)
                break
        
        # Update sidebar - remove session and handle adoption
        if self.session_sidebar:
            self.session_sidebar.controller.remove_session_with_adoption(session, children_to_adopt, parent_session)
        
        # Update button states
        self._update_button_states()
        
        # Show welcome page if no sessions left
        if not self.session_manager.get_all_sessions():
            self.terminal_stack.set_visible_child_name("welcome")
            self.set_title("Tree Style Terminal")
        
        print(f"Session closed: {session.title}")
    
    def _on_session_selected(self, session: TerminalSession) -> None:
        """
        Handle session selection from sidebar.
        
        Args:
            session: The selected session
        """
        self.session_manager.select_session(session)
    
    def _on_session_selected_by_manager(self, session: TerminalSession) -> None:
        """
        Handle session selection by the session manager.
        
        Args:
            session: The selected session
        """
        # Switch to the terminal
        terminal_id = f"session_{session.pid}"
        self.terminal_stack.set_visible_child_name(terminal_id)
        
        # Update window title
        self.set_title(f"Tree Style Terminal - {session.title}")
        
        # Update sidebar selection
        if self.session_sidebar:
            self.session_sidebar.select_session(session)
        
        # Update button states
        self._update_button_states()
        
        print(f"Switched to session: {session.title}")

    def toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        if hasattr(self, 'sidebar_revealer') and self.sidebar_revealer:
            current_state = self.sidebar_revealer.get_reveal_child()
            self.sidebar_revealer.set_reveal_child(not current_state)
            self._sidebar_collapsed = not current_state
            print(f"Sidebar {'hidden' if current_state else 'shown'}")

    def focus_terminal(self) -> None:
        """Focus the currently active terminal."""
        if self.session_manager.current_session:
            terminal_widget = self.session_manager.get_terminal_widget(self.session_manager.current_session)
            if terminal_widget and hasattr(terminal_widget, 'grab_focus'):
                terminal_widget.grab_focus()
                print("Focused terminal")

    def focus_sidebar(self) -> None:
        """Focus the sidebar tree view."""
        if hasattr(self, 'session_sidebar') and self.session_sidebar:
            if hasattr(self.session_sidebar, 'grab_focus'):
                self.session_sidebar.grab_focus()
                print("Focused sidebar")


class TreeStyleTerminalApp(Gtk.Application):
    """Main GTK application class."""
    
    def __init__(self):
        super().__init__(
            application_id="org.example.TreeStyleTerminal",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        
        self.window: Optional[MainWindow] = None
        
        # Connect the activate signal
        self.connect("activate", self._on_activate)
        self.connect("startup", self._on_startup)
    
    def _on_startup(self, app: "TreeStyleTerminalApp") -> None:
        """Called when the application starts up."""
        # Set up any application-wide resources here
        pass
    
    def _on_activate(self, app: "TreeStyleTerminalApp") -> None:
        """Called when the application is activated."""
        if not self.window:
            self.window = MainWindow(application=self)
        
        self.window.show_all()
        self.window.present()


def main() -> int:
    """Main entry point for the application."""
    # Create and run the application
    app = TreeStyleTerminalApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())