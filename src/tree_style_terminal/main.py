#!/usr/bin/env python3
"""
Tree Style Terminal - Main application entry point.

This module contains the main GTK application class and window implementation.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk, Gio, GLib, Gtk

from .config import ConfigError, config_manager
from .config.defaults import DEFAULT_CONFIG
from .config.workspace_profile import (
    WorkspaceProfile,
    WorkspaceProfileError,
    load_workspace_profile,
)
from .controllers.session_manager import SessionManager
from .controllers.shortcuts import ShortcutController
from .controllers.sidebar import SidebarController
from .css_loader import CSSLoader
from .models.session import TerminalSession
from .models.tree import SessionTree
from .widgets.sidebar import SessionSidebar
from .widgets.terminal import VteTerminal

logger = logging.getLogger(__name__)


DEFAULT_WINDOW_WIDTH = 1024


@dataclass(frozen=True)
class SidebarWidthBounds:
    """Computed sidebar size limits for the current window width."""

    minimum: int
    default: int
    maximum: int


def clamp_sidebar_width(value: int, bounds: SidebarWidthBounds) -> int:
    """Clamp a sidebar width to the computed bounds."""
    return max(bounds.minimum, min(value, bounds.maximum))


def calculate_sidebar_width_bounds(window_width: int) -> SidebarWidthBounds:
    """Calculate sidebar min/default/max widths from the available window width."""
    available_width = max(window_width, 1)
    minimum = max(150, min(round(available_width * 0.12), 260))
    default = max(250, min(round(available_width * 0.22), 560))

    terminal_reserve = 360
    desired_maximum = max(320, round(available_width * 0.40))
    upper_maximum = min(1000, max(minimum, available_width - terminal_reserve))
    maximum = min(desired_maximum, upper_maximum)
    maximum = max(minimum, maximum)
    default = max(minimum, min(default, maximum))

    return SidebarWidthBounds(
        minimum=minimum,
        default=default,
        maximum=maximum,
    )


def configure_sidebar_paned(paned: Gtk.Paned) -> None:
    """Apply shared sidebar paned behavior."""
    paned.get_style_context().add_class("main-paned")
    if hasattr(paned, "set_wide_handle"):
        paned.set_wide_handle(False)


class MainWindow(Gtk.ApplicationWindow):
    """Main application window with tree-style terminal layout."""

    def __init__(self, application: TreeStyleTerminalApp):
        super().__init__(application=application)

        # Load configuration
        try:
            config_manager.load_config()
        except ConfigError as e:
            logger.error("Configuration error: %s", e)
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
            logger.error(
                "Terminal transparency requires a compositing window manager, but none is available. "
                "Please disable transparency in the configuration or enable a compositing manager."
            )
            raise SystemExit(1)

        # Get RGBA visual
        visual = screen.get_rgba_visual()
        if visual is None:
            logger.error(
                "RGBA visual not available for terminal transparency. "
                "Please disable transparency in the configuration."
            )
            raise SystemExit(1)

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
            Gtk.Image.new_from_icon_name("sidebar-show-symbolic", Gtk.IconSize.BUTTON)
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

        # Add active-terminal search button
        self.search_button = Gtk.Button()
        self.search_button.set_image(
            Gtk.Image.new_from_icon_name("edit-find-symbolic", Gtk.IconSize.BUTTON)
        )
        search_shortcut = config_manager.get("shortcuts.terminal_search", "<Control><Shift>f")
        self.search_button.set_tooltip_text(f"Search active terminal ({search_shortcut})")
        self.search_button.connect("clicked", self._on_search_clicked)
        self.search_button.set_sensitive(False)
        self.headerbar.pack_end(self.search_button)

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
            logger.warning("Could not load UI file %s: %s", ui_path, e)
            self._create_manual_ui()
            return

        # Get the main container from the UI
        main_container = builder.get_object("main_container")
        if main_container:
            # For UI file compatibility, set main_paned to main_container
            # This allows toggle functions to work with both UI types
            self.main_paned = main_container
            configure_sidebar_paned(self.main_paned)
            self.add(main_container)
        else:
            self._create_manual_ui()
            return

        # Store references to important widgets
        self.sidebar_revealer = builder.get_object("sidebar_revealer")
        self.terminal_stack = builder.get_object("terminal_stack")
        self._mark_sidebar_transparency_widgets(
            self.sidebar_revealer,
            builder.get_object("sidebar_container"),
            builder.get_object("sidebar_header"),
            builder.get_object("sidebar_scrolled"),
        )

        # Initialize sidebar state tracking for UI file compatibility
        self._sidebar_collapsed = False
        self._sidebar_uses_dynamic_default = self._uses_default_sidebar_width()
        self._updating_sidebar_position = False
        self._programmatic_sidebar_position = None
        self._saved_sidebar_width = self._get_initial_sidebar_width()
        self._set_sidebar_position(self._saved_sidebar_width)

        # Connect paned position changes if main_container is a Paned
        if hasattr(self.main_paned, 'get_position') and callable(getattr(self.main_paned, 'get_position', None)):
            self.main_paned.connect("notify::position", self._on_paned_position_changed)
            self.main_paned.connect("size-allocate", self._on_paned_size_allocate)

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
            self.session_sidebar.set_rename_callback(self._on_session_rename_requested)
            self.session_sidebar.set_clear_title_callback(self._on_session_clear_title_requested)
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

    def _mark_sidebar_transparency_widgets(self, *widgets: Gtk.Widget) -> None:
        """Add CSS hooks used by runtime sidebar transparency rules."""
        for widget in widgets:
            if widget is None:
                continue
            context = widget.get_style_context()
            context.add_class("sidebar-transparency-root")
            context.remove_class("view")

    def _uses_default_sidebar_width(self) -> bool:
        return config_manager.get("ui.sidebar_width", 250) == DEFAULT_CONFIG["ui"]["sidebar_width"]

    def _get_sidebar_bounds(self, paned: Gtk.Paned | None = None) -> SidebarWidthBounds:
        paned = paned or self.main_paned
        allocated_width = paned.get_allocated_width() if paned else 0
        window_width = max(allocated_width, self.get_allocated_width(), DEFAULT_WINDOW_WIDTH)
        return calculate_sidebar_width_bounds(window_width)

    def _get_initial_sidebar_width(self) -> int:
        bounds = self._get_sidebar_bounds()
        configured_width = config_manager.get("ui.sidebar_width", bounds.default)
        if self._uses_default_sidebar_width():
            return bounds.default
        return clamp_sidebar_width(configured_width, bounds)

    def _set_sidebar_position(self, width: int) -> None:
        self._programmatic_sidebar_position = width
        self._updating_sidebar_position = True
        try:
            self.main_paned.set_position(width)
        finally:
            self._updating_sidebar_position = False

    def _create_manual_ui(self) -> None:
        """Create a basic UI manually if Glade file is not available."""
        # Create main horizontal paned for resizable sidebar
        self.main_paned = Gtk.HPaned()
        configure_sidebar_paned(self.main_paned)

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
        self._sidebar_uses_dynamic_default = self._uses_default_sidebar_width()
        self._updating_sidebar_position = False
        self._programmatic_sidebar_position = None
        self._saved_sidebar_width = self._get_initial_sidebar_width()

        # Create session sidebar widget
        self.session_sidebar = SessionSidebar(self.sidebar_controller)
        self.session_sidebar.set_selection_callback(self._on_session_selected)
        self.session_sidebar.set_rename_callback(self._on_session_rename_requested)
        self.session_sidebar.set_clear_title_callback(self._on_session_clear_title_requested)
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
        self._set_sidebar_position(self._saved_sidebar_width)

        # Connect to position changes for width constraints
        self.main_paned.connect("notify::position", self._on_paned_position_changed)
        self.main_paned.connect("size-allocate", self._on_paned_size_allocate)

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

    def _on_search_clicked(self, button: Gtk.Button) -> None:
        """Handle terminal search button click."""
        action = self.shortcut_controller.get_action("terminal_search")
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
        if hasattr(self, 'search_button'):
            self.search_button.set_sensitive(has_current_session)

        # Update shortcut controller action states
        self.shortcut_controller.update_action_states()

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

        GLib.idle_add(self.focus_terminal)

        logger.debug(f"Session created: {session.title}")

    def _on_session_closed(self, session: TerminalSession, children_to_adopt: list[TerminalSession], parent_session: TerminalSession | None) -> None:
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

        logger.debug(f"Session closed: {session.title}")

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

        logger.debug(f"Session changed: {session.title}")

    def _on_session_selected(self, session: TerminalSession) -> None:
        """
        Handle session selection from sidebar.

        Args:
            session: The selected session
        """
        focus_terminal_after_select = (
            self.session_sidebar is not None
            and self.session_sidebar.last_selection_was_pointer()
        )
        self.session_manager.select_session(session)
        if focus_terminal_after_select:
            GLib.idle_add(self.focus_terminal)

    def _on_session_rename_requested(self, session: TerminalSession, title: str) -> None:
        """Handle a session rename request from the sidebar."""
        self.session_manager.rename_session(session, title)

    def _on_session_clear_title_requested(self, session: TerminalSession) -> None:
        """Handle a custom-title clear request from the sidebar."""
        self.session_manager.clear_session_title(session)

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

        logger.debug(f"Switched to session: {session.title}")

    def toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        if hasattr(self, 'sidebar_revealer') and self.sidebar_revealer:
            logger.debug(
                "Sidebar toggle: collapsed=%s -> %s",
                self._sidebar_collapsed,
                not self._sidebar_collapsed,
            )

            if not self._sidebar_collapsed:  # Currently expanded, so collapse
                self._collapse_sidebar()
            else:  # Currently collapsed, so expand
                self._expand_sidebar()

    def _collapse_sidebar(self) -> None:
        """Collapse the sidebar."""
        if self._is_paned_layout():
            # Save current width before collapsing (Paned layout)
            bounds = self._get_sidebar_bounds()
            self._saved_sidebar_width = clamp_sidebar_width(self.main_paned.get_position(), bounds)

            # Hide the revealer completely to make it disappear from paned
            self.sidebar_revealer.set_reveal_child(False)
            self.sidebar_revealer.set_visible(False)

            logger.debug("Sidebar collapsed (paned, saved width: %s)", self._saved_sidebar_width)
        else:
            # Box layout - use revealer properties
            self.sidebar_revealer.set_reveal_child(False)
            self.sidebar_revealer.set_size_request(0, -1)
            self.sidebar_revealer.set_visible(False)
            logger.debug("Sidebar collapsed (box layout)")

        self._sidebar_collapsed = True

    def _expand_sidebar(self) -> None:
        """Expand the sidebar."""
        if self._is_paned_layout():
            # First make revealer visible and restore position
            self.sidebar_revealer.set_visible(True)
            self._set_sidebar_position(clamp_sidebar_width(self._saved_sidebar_width, self._get_sidebar_bounds()))

            # Then show the revealer content
            # Use idle_add to ensure position is set before revealing content
            GLib.idle_add(lambda: self.sidebar_revealer.set_reveal_child(True))

            logger.debug("Sidebar expanded (paned, restored width: %s)", self._saved_sidebar_width)
        else:
            # Box layout - restore revealer properties
            self.sidebar_revealer.set_visible(True)
            self.sidebar_revealer.set_size_request(-1, -1)
            self.sidebar_revealer.set_reveal_child(True)
            logger.debug("Sidebar expanded (box layout)")

        self._sidebar_collapsed = False

    def _is_paned_layout(self) -> bool:
        """Check if we're using Paned layout (manual UI) vs Box layout (UI file)."""
        return hasattr(self.main_paned, 'get_position') and callable(getattr(self.main_paned, 'get_position', None))

    def _on_paned_position_changed(self, paned: Gtk.HPaned, param_spec: object) -> None:
        """Handle paned position changes to enforce width constraints."""
        if not hasattr(self, '_sidebar_collapsed') or self._sidebar_collapsed:
            return

        current_position = paned.get_position()
        expected_position = getattr(self, "_programmatic_sidebar_position", None)
        if expected_position is not None:
            self._programmatic_sidebar_position = None
        elif not getattr(self, "_updating_sidebar_position", False):
            self._sidebar_uses_dynamic_default = False

        bounds = self._get_sidebar_bounds(paned)
        constrained_position = clamp_sidebar_width(current_position, bounds)

        if constrained_position != current_position:
            self._set_sidebar_position(constrained_position)
            current_position = constrained_position

        self._saved_sidebar_width = current_position

    def _on_paned_size_allocate(self, paned: Gtk.HPaned, allocation: Gdk.Rectangle) -> None:
        """Keep sidebar size within bounds after the window is resized."""
        if not hasattr(self, '_sidebar_collapsed') or self._sidebar_collapsed:
            return

        bounds = calculate_sidebar_width_bounds(allocation.width)
        current_position = paned.get_position()
        if getattr(self, "_sidebar_uses_dynamic_default", False):
            target_position = bounds.default
        else:
            target_position = clamp_sidebar_width(current_position, bounds)

        if current_position != target_position:
            self._set_sidebar_position(target_position)
        self._saved_sidebar_width = target_position

    def focus_terminal(self) -> None:
        """Focus the currently active terminal."""
        if self.session_manager.current_session:
            terminal_widget = self.session_manager.get_terminal_widget(self.session_manager.current_session)
            if terminal_widget and hasattr(terminal_widget, 'grab_focus'):
                terminal_widget.grab_focus()
                logger.debug("Focused terminal")

    def focus_sidebar(self) -> None:
        """Focus the sidebar tree view."""
        if (
            hasattr(self, 'session_sidebar')
            and self.session_sidebar
            and hasattr(self.session_sidebar, 'grab_focus')
        ):
            self.session_sidebar.grab_focus()

    def _update_terminal_themes(self, theme_name: str) -> None:
        """Update all terminals to use the specified theme."""
        self.session_manager.set_theme(theme_name)
        logger.info("Updated all terminals to %s theme", theme_name)

    def _update_window_theme_class(self, theme_name: str) -> None:
        """Update window CSS class for theme targeting."""
        style_context = self.get_style_context()

        # Remove old theme classes
        style_context.remove_class("light")
        style_context.remove_class("dark")

        # Add new theme class
        style_context.add_class(theme_name)
        logger.debug("Updated window theme class to %s", theme_name)

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
            flags=Gio.ApplicationFlags.NON_UNIQUE
        )

        self.window: MainWindow | None = None
        self.args = args or {}
        self._initial_session_created = False
        self.css_loader = CSSLoader(override_dpi=self.args.get('dpi'))

        # Connect the activate signal
        self.connect("activate", self._on_activate)
        self.connect("startup", self._on_startup)

    def _on_startup(self, app: TreeStyleTerminalApp) -> None:
        """Called when the application starts up."""
        if not self.args.get('quiet'):
            logger.info("Tree Style Terminal starting up...")

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
            except (AttributeError, TypeError):
                try:
                    mono_font = settings.get_property("gtk-monospace-font")
                except (AttributeError, TypeError):
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
            print(f"  Display: {width}x{height} pixels, {width_mm}x{height_mm}mm")
            print(f"  Calculated DPI: {avg_dpi:.1f}")
            print(f"  GTK XFT DPI: {dpi/1024.0 if dpi else 'not set'}")
            print(f"  System font: {font_name or 'not set'}")
            print(f"  Monospace font: {mono_font or 'not set'}")
            print(f"  Manual DPI override: {os.environ.get('TST_DPI', 'not set')}")

        except Exception as e:
            print(f"Could not retrieve system information: {e}")


    def _on_activate(self, app: TreeStyleTerminalApp) -> None:
        """Called when the application is activated."""
        if not self.window:
            self.window = MainWindow(application=self)

        self._create_initial_session_if_requested()

        self.window.show_all()
        self.window.present()

    def _create_initial_session_if_requested(self) -> None:
        """Create the requested startup session or workspace tree once."""
        workspace_profile = self.args.get("workspace_profile")
        initial_cwd = self.args.get("initial_cwd")
        if self._initial_session_created or not self.window:
            return

        self._initial_session_created = True
        if isinstance(workspace_profile, WorkspaceProfile):
            self.window.session_manager.create_workspace_tree(workspace_profile.root)
        elif initial_cwd:
            self.window.session_manager.new_session(cwd=initial_cwd)


def _resolve_startup_directory(path_value: str, base_dir: Path | None = None) -> str:
    """Resolve and validate a startup directory argument."""
    if not path_value:
        raise argparse.ArgumentTypeError("working directory must not be empty")

    candidate = Path(path_value).expanduser()
    if not candidate.is_absolute():
        candidate = (base_dir or Path.cwd()) / candidate

    resolved = candidate.resolve(strict=False)
    if not resolved.is_dir():
        raise argparse.ArgumentTypeError(
            f"{path_value!r} is not an existing directory"
        )

    return str(resolved)


def _select_initial_cwd(args: argparse.Namespace, parser: argparse.ArgumentParser) -> str | None:
    """Return the requested initial cwd or fail with a clear parser error."""
    requested = [
        value
        for value in (args.working_directory, args.directory)
        if value is not None
    ]
    if not requested:
        return None

    if len(requested) > 1:
        parser.error("provide either a positional directory or --working-directory/--workdir, not both")

    try:
        return _resolve_startup_directory(requested[0])
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))


def _resolve_profile_path(path_value: str, base_dir: Path | None = None) -> str:
    """Resolve and validate a workspace profile path argument."""
    if not path_value:
        raise argparse.ArgumentTypeError("profile path must not be empty")

    candidate = Path(path_value).expanduser()
    if not candidate.is_absolute():
        candidate = (base_dir or Path.cwd()) / candidate

    resolved = candidate.resolve(strict=False)
    if not resolved.is_file():
        raise argparse.ArgumentTypeError(
            f"{path_value!r} is not an existing file"
        )

    return str(resolved)


def parse_arguments(argv: list[str] | None = None):
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
  %(prog)s --log-level info    # Show runtime diagnostics for this launch

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
        help='Suppress the startup message'
    )

    parser.add_argument(
        '--log-level',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='Set runtime diagnostic verbosity (overrides app.log_level in config)'
    )

    parser.add_argument(
        '--working-directory',
        '--workdir',
        dest='working_directory',
        help='Create the first terminal session in this directory'
    )

    parser.add_argument(
        '--profile',
        '-p',
        dest='profile_path',
        type=_resolve_profile_path,
        help='Create the startup session tree from a workspace profile YAML file'
    )

    parser.add_argument(
        'directory',
        nargs='?',
        help='Create the first terminal session in this directory'
    )

    args = parser.parse_args(argv)
    args.initial_cwd = _select_initial_cwd(args, parser)
    if args.profile_path and args.initial_cwd:
        parser.error("provide either --profile/-p or a startup directory, not both")
    return args

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
        except (AttributeError, TypeError):
            try:
                mono_font = settings.get_property("gtk-monospace-font")
            except (AttributeError, TypeError):
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

        # Use improved DPI detection logic (same as CSSLoader)
        if dpi_override:
            effective_dpi = float(dpi_override)
        elif env_dpi:
            effective_dpi = float(env_dpi)
        else:
            # Apply the same improved auto-detection logic as CSSLoader
            system_dpi = dpi / 1024.0 if dpi else None
            monitor_dpi = avg_dpi

            # Choose the more appropriate DPI source with comfort scaling
            if monitor_dpi > 150 and system_dpi and system_dpi < monitor_dpi * 0.8:
                effective_dpi = monitor_dpi
            elif system_dpi and system_dpi > 96:
                effective_dpi = system_dpi
            else:
                effective_dpi = monitor_dpi

        # Calculate base scale factor
        base_scale = effective_dpi / 96.0

        # Apply comfort scaling for better readability on high-DPI displays
        if 240 <= effective_dpi <= 260:  # Calibrated for ~250 DPI displays (MacBook-style)
            # Provide optimal 2.0x scaling for this DPI range
            scale_factor = 2.0
        elif effective_dpi >= 180:  # High-DPI (4K+ monitors)
            scale_factor = max(base_scale, 1.8)
        elif effective_dpi >= 120:  # Medium-high DPI (1440p monitors)
            scale_factor = max(base_scale, 1.25)
        else:
            scale_factor = max(base_scale, 1.0)

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


def configure_logging(log_level: str | None = None) -> None:
    """Configure runtime diagnostics for the GUI application."""
    configured_level = log_level
    if configured_level is None:
        try:
            config_manager.load_config()
            configured_level = config_manager.get("app.log_level", "warning")
        except ConfigError as e:
            logger.error("Configuration error: %s", e)
            raise

    level = getattr(logging, configured_level.upper(), logging.WARNING)
    logging.basicConfig(level=level, format="%(levelname)s:%(name)s:%(message)s", force=True)


def main() -> int:
    """Main entry point for the application."""
    args = parse_arguments()

    # Handle special modes that don't need the full GUI
    if args.test_fonts:
        print_font_test_info(args.dpi)
        return 0

    configure_logging(args.log_level)

    workspace_profile = None
    if args.profile_path:
        try:
            workspace_profile = load_workspace_profile(args.profile_path)
        except WorkspaceProfileError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    # Create application with parsed arguments
    app_args = {
        'dpi': args.dpi,
        'show_info': args.show_info,
        'quiet': args.quiet,
        'log_level': args.log_level,
        'initial_cwd': args.initial_cwd,
        'workspace_profile': workspace_profile,
    }

    # Create filtered argv for GTK (remove our custom arguments)
    gtk_argv = [sys.argv[0]]  # Keep program name

    app = TreeStyleTerminalApp(app_args)
    return app.run(gtk_argv)


if __name__ == "__main__":
    sys.exit(main())
