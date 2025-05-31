"""
Shortcut controller for session management actions.

Provides a central registry for GTK actions and keyboard shortcuts,
coordinating between user input and SessionManager operations.
"""

import logging
from collections.abc import Callable

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib, Gtk  # noqa: E402

from .session_manager import SessionManager  # noqa: E402

logger = logging.getLogger(__name__)


class ShortcutController:
    """
    Central registry for application actions and keyboard shortcuts.

    Manages the mapping between user input (keyboard shortcuts, menu items)
    and session management operations via SessionManager.
    """

    def __init__(self, session_manager: SessionManager):
        """
        Initialize the shortcut controller.

        Args:
            session_manager: The SessionManager to control
        """
        self.session_manager = session_manager
        self._actions: dict[str, Gio.SimpleAction] = {}
        self._setup_actions()
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
                self.session_manager.close_current_session()
                logger.info(f"Closed session: {session_title}")
            else:
                logger.warning("No current session to close")
        except Exception as e:
            logger.error(f"Error closing session: {e}")

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

    def update_action_states(self) -> None:
        """Update action enabled states based on current session state."""
        has_current_session = self.session_manager.current_session is not None

        # new_child and new_sibling are always available
        self.enable_action("new_child", True)
        self.enable_action("new_sibling", True)

        # close_session requires a current session
        self.enable_action("close_session", has_current_session)
