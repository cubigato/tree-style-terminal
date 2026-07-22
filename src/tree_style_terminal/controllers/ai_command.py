"""GTK controller for AI-assisted shell command drafting."""

from __future__ import annotations

import logging
import threading
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk, GLib, Gtk

from ..ai_command import (
    DEFAULT_HISTORY_LINES,
    AICommandConfig,
    CommandDraftError,
    request_command_draft,
)
from ..config import config_manager
from ..widgets.terminal import VteTerminal
from .session_manager import SessionManager

logger = logging.getLogger(__name__)

AI_ICON_NAME = "ai-sparkles-symbolic"
EXTENDED_HISTORY_LINES = 200
LARGE_HISTORY_LINES = 1000


class AICommandController:
    """Own the AI button, one-shot context menu, request state, and dialogs."""

    def __init__(
        self,
        parent_window: Gtk.ApplicationWindow,
        session_manager: SessionManager,
    ) -> None:
        self.parent_window = parent_window
        self.session_manager = session_manager
        self.pending = False
        self._terminal_available = False
        self.shortcut = config_manager.get(
            "shortcuts.ai_command_draft",
            "<Control><Shift>a",
        )

        icon_root = Path(__file__).parents[1] / "resources" / "icons"
        Gtk.IconTheme.get_default().prepend_search_path(str(icon_root))

        self.button = Gtk.Button()
        self.button.set_image(self._new_icon())
        self.button.set_tooltip_text(self._idle_tooltip())
        self.button.connect("clicked", lambda _button: self.request())
        self.button.connect("button-press-event", self._on_button_press)
        self.button.set_sensitive(False)

        self._setup_context_menu()

    def _new_icon(self) -> Gtk.Image:
        """Return a fresh image widget for the bundled symbolic icon."""
        return Gtk.Image.new_from_icon_name(AI_ICON_NAME, Gtk.IconSize.BUTTON)

    def _idle_tooltip(self) -> str:
        return (
            f"Draft shell command with AI ({self.shortcut}); "
            "right-click for more context"
        )

    def _setup_context_menu(self) -> None:
        """Create one-shot larger-context actions for the AI button."""
        self.context_menu = Gtk.Menu()

        self.extended_context_item = Gtk.MenuItem(
            label=f"Draft with {EXTENDED_HISTORY_LINES} lines"
        )
        self.extended_context_item.connect(
            "activate",
            lambda _item: self.request(history_lines=EXTENDED_HISTORY_LINES),
        )
        self.context_menu.append(self.extended_context_item)

        self.large_context_item = Gtk.MenuItem(
            label=f"Draft with {LARGE_HISTORY_LINES} lines"
        )
        self.large_context_item.connect(
            "activate",
            lambda _item: self.request(history_lines=LARGE_HISTORY_LINES),
        )
        self.context_menu.append(self.large_context_item)

        self.selected_context_item = Gtk.MenuItem(
            label=f"Draft with selected text (up to {LARGE_HISTORY_LINES} lines)"
        )
        self.selected_context_item.connect(
            "activate",
            lambda _item: self.request(use_selected_text=True),
        )
        self.context_menu.append(self.selected_context_item)
        self.context_menu.show_all()

    def _on_button_press(
        self,
        _button: Gtk.Button,
        event: Gdk.EventButton,
    ) -> bool:
        """Open one-shot AI context choices on secondary click."""
        if event.button != Gdk.BUTTON_SECONDARY:
            return False

        terminal_widget = self._get_current_terminal()
        has_selection = bool(terminal_widget and terminal_widget.has_selection())
        self.selected_context_item.set_sensitive(has_selection)

        if hasattr(self.context_menu, "popup_at_pointer"):
            self.context_menu.popup_at_pointer(event)
        else:
            self.context_menu.popup(
                None,
                None,
                None,
                None,
                event.button,
                event.time,
            )
        return True

    def _get_current_terminal(self) -> VteTerminal | None:
        current_session = self.session_manager.current_session
        if current_session is None:
            return None
        return self.session_manager.get_terminal_widget(current_session)

    def request(
        self,
        *,
        history_lines: int = DEFAULT_HISTORY_LINES,
        use_selected_text: bool = False,
    ) -> None:
        """Draft a shell command without blocking GTK or submitting the result."""
        if self.pending:
            return

        config = AICommandConfig.from_values(
            config_manager.get("ai.endpoint", ""),
            config_manager.get("ai.api_key", ""),
            config_manager.get("ai.model", ""),
        )
        if config is None:
            self._show_configuration_help()
            return

        terminal_widget = self._get_current_terminal()
        if terminal_widget is None:
            return

        try:
            history, user_input = terminal_widget.capture_command_draft_context(
                history_lines=0 if use_selected_text else history_lines
            )
            if use_selected_text:
                history = terminal_widget.get_selected_text(LARGE_HISTORY_LINES)
        except Exception as exc:
            logger.warning(
                "Could not capture terminal context for AI drafting: %s",
                type(exc).__name__,
            )
            self._show_error("Could not read the current terminal input.")
            return

        if use_selected_text and not history:
            self._show_error("Select terminal text to use as AI context first.")
            return
        if not user_input.strip():
            self._show_error("Type a short description on the prompt first.")
            return

        self._set_pending(True)
        worker = threading.Thread(
            target=self._run_request,
            args=(config, terminal_widget, history, user_input),
            daemon=True,
        )
        worker.start()

    def _run_request(
        self,
        config: AICommandConfig,
        terminal_widget: VteTerminal,
        history: str,
        user_input: str,
    ) -> None:
        """Perform the network call off the GTK main thread."""
        try:
            command = request_command_draft(config, history, user_input)
        except CommandDraftError as exc:
            logger.warning("AI command drafting failed: %s", type(exc).__name__)
            GLib.idle_add(self._finish_error, str(exc))
            return
        except Exception as exc:
            logger.error("Unexpected AI command drafting failure: %s", type(exc).__name__)
            GLib.idle_add(self._finish_error, "The AI request failed.")
            return

        GLib.idle_add(
            self._finish_success,
            terminal_widget,
            user_input,
            command,
        )

    def _finish_success(
        self,
        terminal_widget: VteTerminal,
        original_input: str,
        command: str,
    ) -> bool:
        """Replace unchanged input with the completed draft on the GTK thread."""
        self._set_pending(False)
        try:
            _history, current_input = terminal_widget.capture_command_draft_context()
            if current_input != original_input:
                self._show_error(
                    "The terminal input changed while the AI request was running. "
                    "Nothing was replaced."
                )
                return False
            terminal_widget.replace_current_input(command)
        except Exception as exc:
            logger.warning("Could not insert AI command draft: %s", type(exc).__name__)
            self._show_error("Could not replace the current terminal input.")
        return False

    def _finish_error(self, message: str) -> bool:
        """Restore controls and report a sanitized request error on the GTK thread."""
        self._set_pending(False)
        self._show_error(message)
        return False

    def _set_pending(self, pending: bool) -> None:
        """Track request state and show progress on the AI button."""
        self.pending = pending
        if pending:
            spinner = Gtk.Spinner()
            spinner.start()
            spinner.show()
            self.button.set_image(spinner)
            self.button.set_tooltip_text("Drafting shell command with AI…")
        else:
            self.button.set_image(self._new_icon())
            self.button.set_tooltip_text(self._idle_tooltip())
        self._update_button_sensitivity()

    def set_terminal_available(self, available: bool) -> None:
        """Update whether the button may be used for the current session state."""
        self._terminal_available = available
        self._update_button_sensitivity()

    def _update_button_sensitivity(self) -> None:
        self.button.set_sensitive(self._terminal_available and not self.pending)

    def _show_configuration_help(self) -> None:
        """Explain how to enable AI drafting without displaying credential values."""
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text="AI command drafting is not configured",
        )
        dialog.format_secondary_text(
            f"Add endpoint, api_key, and model under 'ai' in\n"
            f"{config_manager.get_config_path()}\n\n"
            "See CONFIG.md for an example."
        )
        dialog.run()
        dialog.destroy()

    def _show_error(self, message: str) -> None:
        """Show an AI drafting error without changing terminal input."""
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Could not draft shell command",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
