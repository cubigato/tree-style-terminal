#!/usr/bin/env python3
"""
Tree Style Terminal - Main application entry point.

This module contains the main GTK application class and window implementation.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional, Dict

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gio, GLib, Gdk

from .widgets.terminal import VteTerminal
from .widgets.sidebar import SessionSidebar
from .controllers.sidebar import SidebarController
from .controllers.session_manager import SessionManager
from .controllers.shortcuts import ShortcutController
from .models.session import TerminalSession
from .models.tree import SessionTree
from .config import config_manager, ConfigError


class CSSLoader:
    """Handles CSS loading and theme management for the application."""
    
    def __init__(self, override_dpi=None):
        self.css_provider = Gtk.CssProvider()
        self.theme_provider = Gtk.CssProvider()
        self.system_css_provider = Gtk.CssProvider()
        
        # Load configuration for theme detection
        try:
            config_manager.load_config()
            config_theme = config_manager.get("theme", "automatic")
            if config_theme == "automatic":
                self.current_theme = self._detect_system_theme()
            else:
                self.current_theme = config_theme
        except ConfigError as e:
            print(f"Configuration error: {e}")
            raise
        
        self._override_dpi = override_dpi
        
    def load_base_css(self):
        """Load the base CSS styles with system font detection."""
        # First load system-aware CSS
        self._load_system_css()
        
        css_dir = Path(__file__).parent / "resources" / "css"
        base_css_path = css_dir / "style.css"
        
        if base_css_path.exists():
            try:
                self.css_provider.load_from_path(str(base_css_path))
                self._add_provider_to_screen(self.css_provider)
                print(f"Loaded base CSS from {base_css_path}")
            except GLib.Error as e:
                print(f"Error loading base CSS: {e}")
        else:
            print(f"Warning: Base CSS file not found at {base_css_path}")
    
    def _load_system_css(self):
        """Dynamic CSS generation disabled; using static style.css only."""
        return
    
    def load_theme(self, theme_name: str):
        """Load a specific theme (light/dark)."""
        css_dir = Path(__file__).parent / "resources" / "css"
        theme_css_path = css_dir / f"{theme_name}-theme.css"
        
        if theme_css_path.exists():
            try:
                # Remove old theme provider
                screen = Gdk.Screen.get_default()
                context = Gtk.StyleContext()
                context.remove_provider_for_screen(screen, self.theme_provider)
                
                # Load new theme
                self.theme_provider = Gtk.CssProvider()
                self.theme_provider.load_from_path(str(theme_css_path))
                self._add_provider_to_screen(self.theme_provider)
                
                # Reload system CSS after theme to ensure transparency overrides
                self._load_system_css()
                
                self.current_theme = theme_name
                print(f"Loaded {theme_name} theme from {theme_css_path}")
            except GLib.Error as e:
                print(f"Error loading {theme_name} theme: {e}")
        else:
            print(f"Warning: Theme file not found at {theme_css_path}")
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.load_theme(new_theme)
    
    def _add_provider_to_screen(self, provider):
        """Helper to add CSS provider to screen."""
        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        # Use APPLICATION priority (800) which is higher than theme (600) to ensure our CSS overrides Adwaita
        priority = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        context.add_provider_for_screen(
            screen, 
            provider, 
            priority
        )
    
    def _detect_system_theme(self):
        """Detect the system's preferred theme (light/dark)."""
        try:
            settings = Gtk.Settings.get_default()
            
            # Try to get the dark theme preference
            prefer_dark = settings.get_property("gtk-application-prefer-dark-theme")
            if prefer_dark:
                print("Detected system preference: dark theme")
                return "dark"
            
            # Fallback: check the theme name for dark indicators
            theme_name = settings.get_property("gtk-theme-name") or ""
            theme_name_lower = theme_name.lower()
            
            if any(dark_indicator in theme_name_lower for dark_indicator in ["dark", "noir", "black", "adwaita-dark"]):
                print(f"Detected dark theme from theme name: {theme_name}")
                return "dark"
            
            print(f"Detected light theme (theme name: {theme_name})")
            return "light"
            
        except Exception as e:
            print(f"Could not detect system theme preference: {e}")
            print("Falling back to light theme")
            return "light"


class MainWindow(Gtk.ApplicationWindow):
    """Main application window with tree-style terminal layout."""
    
    def __init__(self, application: "TreeStyleTerminalApp"):
        super().__init__(application=application)
        
        # Load configuration
        try:
            config_manager.load_config()
        except ConfigError as e:
            print(f"Configuration error: {e}")
            raise
        
        # Check transparency requirements and enable RGBA visual if needed
        transparency = config_manager.get("terminal.transparency", 1.0)
        if transparency < 1.0:
            self._setup_transparency()
        
        # Add CSS class to window
        self.get_style_context().add_class("main-window")
        
        # Add theme class to window for CSS targeting
        app = application
        if hasattr(app, 'css_loader') and hasattr(app.css_loader, 'current_theme'):
            self.get_style_context().add_class(app.css_loader.current_theme)
        
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
        
        # Update theme button icon based on current theme
        self._update_theme_button_icon()
        
        # Load the UI from the Glade file
        self._load_ui()
        
        # Set up session management callbacks
        self._setup_session_callbacks()
        
        # Don't create initial session in constructor to allow clean testing
        # Initial session will be created when needed
    

    def _setup_transparency(self) -> None:
        """Set up RGBA visual for terminal transparency support."""
        screen = self.get_screen()
        
        # Check if compositing is available
        if not screen.is_composited():
            print("Error: Terminal transparency requires a compositing window manager, but none is available.")
            print("Please disable transparency in the configuration or enable a compositing manager.")
            exit(1)
        
        # Get RGBA visual
        visual = screen.get_rgba_visual()
        if visual is None:
            print("Error: RGBA visual not available for terminal transparency.")
            print("Please disable transparency in the configuration.")
            exit(1)
        
        # Enable RGBA visual and app paintable
        self.set_visual(visual)
        self.set_app_paintable(True)
        
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
        
        # Add theme toggle button
        self.theme_toggle_button = Gtk.Button()
        self.theme_toggle_button.set_image(
            Gtk.Image.new_from_icon_name("weather-clear-night-symbolic", Gtk.IconSize.BUTTON)
        )
        self.theme_toggle_button.set_tooltip_text("Toggle Dark/Light Theme")
        self.theme_toggle_button.connect("clicked", self._on_theme_toggle_clicked)
        self.headerbar.pack_end(self.theme_toggle_button)
        
        # Keep reference to old new_terminal_button for compatibility
        self.new_terminal_button = self.new_sibling_button
        
    def _load_ui(self) -> None:
        """Load the UI from Glade file or create manually."""
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
            # For UI file compatibility, set main_paned to main_container
            # This allows toggle functions to work with both UI types
            self.main_paned = main_container
            self.add(main_container)
        else:
            self._create_manual_ui()
            return
        
        # Store references to important widgets
        self.sidebar_revealer = builder.get_object("sidebar_revealer")
        self.terminal_stack = builder.get_object("terminal_stack")
        
        # Initialize sidebar state tracking for UI file compatibility
        self._sidebar_collapsed = False
        self._saved_sidebar_width = config_manager.get("ui.sidebar_width", 250)
        
        # Connect paned position changes if main_container is a Paned
        if hasattr(self.main_paned, 'get_position') and callable(getattr(self.main_paned, 'get_position', None)):
            self.main_paned.connect("notify::position", self._on_paned_position_changed)
        
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
        # Create main horizontal paned for resizable sidebar
        self.main_paned = Gtk.HPaned()
        self.main_paned.get_style_context().add_class("main-paned")
        
        # Create sidebar area
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # Remove fixed width - let paned handle sizing
        
        # Create sidebar revealer
        self.sidebar_revealer = Gtk.Revealer()
        self.sidebar_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
        self.sidebar_revealer.set_transition_duration(200)
        self.sidebar_revealer.set_reveal_child(True)
        self.sidebar_revealer.get_style_context().add_class("sidebar")
        self.sidebar_revealer.add(sidebar_box)
        
        # Initialize sidebar state tracking with config
        self._sidebar_collapsed = False
        self._saved_sidebar_width = config_manager.get("ui.sidebar_width", 250)
        
        # Create session sidebar widget
        self.session_sidebar = SessionSidebar(self.sidebar_controller)
        self.session_sidebar.set_selection_callback(self._on_session_selected)
        self.session_sidebar.get_style_context().add_class("sidebar")
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
        
        # Pack into paned widget (no separator needed - paned has built-in handle)
        self.main_paned.pack1(self.sidebar_revealer, resize=False, shrink=False)
        self.main_paned.pack2(terminal_area, resize=True, shrink=True)
        
        # Set initial sidebar width
        self.main_paned.set_position(self._saved_sidebar_width)
        
        # Connect to position changes for width constraints
        self.main_paned.connect("notify::position", self._on_paned_position_changed)
        
        self.add(self.main_paned)
    
    def _get_ui_file_path(self) -> Path:
        """Get the path to the UI file."""
        # Get the directory where this module is located
        module_dir = Path(__file__).parent
        ui_file = module_dir / "ui" / "main_window.ui"
        return ui_file
    
    def _on_sidebar_toggle_clicked(self, button: Gtk.Button) -> None:
        """Handle sidebar toggle button click."""
        self.toggle_sidebar()
    
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
    
    def _on_theme_toggle_clicked(self, button: Gtk.Button) -> None:
        """Handle theme toggle button click."""
        app = self.get_application()
        app.css_loader.toggle_theme()
        
        # Update all terminals with the new theme
        self._update_terminal_themes(app.css_loader.current_theme)
        
        # Update window CSS class for theme
        self._update_window_theme_class(app.css_loader.current_theme)
        
        # Update button icon based on current theme
        self._update_theme_button_icon()
    
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
            
            # Apply current theme to the new terminal
            app = self.get_application()
            if app and hasattr(app, 'css_loader'):
                terminal_widget.apply_theme(app.css_loader.current_theme)
            
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
        self.session_manager.set_session_changed_callback(self._on_session_changed)
        
        # Set initial theme in session manager
        app = self.get_application()
        if app and hasattr(app, 'css_loader'):
            self.session_manager.set_theme(app.css_loader.current_theme)
    
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
    
    def _on_session_changed(self, session: TerminalSession) -> None:
        """
        Handle session property changes (e.g., CWD, title updates).
        
        Args:
            session: The session that changed
        """
        # Update sidebar display
        if self.session_sidebar:
            self.session_sidebar.controller.update_session(session)
        
        # Update window title if this is the current session
        if self.session_manager.current_session == session:
            self.set_title(f"Tree Style Terminal - {session.title}")
        
        print(f"Session changed: {session.title}")
    
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
            print(f"Sidebar toggle: collapsed={self._sidebar_collapsed} -> {not self._sidebar_collapsed}")
            
            if not self._sidebar_collapsed:  # Currently expanded, so collapse
                self._collapse_sidebar()
            else:  # Currently collapsed, so expand
                self._expand_sidebar()

    def _collapse_sidebar(self) -> None:
        """Collapse the sidebar."""
        if self._is_paned_layout():
            # Save current width before collapsing (Paned layout)
            self._saved_sidebar_width = max(150, self.main_paned.get_position())
            
            # Hide the revealer completely to make it disappear from paned
            self.sidebar_revealer.set_reveal_child(False)
            self.sidebar_revealer.set_visible(False)
            
            print(f"Sidebar collapsed (paned, saved width: {self._saved_sidebar_width})")
        else:
            # Box layout - use revealer properties
            self.sidebar_revealer.set_reveal_child(False)
            self.sidebar_revealer.set_size_request(0, -1)
            self.sidebar_revealer.set_visible(False)
            print("Sidebar collapsed (box layout)")
        
        self._sidebar_collapsed = True

    def _expand_sidebar(self) -> None:
        """Expand the sidebar."""
        if self._is_paned_layout():
            # First make revealer visible and restore position
            self.sidebar_revealer.set_visible(True)
            self.main_paned.set_position(self._saved_sidebar_width)
            
            # Then show the revealer content
            # Use idle_add to ensure position is set before revealing content
            GLib.idle_add(lambda: self.sidebar_revealer.set_reveal_child(True))
            
            print(f"Sidebar expanded (paned, restored width: {self._saved_sidebar_width})")
        else:
            # Box layout - restore revealer properties
            self.sidebar_revealer.set_visible(True)
            self.sidebar_revealer.set_size_request(-1, -1)
            self.sidebar_revealer.set_reveal_child(True)
            print("Sidebar expanded (box layout)")
        
        self._sidebar_collapsed = False

    def _is_paned_layout(self) -> bool:
        """Check if we're using Paned layout (manual UI) vs Box layout (UI file)."""
        return hasattr(self.main_paned, 'get_position') and callable(getattr(self.main_paned, 'get_position', None))

    def _on_paned_position_changed(self, paned: Gtk.HPaned, param_spec: object) -> None:
        """Handle paned position changes to enforce width constraints."""
        if not hasattr(self, '_sidebar_collapsed') or self._sidebar_collapsed:
            return
            
        current_position = paned.get_position()
        
        # Define min/max constraints
        min_width = 150
        max_width = 500
        
        # Enforce constraints
        if current_position < min_width and current_position > 0:
            paned.set_position(min_width)
        elif current_position > max_width:
            paned.set_position(max_width)

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
    
    def _update_terminal_themes(self, theme_name: str) -> None:
        """Update all terminals to use the specified theme."""
        # Update legacy terminals dictionary
        for terminal_widget in self.terminals.values():
            if hasattr(terminal_widget, 'apply_theme'):
                terminal_widget.apply_theme(theme_name)
        
        # Update terminals managed by session manager
        if hasattr(self.session_manager, 'set_theme'):
            self.session_manager.set_theme(theme_name)
        
        print(f"Updated all terminals to {theme_name} theme")
    
    def _update_window_theme_class(self, theme_name: str) -> None:
        """Update window CSS class for theme targeting."""
        style_context = self.get_style_context()
        
        # Remove old theme classes
        style_context.remove_class("light")
        style_context.remove_class("dark")
        
        # Add new theme class
        style_context.add_class(theme_name)
        print(f"Updated window theme class to {theme_name}")
    
    def _update_theme_button_icon(self) -> None:
        """Update theme toggle button icon based on current theme."""
        app = self.get_application()
        current_theme = app.css_loader.current_theme
        
        if current_theme == "dark":
            self.theme_toggle_button.set_image(
                Gtk.Image.new_from_icon_name("weather-clear-symbolic", Gtk.IconSize.BUTTON)
            )
            self.theme_toggle_button.set_tooltip_text("Switch to Light Theme")
        else:
            self.theme_toggle_button.set_image(
                Gtk.Image.new_from_icon_name("weather-clear-night-symbolic", Gtk.IconSize.BUTTON)
            )
            self.theme_toggle_button.set_tooltip_text("Switch to Dark Theme")


class TreeStyleTerminalApp(Gtk.Application):
    """Main GTK application class."""
    
    def __init__(self, args=None):
        super().__init__(
            application_id="org.example.TreeStyleTerminal",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        
        self.window: Optional[MainWindow] = None
        self.args = args or {}
        self.css_loader = CSSLoader(override_dpi=self.args.get('dpi'))
        
        # Connect the activate signal
        self.connect("activate", self._on_activate)
        self.connect("startup", self._on_startup)
    
    def _on_startup(self, app: "TreeStyleTerminalApp") -> None:
        """Called when the application starts up."""
        if not self.args.get('quiet'):
            print("Tree Style Terminal starting up...")
        
        # Print system information for debugging (independent of quiet mode)
        if self.args.get('show_info'):
            self._print_system_info()
        
        # Load CSS styles
        self.css_loader.load_base_css()
        self.css_loader.load_theme(self.css_loader.current_theme)  # Use detected system theme
    
    def _print_system_info(self) -> None:
        """Print system information for debugging font scaling."""
        try:
            settings = Gtk.Settings.get_default()
            screen = Gdk.Screen.get_default()
            
            # System font information
            font_name = settings.get_property("gtk-font-name")
            try:
                mono_font = settings.get_property("gtk-monospace-font-name")
            except:
                try:
                    mono_font = settings.get_property("gtk-monospace-font")
                except:
                    mono_font = None
            dpi = settings.get_property("gtk-xft-dpi")
            
            # Display information
            display = screen.get_display()
            monitor = display.get_primary_monitor() or display.get_monitor(0)
            geometry = monitor.get_geometry()
            width = geometry.width
            height = geometry.height
            width_mm = monitor.get_width_mm()
            height_mm = monitor.get_height_mm()
            
            # Calculate actual DPI
            if width_mm > 0 and height_mm > 0:
                dpi_x = (width * 25.4) / width_mm
                dpi_y = (height * 25.4) / height_mm
                avg_dpi = (dpi_x + dpi_y) / 2
            else:
                avg_dpi = 96  # fallback
            
            print(f"System Information:")
            print(f"  Display: {width}x{height} pixels, {width_mm}x{height_mm}mm")
            print(f"  Calculated DPI: {avg_dpi:.1f}")
            print(f"  GTK XFT DPI: {dpi/1024.0 if dpi else 'not set'}")
            print(f"  System font: {font_name or 'not set'}")
            print(f"  Monospace font: {mono_font or 'not set'}")
            print(f"  Manual DPI override: {os.environ.get('TST_DPI', 'not set')}")
            
        except Exception as e:
            print(f"Could not retrieve system information: {e}")
    

    def _on_activate(self, app: "TreeStyleTerminalApp") -> None:
        """Called when the application is activated."""
        if not self.window:
            self.window = MainWindow(application=self)
        
        self.window.show_all()
        self.window.present()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Tree Style Terminal - Terminal with tree-based session management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
DPI Configuration Examples:
  %(prog)s --dpi 144           # 1.5x scaling for 1440p displays
  %(prog)s --dpi 192           # 2x scaling for 4K displays  
  %(prog)s --dpi 240           # 2.5x scaling for high-DPI 4K
  %(prog)s --show-info         # Show system font information
  %(prog)s --show-info --dpi 180  # Test DPI settings without starting GUI

Environment Variables:
  TST_DPI=192                  # Alternative way to set DPI
        """
    )
    
    parser.add_argument(
        '--dpi',
        type=float,
        help='Override DPI for font scaling (e.g., 144, 192, 240)'
    )
    
    parser.add_argument(
        '--show-info',
        action='store_true',
        help='Show system display and font information'
    )
    
    parser.add_argument(
        '--test-fonts',
        action='store_true',
        help='Show font scaling test and exit (like font_test.py)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress startup messages'
    )
    
    return parser.parse_args()

def print_font_test_info(dpi_override=None):
    """Print font scaling test information (integrated from font_test.py)."""
    print("=== Font Scaling Information ===\n")
    
    try:
        # Initialize GTK to get settings
        Gtk.init([])
        
        settings = Gtk.Settings.get_default()
        screen = Gdk.Screen.get_default()
        
        # System font information
        font_name = settings.get_property("gtk-font-name")
        try:
            mono_font = settings.get_property("gtk-monospace-font-name")
        except:
            try:
                mono_font = settings.get_property("gtk-monospace-font")
            except:
                mono_font = None
        dpi = settings.get_property("gtk-xft-dpi")
        
        # Display information
        display = screen.get_display()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        geometry = monitor.get_geometry()
        width = geometry.width
        height = geometry.height
        width_mm = monitor.get_width_mm()
        height_mm = monitor.get_height_mm()
        
        # Calculate actual DPI
        if width_mm > 0 and height_mm > 0:
            dpi_x = (width * 25.4) / width_mm
            dpi_y = (height * 25.4) / height_mm
            avg_dpi = (dpi_x + dpi_y) / 2
        else:
            avg_dpi = 96  # fallback
        
        print("System Information:")
        print(f"  Display: {width}x{height} pixels")
        print(f"  Physical size: {width_mm}x{height_mm}mm")
        print(f"  Calculated DPI: {avg_dpi:.1f}")
        print(f"  GTK XFT DPI: {dpi/1024.0 if dpi else 'not set'}")
        print(f"  System font: {font_name or 'not set'}")
        print(f"  Monospace font: {mono_font or 'not set'}")
        
        # Environment and argument overrides
        env_dpi = os.environ.get('TST_DPI')
        print(f"  Environment DPI: {env_dpi or 'not set'}")
        print(f"  Argument DPI: {dpi_override or 'not set'}")
        
        print("\nFont Size Calculations:")
        
        # Parse system font size
        if font_name:
            font_parts = font_name.split()
            try:
                base_font_size = float(font_parts[-1])
            except (ValueError, IndexError):
                base_font_size = 10.0
        else:
            base_font_size = 10.0
        
        # Use argument override, then environment, then system DPI
        effective_dpi = dpi_override or (float(env_dpi) if env_dpi else (dpi/1024.0 if dpi else avg_dpi))
        scale_factor = max(effective_dpi / 96.0, 1.0)
        
        # Calculate scaled sizes (same logic as in CSSLoader)
        if effective_dpi >= 180:
            min_ui_size = 14
            min_terminal_size = 15
        else:
            min_ui_size = 10
            min_terminal_size = 11
        
        ui_font_size = max(int(base_font_size * scale_factor), min_ui_size)
        terminal_font_size = max(int((base_font_size + 1) * scale_factor), min_terminal_size)
        
        print(f"  Base font size: {base_font_size}px")
        print(f"  Effective DPI: {effective_dpi:.1f}")
        print(f"  Scale factor: {scale_factor:.2f}")
        print(f"  UI font size: {ui_font_size}px")
        print(f"  Terminal font size: {terminal_font_size}px")
        
        # Recommendations
        print("\nRecommendations:")
        if avg_dpi >= 180:
            print("  High DPI display detected (4K+ resolution)")
            if not dpi_override and not env_dpi:
                print("  Consider using --dpi argument for custom scaling")
                print(f"  Example: tree-style-terminal --dpi {avg_dpi:.0f}")
        elif avg_dpi >= 120:
            print("  Medium-high DPI display detected")
        else:
            print("  Standard DPI display")
        
        if ui_font_size < 12:
            print("  Warning: UI fonts may be too small for comfortable reading")
        if terminal_font_size < 12:
            print("  Warning: Terminal fonts may be too small for comfortable reading")
            
    except Exception as e:
        print(f"Error retrieving system information: {e}")

def main() -> int:
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Handle special modes that don't need the full GUI
    if args.test_fonts:
        print_font_test_info(args.dpi)
        return 0
    
    # Create application with parsed arguments
    app_args = {
        'dpi': args.dpi,
        'show_info': args.show_info,
        'quiet': args.quiet
    }
    
    # Create filtered argv for GTK (remove our custom arguments)
    gtk_argv = [sys.argv[0]]  # Keep program name
    
    app = TreeStyleTerminalApp(app_args)
    return app.run(gtk_argv)


if __name__ == "__main__":
    sys.exit(main())