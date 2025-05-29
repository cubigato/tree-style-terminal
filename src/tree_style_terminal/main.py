#!/usr/bin/env python3
"""
Tree Style Terminal - Main application entry point.

This module contains the main GTK application class and window implementation.
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gio, GLib

from .widgets.terminal import VteTerminal


class MainWindow(Gtk.ApplicationWindow):
    """Main application window with tree-style terminal layout."""
    
    def __init__(self, application: "TreeStyleTerminalApp"):
        super().__init__(application=application)
        
        # Set up window properties
        self.set_title("Tree Style Terminal")
        self.set_default_size(1024, 768)
        
        # Terminal management
        self.terminals: Dict[str, VteTerminal] = {}
        self.terminal_counter = 0
        self.active_terminal_id: Optional[str] = None
        
        # Sidebar state management
        self._sidebar_collapsed = False
        
        # Create header bar
        self._setup_headerbar()
        
        # Load the UI from the Glade file
        self._load_ui()
        
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
        self.sidebar_toggle_button.set_tooltip_text("Toggle sidebar")
        self.sidebar_toggle_button.connect("clicked", self._on_sidebar_toggle_clicked)
        self.headerbar.pack_start(self.sidebar_toggle_button)
        
        # Add new terminal button
        self.new_terminal_button = Gtk.Button()
        self.new_terminal_button.set_image(
            Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        )
        self.new_terminal_button.set_tooltip_text("New terminal")
        self.new_terminal_button.connect("clicked", self._on_new_terminal_clicked)
        self.headerbar.pack_start(self.new_terminal_button)
        
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
        self.session_tree_view = builder.get_object("session_tree_view")
        self.terminal_stack = builder.get_object("terminal_stack")
        
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
        
        # Create tree view for sessions
        self.session_tree_view = Gtk.TreeView()
        self.session_tree_view.set_headers_visible(False)
        
        # Add tree view to scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.session_tree_view)
        sidebar_box.pack_start(scrolled, True, True, 0)
        
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
        self._create_new_terminal()
    
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