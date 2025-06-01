"""
Shortcut controller for session management actions.

Provides a central registry for GTK actions and keyboard shortcuts,
coordinating between user input and SessionManager operations.
"""

import logging
from collections.abc import Callable
from typing import Optional

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gio, GLib, Gtk, Gdk  # noqa: E402

from .session_manager import SessionManager  # noqa: E402

logger = logging.getLogger(__name__)


class ShortcutController:
    """
    Central registry for application actions and keyboard shortcuts.

    Manages the mapping between user input (keyboard shortcuts, menu items)
    and session management operations via SessionManager.
    """

    def __init__(self, session_manager: SessionManager, main_window: Optional[Gtk.ApplicationWindow] = None):
        """
        Initialize the shortcut controller.

        Args:
            session_manager: The SessionManager to control
            main_window: The main window to add actions and shortcuts to
        """
        self.session_manager = session_manager
        self.main_window = main_window
        self._actions: dict[str, Gio.SimpleAction] = {}
        self._accel_group: Optional[Gtk.AccelGroup] = None
        
        self._setup_actions()
        
        if main_window:
            self._setup_shortcuts()
        
        logger.debug("ShortcutController initialized")

    def _setup_actions(self) -> None:
        """Set up the core session management actions."""
        # Action: Create new child session
        self._create_action(
            name="new_child",
            callback=self._on_new_child,
            enabled=True
        )

        # Action: Create new sibling session
        self._create_action(
            name="new_sibling",
            callback=self._on_new_sibling,
            enabled=True
        )

        # Action: Close current session
        self._create_action(
            name="close_session",
            callback=self._on_close_session,
            enabled=True
        )

        # Additional navigation actions
        self._create_action(
            name="toggle_sidebar",
            callback=self._on_toggle_sidebar,
            enabled=True
        )

        self._create_action(
            name="focus_terminal",
            callback=self._on_focus_terminal,
            enabled=True
        )

        self._create_action(
            name="focus_sidebar",
            callback=self._on_focus_sidebar,
            enabled=True
        )

        self._create_action(
            name="next_session",
            callback=self._on_next_session,
            enabled=True
        )

        self._create_action(
            name="prev_session",
            callback=self._on_prev_session,
            enabled=True
        )

    def _create_action(self, name: str, callback: Callable, enabled: bool = True) -> None:
        """
        Create and register a new action.

        Args:
            name: Action name/identifier
            callback: Function to call when action is activated
            enabled: Whether the action is initially enabled
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        action.set_enabled(enabled)
        self._actions[name] = action
        logger.debug(f"Created action: {name}")

    def _on_new_child(self, action: Gio.SimpleAction, parameter: GLib.Variant) -> None:
        """Handle new_child action activation."""
        try:
            session = self.session_manager.new_child()
            if session:
                logger.info(f"Created new child session: {session.title}")
            else:
                logger.warning("Failed to create new child session")
        except Exception as e:
            logger.error(f"Error creating child session: {e}")

    def _on_new_sibling(self, action: Gio.SimpleAction, parameter: GLib.Variant) -> None:
        """Handle new_sibling action activation."""
        try:
            session = self.session_manager.new_sibling()
            if session:
                logger.info(f"Created new sibling session: {session.title}")
            else:
                logger.warning("Failed to create new sibling session")
        except Exception as e:
            logger.error(f"Error creating sibling session: {e}")

    def _on_close_session(self, action: Gio.SimpleAction, parameter: GLib.Variant) -> None:
        """Handle close_session action activation."""
        try:
            if self.session_manager.current_session:
                session_title = self.session_manager.current_session.title
                # Check if this is the last session
                all_sessions = self.session_manager.get_all_sessions()
                if len(all_sessions) <= 1:
                    # Last session - close application
                    if self.main_window:
                        self.main_window.get_application().quit()
                else:
                    self.session_manager.close_current_session()
                    logger.info(f"Closed session: {session_title}")
            else:
                logger.warning("No current session to close")
        except Exception as e:
            logger.error(f"Error closing session: {e}")

    def _on_toggle_sidebar(self, action: Gio.SimpleAction, parameter: GLib.Variant) -> None:
        """Handle toggle_sidebar action activation."""
        try:
            if self.main_window and hasattr(self.main_window, 'toggle_sidebar'):
                self.main_window.toggle_sidebar()
            elif self.main_window and hasattr(self.main_window, 'sidebar_revealer'):
                current_state = self.main_window.sidebar_revealer.get_reveal_child()
                self.main_window.sidebar_revealer.set_reveal_child(not current_state)
                logger.debug(f"Sidebar {'shown' if not current_state else 'hidden'}")
        except Exception as e:
            logger.error(f"Error toggling sidebar: {e}")

    def _on_focus_terminal(self, action: Gio.SimpleAction, parameter: GLib.Variant) -> None:
        """Handle focus_terminal action activation."""
        try:
            if self.session_manager.current_session:
                terminal_widget = self.session_manager.get_terminal_widget(self.session_manager.current_session)
                if terminal_widget and hasattr(terminal_widget, 'grab_focus'):
                    terminal_widget.grab_focus()
                    logger.debug("Focused terminal")
        except Exception as e:
            logger.error(f"Error focusing terminal: {e}")

    def _on_focus_sidebar(self, action: Gio.SimpleAction, parameter: GLib.Variant) -> None:
        """Handle focus_sidebar action activation."""
        try:
            if self.main_window and hasattr(self.main_window, 'session_sidebar'):
                if hasattr(self.main_window.session_sidebar, 'grab_focus'):
                    self.main_window.session_sidebar.grab_focus()
                    logger.debug("Focused sidebar")
        except Exception as e:
            logger.error(f"Error focusing sidebar: {e}")

    def _on_next_session(self, action: Gio.SimpleAction, parameter: GLib.Variant) -> None:
        """Handle next_session action activation."""
        try:
            if hasattr(self.session_manager, 'select_next_session'):
                self.session_manager.select_next_session()
            else:
                # Simple fallback implementation
                all_sessions = self.session_manager.get_all_sessions()
                if len(all_sessions) > 1 and self.session_manager.current_session:
                    current_index = all_sessions.index(self.session_manager.current_session)
                    next_index = (current_index + 1) % len(all_sessions)
                    self.session_manager.select_session(all_sessions[next_index])
                    logger.debug("Selected next session")
        except Exception as e:
            logger.error(f"Error selecting next session: {e}")

    def _on_prev_session(self, action: Gio.SimpleAction, parameter: GLib.Variant) -> None:
        """Handle prev_session action activation."""
        try:
            if hasattr(self.session_manager, 'select_previous_session'):
                self.session_manager.select_previous_session()
            else:
                # Simple fallback implementation
                all_sessions = self.session_manager.get_all_sessions()
                if len(all_sessions) > 1 and self.session_manager.current_session:
                    current_index = all_sessions.index(self.session_manager.current_session)
                    prev_index = (current_index - 1) % len(all_sessions)
                    self.session_manager.select_session(all_sessions[prev_index])
                    logger.debug("Selected previous session")
        except Exception as e:
            logger.error(f"Error selecting previous session: {e}")

    def get_action(self, name: str) -> Gio.SimpleAction | None:
        """
        Get an action by name.

        Args:
            name: Action name

        Returns:
            The action if found, None otherwise
        """
        return self._actions.get(name)

    def enable_action(self, name: str, enabled: bool = True) -> None:
        """
        Enable or disable an action.

        Args:
            name: Action name
            enabled: Whether to enable the action
        """
        action = self._actions.get(name)
        if action:
            action.set_enabled(enabled)
            logger.debug(f"Action {name} {'enabled' if enabled else 'disabled'}")
        else:
            logger.warning(f"Action not found: {name}")

    def add_actions_to_widget(self, widget: Gtk.Widget) -> None:
        """
        Add all actions to a GTK widget's action map.

        Args:
            widget: Widget to add actions to (usually a Window or Application)
        """
        if hasattr(widget, 'add_action'):
            for name, action in self._actions.items():
                widget.add_action(action)
                logger.debug(f"Added action {name} to {widget.__class__.__name__}")
        else:
            logger.warning(f"Widget {widget.__class__.__name__} does not support actions")

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts using AccelGroup."""
        if not self.main_window:
            logger.warning("No main window provided, cannot setup shortcuts")
            return

        # Create accelerator group
        self._accel_group = Gtk.AccelGroup()
        self.main_window.add_accel_group(self._accel_group)

        # Define shortcut mappings
        shortcuts = [
            # Core session management - as requested
            ('<Control><Shift>t', 'new_sibling'),
            ('<Control><Alt>t', 'new_child'),
            ('<Control>q', 'close_session'),
            
            # Navigation & UI
            ('F9', 'toggle_sidebar'),
            ('<Control><Shift>o', 'toggle_sidebar'),  # Alternative
            ('<Control><Shift>f', 'focus_terminal'),
            ('<Control><Shift>s', 'focus_sidebar'),
            
            # Session navigation
            ('<Control><Shift>Right', 'next_session'),
            ('<Control><Shift>Left', 'prev_session'),
            ('<Alt>Right', 'next_session'),  # Alternative
            ('<Alt>Left', 'prev_session'),   # Alternative
        ]

        # Add actions to main window first
        self.add_actions_to_widget(self.main_window)

        # Register keyboard shortcuts
        for accel_key, action_name in shortcuts:
            try:
                # Parse the accelerator
                key, mods = Gtk.accelerator_parse(accel_key)
                if key == 0:
                    logger.warning(f"Invalid accelerator: {accel_key}")
                    continue

                # Connect the accelerator to the action
                action = self._actions.get(action_name)
                if action:
                    self._accel_group.connect(
                        key, mods, Gtk.AccelFlags.VISIBLE,
                        lambda accel_group, acceleratable, keyval, modifier, action=action: action.activate(None)
                    )
                    logger.debug(f"Registered shortcut: {accel_key} -> {action_name}")
                else:
                    logger.warning(f"Action not found: {action_name}")

            except Exception as e:
                logger.error(f"Failed to register shortcut {accel_key} -> {action_name}: {e}")

    def set_main_window(self, main_window: Gtk.ApplicationWindow) -> None:
        """
        Set the main window and setup shortcuts.
        
        Args:
            main_window: The main window to add actions and shortcuts to
        """
        self.main_window = main_window
        self._setup_shortcuts()

    def update_action_states(self) -> None:
        """Update action enabled states based on current session state."""
        has_current_session = self.session_manager.current_session is not None

        # new_child and new_sibling are always available
        self.enable_action("new_child", True)
        self.enable_action("new_sibling", True)

        # close_session requires a current session
        self.enable_action("close_session", has_current_session)

        # Navigation actions require multiple sessions
        has_multiple_sessions = len(self.session_manager.get_all_sessions()) > 1
        self.enable_action("next_session", has_multiple_sessions)
        self.enable_action("prev_session", has_multiple_sessions)
