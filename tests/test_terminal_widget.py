"""VTE terminal widget tests for tree-style-terminal."""

import logging
import os
import re
from unittest.mock import Mock, patch


def test_vte_terminal_creation():
    """Test that VteTerminal widget can be instantiated."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    assert terminal is not None
    assert hasattr(terminal, 'terminal')  # VTE widget exists
    assert hasattr(terminal, 'set_font_size')
    assert hasattr(terminal, 'set_scrollback_length')
    assert hasattr(terminal, 'spawn_shell')
    assert hasattr(terminal, '_context_menu')


def test_font_size_configuration():
    """Test set_font_size() doesn't crash with valid inputs."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()

    # Test valid font sizes
    terminal.set_font_size(10)
    terminal.set_font_size(12)
    terminal.set_font_size(14)
    terminal.set_font_size(16)

    # Should not raise exceptions


def test_scrollback_configuration():
    """Test set_scrollback_length() doesn't crash with valid inputs."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()

    # Test valid scrollback lengths
    terminal.set_scrollback_length(1000)
    terminal.set_scrollback_length(5000)
    terminal.set_scrollback_length(10000)
    terminal.set_scrollback_length(0)  # Should handle zero

    # Should not raise exceptions


def test_shell_argv_logic():
    """Test shell command building logic (without actual spawning)."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()

    # Test that spawn_shell method exists and can be called with different parameters
    # We don't actually spawn to avoid creating real processes in tests

    # Test with default shell (should use $SHELL or /bin/bash)
    original_shell = os.environ.get('SHELL')

    try:
        # Set a known shell for testing
        os.environ['SHELL'] = '/bin/bash'

        # These should not crash during parameter processing
        # Note: We're not actually calling spawn_shell() as that would create real processes
        assert hasattr(terminal, 'spawn_shell')
        assert callable(terminal.spawn_shell)

    finally:
        # Restore original shell
        if original_shell:
            os.environ['SHELL'] = original_shell
        elif 'SHELL' in os.environ:
            del os.environ['SHELL']


def test_terminal_properties():
    """Test that terminal widget has expected properties."""
    from tree_style_terminal.widgets.terminal import (
        TERMINAL_LEFT_EDGE_MARGIN_PX,
        VteTerminal,
    )

    terminal = VteTerminal()

    # Check initial state
    assert terminal.pid is None
    assert terminal.pty_fd is None

    # Check that VTE terminal is properly embedded
    assert terminal.terminal is not None
    assert terminal.scrolled_window is not None
    assert terminal.get_margin_start() == TERMINAL_LEFT_EDGE_MARGIN_PX


def test_context_menu_labels_are_english():
    """Test terminal context menu labels stay consistent with the English UI."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()

    assert terminal._open_target_menu_item.get_label() == "Open Link"
    assert terminal._copy_target_menu_item.get_label() == "Copy Link"
    assert terminal._copy_menu_item.get_label() == "Copy"
    assert terminal._paste_menu_item.get_label() == "Paste"
    assert terminal._select_all_menu_item.get_label() == "Select All"


def test_terminal_methods_exist():
    """Test that all expected methods exist on the terminal widget."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()

    # Check that all expected methods exist
    expected_methods = [
        'spawn_shell',
        'set_font_size',
        'set_scrollback_length',
        'show_search',
        'hide_search',
        'search_next',
        'search_previous',
        'copy_clipboard',
        'paste_clipboard',
        'select_all',
        'has_selection',
        '_paste_dropped_text',
        '_target_from_event',
        '_target_to_uri',
        '_update_target_menu_labels',
        'get_window_title',
        'get_current_directory',
        'close'
    ]

    for method_name in expected_methods:
        assert hasattr(terminal, method_name), f"Missing method: {method_name}"
        assert callable(getattr(terminal, method_name)), f"Method not callable: {method_name}"


def test_get_current_directory_uses_vte_uri(tmp_path):
    """Test current directory is read from VTE's tracked file URI."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()
    terminal.terminal.get_current_directory_uri.return_value = tmp_path.as_uri()

    assert terminal.get_current_directory() == str(tmp_path)


def test_get_current_directory_falls_back_to_spawn_cwd():
    """Test current directory falls back when VTE has no tracked URI."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()
    terminal.terminal.get_current_directory_uri.return_value = None
    terminal._last_spawn_cwd = "/fallback"

    assert terminal.get_current_directory() == "/fallback"


def test_get_current_directory_uses_child_process_cwd(tmp_path):
    """Test current directory falls back to the spawned shell process cwd."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()
    terminal.terminal.get_current_directory_uri.return_value = None
    terminal.pid = os.getpid()

    assert terminal.get_current_directory() == os.getcwd()


def test_spawn_complete_stores_child_pid():
    """Test spawn completion records the child process id returned by VTE."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal._spawn_argv = ["/bin/bash"]
    terminal._spawn_cwd = "/tmp"

    pty = Mock()
    pty.spawn_finish.return_value = (True, 12345)
    pty.get_fd.return_value = 99

    terminal._on_spawn_complete(pty, Mock())

    assert terminal.pid == 12345
    assert terminal.pty_fd == 99


def test_terminal_search_builds_fuzzy_case_insensitive_pattern():
    """Test fuzzy search is case-insensitive and separator tolerant."""
    from tree_style_terminal.widgets.terminal import build_terminal_search_pattern

    assert build_terminal_search_pattern("my-command", True) == (
        r"(?i)my[-_\s]*command"
    )
    assert build_terminal_search_pattern("command --flag", True) == (
        r"(?i)command[-_\s]*flag"
    )


def test_terminal_search_fuzzy_pattern_matches_common_separator_differences():
    """Test fuzzy search handles common command separator differences."""
    from tree_style_terminal.widgets.terminal import build_terminal_search_pattern

    assert re.search(build_terminal_search_pattern("x alg", True), "x-algorithm")
    assert re.search(build_terminal_search_pattern("x -alg", True), "x-algorithm")
    assert re.search(build_terminal_search_pattern("cat -help", True), "cat --help")


def test_terminal_search_fuzzy_pattern_remains_conservative():
    """Test fuzzy search does not add broad approximate matching."""
    from tree_style_terminal.widgets.terminal import build_terminal_search_pattern

    pattern = build_terminal_search_pattern("deploy app", True)

    assert pattern == r"(?i)deploy[-_\s]*app"
    assert ".*" not in pattern
    assert build_terminal_search_pattern("--", True) == r"\-\-"


def test_terminal_search_exact_pattern_preserves_literal_behavior():
    """Test exact search keeps the previous literal, case-sensitive behavior."""
    from tree_style_terminal.widgets.terminal import build_terminal_search_pattern

    assert build_terminal_search_pattern("a.b[", False) == r"a\.b\["
    assert build_terminal_search_pattern("my-command", False) == r"my\-command"


def test_terminal_search_sets_fuzzy_regex_by_default():
    """Test terminal search configures VTE search with fuzzy text by default."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()

    terminal._set_search_text("a.b[")

    terminal.terminal.search_set_regex.assert_called_once()
    terminal.terminal.search_set_wrap_around.assert_called_once_with(True)
    terminal.terminal.search_find_next.assert_called_once()
    terminal.terminal.search_find_previous.assert_not_called()


def test_terminal_search_falls_back_to_previous_when_next_misses():
    """Test incremental search can recover when VTE's next position skips a match."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()
    terminal.terminal.search_find_next.return_value = False

    terminal._set_search_text("cat -help")

    terminal.terminal.search_find_next.assert_called_once()
    terminal.terminal.search_find_previous.assert_called_once()


def test_terminal_search_can_use_exact_mode():
    """Test disabling fuzzy search uses exact literal matching."""
    from tree_style_terminal.widgets import terminal as terminal_module
    from tree_style_terminal.widgets.terminal import (
        VTE_REGEX_COMPILE_FLAGS,
        VteTerminal,
    )

    terminal = VteTerminal()
    terminal.terminal = Mock()
    regex = Mock()

    terminal.search_fuzzy_toggle.set_active(False)
    terminal.terminal.reset_mock()
    with patch.object(terminal_module.Vte.Regex, "new_for_search", return_value=regex) as new_regex:
        terminal._set_search_text("my-command")

    new_regex.assert_called_once_with(r"my\-command", -1, VTE_REGEX_COMPILE_FLAGS)
    terminal.terminal.search_set_regex.assert_called_once_with(regex, 0)


def test_terminal_search_opens_in_fuzzy_mode():
    """Test opening terminal search defaults to fuzzy mode."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()

    terminal.search_fuzzy_toggle.set_active(False)
    terminal.show_search()

    assert terminal.search_fuzzy_toggle.get_active() is True


def test_terminal_search_clear_removes_vte_regex():
    """Test clearing search removes VTE search state."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()

    terminal._set_search_text("")

    terminal.terminal.search_set_regex.assert_called_once_with(None, 0)


def test_terminal_search_navigation_uses_vte_api():
    """Test search navigation delegates to VTE."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()

    assert terminal.search_next() is True
    assert terminal.search_previous() is True

    terminal.terminal.search_find_next.assert_called_once()
    terminal.terminal.search_find_previous.assert_called_once()


def test_terminal_enables_vte_hyperlinks():
    """Test OSC 8 hyperlinks are enabled on the VTE widget."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()

    assert terminal.terminal.get_allow_hyperlink() is True


def test_terminal_hyperlink_setup_failures_are_warnings(caplog):
    """Test terminal hyperlink setup failures are visible above debug logging."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()
    terminal.terminal.set_allow_hyperlink.side_effect = RuntimeError("no hyperlinks")

    with caplog.at_level(logging.WARNING):
        terminal._configure_hyperlinks()

    assert "Failed to enable terminal hyperlinks" in caplog.text


def test_terminal_hyperlink_match_regex_uses_vte_compile_flags():
    """Test hyperlink regexes are compiled with flags VTE expects."""
    from tree_style_terminal.widgets import terminal as terminal_module
    from tree_style_terminal.widgets.terminal import (
        VTE_REGEX_COMPILE_FLAGS,
        VteTerminal,
    )

    terminal = VteTerminal()
    terminal.terminal = Mock()
    regex = Mock()

    with patch.object(terminal_module.Vte.Regex, "new_for_match", return_value=regex) as new_regex:
        terminal._configure_hyperlinks()

    assert new_regex.call_count == 2
    assert all(call.args[2] == VTE_REGEX_COMPILE_FLAGS for call in new_regex.call_args_list)
    assert terminal.terminal.match_add_regex.call_count == 2


def test_context_target_prefers_osc8_hyperlink():
    """Test native VTE hyperlinks are used before plain text matches."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()
    terminal.terminal.hyperlink_check_event.return_value = "https://example.test/docs"
    event = Mock()

    target = terminal._target_from_event(event)

    assert target == "https://example.test/docs"
    terminal.terminal.match_check_event.assert_not_called()


def test_context_target_falls_back_to_text_match_and_trims_punctuation():
    """Test plain URL/path matches are cleaned for context actions."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()
    terminal.terminal.hyperlink_check_event.return_value = None
    terminal.terminal.match_check_event.return_value = ("https://example.test/path),", 1)
    event = Mock()

    assert terminal._target_from_event(event) == "https://example.test/path"


def test_context_target_to_uri_preserves_url():
    """Test URLs are passed to GTK as-is."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()

    assert terminal._target_to_uri("https://example.test/path") == "https://example.test/path"


def test_context_target_to_uri_resolves_relative_file_path(tmp_path):
    """Test detected file paths are opened relative to terminal cwd."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    with patch.object(terminal, "get_current_directory", return_value=str(tmp_path)):
        uri = terminal._target_to_uri("./README.md")

    assert uri == (tmp_path / "README.md").as_uri()


def test_context_target_menu_labels_distinguish_paths():
    """Test path context actions use path-specific labels."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()

    terminal._update_target_menu_labels("./README.md")

    assert terminal._open_target_menu_item.get_label() == "Open File"
    assert terminal._copy_target_menu_item.get_label() == "Copy Path"


def test_copy_context_target_uses_clipboard():
    """Test the link context copy action writes the target to the clipboard."""
    from tree_style_terminal.widgets import terminal as terminal_module
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal._context_menu_target = "https://example.test"
    clipboard = Mock()

    with patch.object(terminal_module.Gtk.Clipboard, "get", return_value=clipboard):
        terminal._copy_context_target()

    clipboard.set_text.assert_called_once_with("https://example.test", -1)
    clipboard.store.assert_called_once()


def test_open_context_target_uses_gtk_show_uri():
    """Test the link context open action delegates to GTK URI opening."""
    from tree_style_terminal.widgets import terminal as terminal_module
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal._context_menu_target = "https://example.test"

    with patch.object(terminal_module.Gtk, "show_uri_on_window") as mock_show_uri:
        terminal._open_context_target()

    mock_show_uri.assert_called_once()
    assert mock_show_uri.call_args.args[1] == "https://example.test"


def test_primary_click_does_not_show_context_menu_or_affect_selection():
    """Test normal terminal clicks are left for VTE selection handling."""
    from gi.repository import Gdk

    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    event = Mock()
    event.type = Gdk.EventType.BUTTON_PRESS
    event.button = Gdk.BUTTON_PRIMARY

    with patch.object(terminal, "_popup_context_menu") as mock_popup:
        handled = terminal._on_button_press(terminal.terminal, event)

    mock_popup.assert_not_called()
    assert handled is False


def test_terminal_search_escape_closes_search():
    """Test Escape closes the terminal search UI."""
    from gi.repository import Gdk

    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    event = Mock()
    event.keyval = Gdk.KEY_Escape

    with patch.object(terminal, "hide_search") as mock_hide_search:
        handled = terminal._on_search_key_press(terminal.search_entry, event)

    mock_hide_search.assert_called_once()
    assert handled is True


def test_terminal_search_enter_moves_to_next_match():
    """Test Enter moves to the next terminal search match."""
    from gi.repository import Gdk

    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    event = Mock()
    event.keyval = Gdk.KEY_Return
    event.state = 0

    with (
        patch.object(terminal, "search_next") as mock_search_next,
        patch.object(terminal, "search_previous") as mock_search_previous,
    ):
        handled = terminal._on_search_key_press(terminal.search_entry, event)

    mock_search_next.assert_called_once()
    mock_search_previous.assert_not_called()
    assert handled is True


def test_terminal_search_shift_enter_moves_to_previous_match():
    """Test Shift+Enter moves to the previous terminal search match."""
    from gi.repository import Gdk

    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    event = Mock()
    event.keyval = Gdk.KEY_Return
    event.state = Gdk.ModifierType.SHIFT_MASK

    with (
        patch.object(terminal, "search_next") as mock_search_next,
        patch.object(terminal, "search_previous") as mock_search_previous,
    ):
        handled = terminal._on_search_key_press(terminal.search_entry, event)

    mock_search_next.assert_not_called()
    mock_search_previous.assert_called_once()
    assert handled is True


def test_terminal_search_non_escape_key_is_not_handled():
    """Test non-Escape keys keep normal entry handling."""
    from gi.repository import Gdk

    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    event = Mock()
    event.keyval = Gdk.KEY_a

    with patch.object(terminal, "hide_search") as mock_hide_search:
        handled = terminal._on_search_key_press(terminal.search_entry, event)

    mock_hide_search.assert_not_called()
    assert handled is False


def test_paste_dropped_text_uses_vte_paste_text():
    """Test dropped text is inserted through VTE's paste API."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()
    selection_data = Mock()
    selection_data.get_text.return_value = "https://example.test/ä path"

    handled = terminal._paste_dropped_text(selection_data)

    assert handled is True
    terminal.terminal.paste_text.assert_called_once_with("https://example.test/ä path")


def test_paste_dropped_text_ignores_non_text_payload():
    """Test non-text drops are ignored without writing terminal input."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    terminal.terminal = Mock()
    selection_data = Mock()
    selection_data.get_text.return_value = None

    handled = terminal._paste_dropped_text(selection_data)

    assert handled is False
    terminal.terminal.paste_text.assert_not_called()


def test_drag_data_received_finishes_context_with_result():
    """Test GTK drop context is completed after handling a text drop."""
    from tree_style_terminal.widgets import terminal as terminal_module
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    context = Mock()
    selection_data = Mock()

    with (
        patch.object(terminal, "_paste_dropped_text", return_value=True),
        patch.object(terminal_module.GLib, "idle_add") as mock_idle_add,
    ):
        terminal._on_drag_data_received(
            terminal.terminal,
            context,
            0,
            0,
            selection_data,
            0,
            1234,
        )

    context.finish.assert_called_once_with(True, False, 1234)
    mock_idle_add.assert_called_once_with(terminal._focus_after_drop, 1234)


def test_drag_data_received_does_not_focus_after_rejected_drop():
    """Test rejected drops do not attempt to take focus."""
    from tree_style_terminal.widgets import terminal as terminal_module
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    context = Mock()
    selection_data = Mock()

    with (
        patch.object(terminal, "_paste_dropped_text", return_value=False),
        patch.object(terminal_module.GLib, "idle_add") as mock_idle_add,
    ):
        terminal._on_drag_data_received(
            terminal.terminal,
            context,
            0,
            0,
            selection_data,
            0,
            1234,
        )

    context.finish.assert_called_once_with(False, False, 1234)
    mock_idle_add.assert_not_called()


def test_focus_after_drop_presents_window_and_grabs_terminal_focus():
    """Test post-drop focus requests use the drop timestamp."""
    from tree_style_terminal.widgets.terminal import VteTerminal

    terminal = VteTerminal()
    toplevel = Mock()

    with (
        patch.object(terminal, "get_toplevel", return_value=toplevel),
        patch.object(terminal, "grab_focus") as mock_grab_focus,
    ):
        keep_callback = terminal._focus_after_drop(1234)

    toplevel.present_with_time.assert_called_once_with(1234)
    mock_grab_focus.assert_called_once()
    assert keep_callback is False
