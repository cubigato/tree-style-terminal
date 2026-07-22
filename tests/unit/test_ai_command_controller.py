"""Tests for the GTK controller around AI command drafting."""

from unittest.mock import Mock, patch

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from tree_style_terminal.ai_command import AICommandConfig, CommandDraftError
from tree_style_terminal.config import config_manager
from tree_style_terminal.main import MainWindow, TreeStyleTerminalApp
from tree_style_terminal.models.session import TerminalSession


def create_window_with_terminal(terminal=None):
    """Return a window whose current session resolves to the supplied terminal."""
    window = MainWindow(application=TreeStyleTerminalApp())
    session = TerminalSession(pid=1, pty_fd=1, cwd="/tmp")
    terminal = terminal or Mock()
    window.session_tree.add_node(session)
    window.session_manager.current_session = session
    window.session_manager._session_terminals[session] = terminal
    window._update_button_states()
    return window, terminal


def configured_values(key, default=None):
    values = {
        "ai.endpoint": "https://example.test/v1/chat/completions",
        "ai.api_key": "secret",
        "ai.model": "model",
    }
    return values.get(key, default)


def test_button_uses_bundled_symbolic_icon_and_tracks_terminal_state():
    window = MainWindow(application=TreeStyleTerminalApp())
    controller = window.ai_command_controller
    icon_name, _size = controller.button.get_image().get_icon_name()

    assert icon_name == "ai-sparkles-symbolic"
    icon_theme = Gtk.IconTheme.get_default()
    assert icon_theme.has_icon("ai-sparkles-symbolic")
    icon_info = icon_theme.lookup_icon("ai-sparkles-symbolic", 16, 0)
    assert icon_info is not None
    assert icon_info.is_symbolic()
    assert controller.button.get_sensitive() is False

    window, _terminal = create_window_with_terminal()

    assert window.ai_command_controller.button.get_sensitive() is True


def test_context_menu_offers_one_shot_context_sizes():
    window = MainWindow(application=TreeStyleTerminalApp())
    controller = window.ai_command_controller
    labels = [item.get_label() for item in controller.context_menu.get_children()]

    assert labels == [
        "Draft with 200 lines",
        "Draft with 1000 lines",
        "Draft with selected text (up to 1000 lines)",
    ]

    with patch.object(controller, "request") as request:
        controller.extended_context_item.emit("activate")
        controller.large_context_item.emit("activate")
        controller.selected_context_item.emit("activate")

    assert [entry.kwargs for entry in request.call_args_list] == [
        {"history_lines": 200},
        {"history_lines": 1000},
        {"use_selected_text": True},
    ]


def test_secondary_click_enables_selected_context_when_available():
    terminal = Mock()
    terminal.has_selection.return_value = True
    window, terminal = create_window_with_terminal(terminal)
    controller = window.ai_command_controller
    event = Mock(button=Gdk.BUTTON_SECONDARY)

    with patch.object(controller.context_menu, "popup_at_pointer") as popup:
        handled = controller._on_button_press(controller.button, event)

    assert handled is True
    assert controller.selected_context_item.get_sensitive() is True
    popup.assert_called_once_with(event)


def test_unconfigured_action_shows_help_without_starting_request():
    window = MainWindow(application=TreeStyleTerminalApp())
    controller = window.ai_command_controller

    def empty_ai_values(key, default=None):
        return "" if key.startswith("ai.") else default

    with (
        patch.object(config_manager, "get", side_effect=empty_ai_values),
        patch.object(controller, "_show_configuration_help") as show_help,
        patch("tree_style_terminal.controllers.ai_command.threading.Thread") as thread,
    ):
        controller.request()

    show_help.assert_called_once_with()
    thread.assert_not_called()


def test_configured_action_starts_background_worker_and_spinner():
    terminal = Mock()
    terminal.capture_command_draft_context.return_value = ("history", "show files")
    window, _terminal = create_window_with_terminal(terminal)
    controller = window.ai_command_controller

    with (
        patch.object(config_manager, "get", side_effect=configured_values),
        patch(
            "tree_style_terminal.controllers.ai_command.threading.Thread"
        ) as thread_class,
        patch("tree_style_terminal.controllers.ai_command.request_command_draft") as request,
    ):
        controller.request()

    thread_class.return_value.start.assert_called_once_with()
    request.assert_not_called()
    assert controller.pending is True
    spinner = controller.button.get_image()
    assert isinstance(spinner, Gtk.Spinner)
    assert spinner.get_property("active") is True
    assert controller.button.get_tooltip_text() == "Drafting shell command with AI…"


def test_selected_text_replaces_recent_history_for_one_request():
    terminal = Mock()
    terminal.capture_command_draft_context.return_value = ("", "explain the error")
    terminal.get_selected_text.return_value = "selected command\nselected error"
    window, _terminal = create_window_with_terminal(terminal)
    controller = window.ai_command_controller

    with (
        patch.object(config_manager, "get", side_effect=configured_values),
        patch(
            "tree_style_terminal.controllers.ai_command.threading.Thread"
        ) as thread_class,
    ):
        controller.request(use_selected_text=True)

    terminal.capture_command_draft_context.assert_called_once_with(history_lines=0)
    terminal.get_selected_text.assert_called_once_with(1000)
    worker_args = thread_class.call_args.kwargs["args"]
    assert worker_args[2:] == (
        "selected command\nselected error",
        "explain the error",
    )


def test_progress_indicator_restores_sparkle_icon_after_request():
    window = MainWindow(application=TreeStyleTerminalApp())
    controller = window.ai_command_controller

    controller._set_pending(True)
    controller._set_pending(False)

    image = controller.button.get_image()
    icon_name, _size = image.get_icon_name()
    assert icon_name == "ai-sparkles-symbolic"
    assert controller.button.get_tooltip_text().startswith(
        "Draft shell command with AI ("
    )


def test_request_result_replaces_unchanged_input_without_submit():
    window = MainWindow(application=TreeStyleTerminalApp())
    controller = window.ai_command_controller
    terminal = Mock()
    terminal.capture_command_draft_context.return_value = (
        "recent output",
        "show changes",
    )
    config = AICommandConfig("https://example.test", "secret", "model")

    with (
        patch(
            "tree_style_terminal.controllers.ai_command.request_command_draft",
            return_value="git status",
        ),
        patch(
            "tree_style_terminal.controllers.ai_command.GLib.idle_add",
            side_effect=lambda function, *args: function(*args),
        ),
    ):
        controller._run_request(config, terminal, "recent output", "show changes")

    terminal.replace_current_input.assert_called_once_with("git status")
    assert controller.pending is False


def test_success_leaves_changed_terminal_input_untouched():
    window = MainWindow(application=TreeStyleTerminalApp())
    controller = window.ai_command_controller
    terminal = Mock()
    terminal.capture_command_draft_context.return_value = ("history", "new text")

    with patch.object(controller, "_show_error") as show_error:
        controller._finish_success(terminal, "old text", "git status")

    terminal.replace_current_input.assert_not_called()
    assert "input changed" in show_error.call_args.args[0]


def test_request_error_leaves_terminal_input_untouched():
    window = MainWindow(application=TreeStyleTerminalApp())
    controller = window.ai_command_controller
    terminal = Mock()
    config = AICommandConfig("https://example.test", "secret", "model")

    with (
        patch(
            "tree_style_terminal.controllers.ai_command.request_command_draft",
            side_effect=CommandDraftError("Invalid response."),
        ),
        patch(
            "tree_style_terminal.controllers.ai_command.GLib.idle_add",
            side_effect=lambda function, *args: function(*args),
        ),
        patch.object(controller, "_show_error") as show_error,
    ):
        controller._run_request(config, terminal, "history", "show files")

    terminal.replace_current_input.assert_not_called()
    show_error.assert_called_once_with("Invalid response.")
