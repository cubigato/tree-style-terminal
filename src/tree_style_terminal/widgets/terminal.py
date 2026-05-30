#!/usr/bin/env python3
"""
Terminal widget module for Tree Style Terminal.

This module provides a VTE terminal widget wrapper with spawn functionality.
"""

import os
import logging
import re
from pathlib import Path
from urllib.parse import unquote, urlparse
from typing import Optional, List

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
gi.require_version("Gdk", "3.0")

from gi.repository import Gtk, Vte, GLib, Gdk

from ..config import config_manager, ConfigError

logger = logging.getLogger(__name__)

URL_MATCH_PATTERN = r"https?://[^\s<>'\"]+[^\s<>'\".,;:!?)]"
FILE_PATH_MATCH_PATTERN = r"(?:~|/|\./|\../)[^\s<>'\"]*[^\s<>'\".,;:!?)]"
FUZZY_SEARCH_SEPARATOR_PATTERN = r"[-_\s]*"
PCRE2_MULTILINE = 1024
VTE_REGEX_COMPILE_FLAGS = Vte.REGEX_FLAGS_DEFAULT | PCRE2_MULTILINE


def build_terminal_search_pattern(text: str, fuzzy: bool) -> str:
    """Build the PCRE2 pattern used for VTE terminal search."""
    if not fuzzy:
        return re.escape(text)

    pattern_parts: List[str] = ["(?i)"]
    in_separator_run = False
    has_search_term = False

    for character in text:
        if character in " \t\r\n-_":
            if not in_separator_run:
                pattern_parts.append(FUZZY_SEARCH_SEPARATOR_PATTERN)
                in_separator_run = True
            continue

        pattern_parts.append(re.escape(character))
        in_separator_run = False
        has_search_term = True

    if not has_search_term:
        return re.escape(text)

    return "".join(pattern_parts)


class VteTerminal(Gtk.Box):
    """
    A VTE terminal widget wrapper that provides spawn functionality
    and basic configuration options.
    """

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Load configuration
        try:
            config_manager.load_config()
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            raise

        # Create the VTE terminal
        self.terminal = Vte.Terminal()

        # Get theme from config (fallback to dark)
        self._current_theme = config_manager.get("theme", "dark")

        # Set up basic terminal properties
        self._configure_terminal()
        self._context_menu = self._create_context_menu()
        self._context_menu_target: Optional[str] = None
        self._setup_text_drag_and_drop()

        # Add a lightweight search bar for the active terminal scrollback.
        self._setup_search_bar()

        # Add terminal to a scrolled window
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )
        self.scrolled_window.add(self.terminal)

        # Pack into the box
        self.pack_start(self.search_revealer, False, False, 0)
        self.pack_start(self.scrolled_window, True, True, 0)

        # Show the terminal widgets explicitly
        self.terminal.show()
        self.scrolled_window.show()
        self.search_revealer.show()
        self.search_bar.show_all()
        self.show()

        # Store process information
        self.pid: Optional[int] = None
        self.pty_fd: Optional[int] = None

        # Connect signals
        self.terminal.connect("child-exited", self._on_child_exited)
        self.terminal.connect("window-title-changed", self._on_title_changed)
        self.terminal.connect("button-press-event", self._on_button_press)

    def grab_focus(self) -> None:
        """Focus the underlying VTE widget instead of the wrapper box."""
        self.terminal.grab_focus()

    def _setup_search_bar(self) -> None:
        """Create the hidden search controls for terminal scrollback."""
        self.search_revealer = Gtk.Revealer()
        self.search_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.search_revealer.set_transition_duration(120)
        self.search_revealer.set_reveal_child(False)

        self.search_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.search_bar.get_style_context().add_class("terminal-search-bar")

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search")
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.search_entry.connect("activate", lambda _entry: self.search_next())
        self.search_entry.connect("key-press-event", self._on_search_key_press)
        self.search_bar.pack_start(self.search_entry, True, True, 0)

        self.search_fuzzy_toggle = Gtk.ToggleButton(label="Fuzzy")
        self.search_fuzzy_toggle.set_active(True)
        self.search_fuzzy_toggle.set_tooltip_text(
            "Fuzzy search: case-insensitive, ignores spaces, hyphens, and underscores"
        )
        self.search_fuzzy_toggle.connect("toggled", self._on_search_mode_toggled)
        self.search_bar.pack_start(self.search_fuzzy_toggle, False, False, 0)

        self.search_previous_button = Gtk.Button()
        self.search_previous_button.set_image(
            Gtk.Image.new_from_icon_name("go-up-symbolic", Gtk.IconSize.BUTTON)
        )
        self.search_previous_button.set_tooltip_text("Previous match (Shift+Enter)")
        self.search_previous_button.connect("clicked", lambda _button: self.search_previous())
        self.search_bar.pack_start(self.search_previous_button, False, False, 0)

        self.search_next_button = Gtk.Button()
        self.search_next_button.set_image(
            Gtk.Image.new_from_icon_name("go-down-symbolic", Gtk.IconSize.BUTTON)
        )
        self.search_next_button.set_tooltip_text("Next match (Enter)")
        self.search_next_button.connect("clicked", lambda _button: self.search_next())
        self.search_bar.pack_start(self.search_next_button, False, False, 0)

        self.search_close_button = Gtk.Button()
        self.search_close_button.set_image(
            Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.BUTTON)
        )
        self.search_close_button.set_tooltip_text("Close search")
        self.search_close_button.connect("clicked", lambda _button: self.hide_search())
        self.search_bar.pack_start(self.search_close_button, False, False, 0)

        self.search_revealer.add(self.search_bar)

    def show_search(self) -> None:
        """Open the scrollback search UI for this terminal."""
        self.search_fuzzy_toggle.set_active(True)
        self.search_revealer.set_reveal_child(True)
        self.search_entry.grab_focus()
        self.search_entry.select_region(0, -1)

    def hide_search(self) -> None:
        """Close search and clear VTE search state."""
        self.search_entry.set_text("")
        self.terminal.search_set_regex(None, 0)
        self.search_revealer.set_reveal_child(False)
        self.grab_focus()

    def _on_search_changed(self, entry: Gtk.SearchEntry) -> None:
        """Update VTE search state as the user edits the query."""
        self._set_search_text(entry.get_text())

    def _on_search_mode_toggled(self, _button: Gtk.ToggleButton) -> None:
        """Refresh VTE search state when fuzzy/exact mode changes."""
        self._set_search_text(self.search_entry.get_text())

    def _on_search_key_press(self, _entry: Gtk.SearchEntry, event: Gdk.EventKey) -> bool:
        """Handle search-field keyboard navigation."""
        if event.keyval == Gdk.KEY_Escape:
            self.hide_search()
            return True

        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if event.state & Gdk.ModifierType.SHIFT_MASK:
                self.search_previous()
            else:
                self.search_next()
            return True

        return False

    def _set_search_text(self, text: str) -> None:
        """Set the search text used by VTE."""
        if not text:
            self.terminal.search_set_regex(None, 0)
            return

        try:
            pattern = build_terminal_search_pattern(
                text,
                self.search_fuzzy_toggle.get_active(),
            )
            regex = Vte.Regex.new_for_search(pattern, -1, VTE_REGEX_COMPILE_FLAGS)
            self.terminal.search_set_regex(regex, 0)
            self.terminal.search_set_wrap_around(True)
            if not self.search_next():
                self.search_previous()
        except Exception as e:
            logger.warning(f"Failed to set terminal search text: {e}")

    def search_next(self) -> bool:
        """Move to the next search match."""
        try:
            return bool(self.terminal.search_find_next())
        except Exception as e:
            logger.debug(f"Failed to find next terminal search match: {e}")
            return False

    def search_previous(self) -> bool:
        """Move to the previous search match."""
        try:
            return bool(self.terminal.search_find_previous())
        except Exception as e:
            logger.debug(f"Failed to find previous terminal search match: {e}")
            return False

    def _configure_terminal(self) -> None:
        """Configure basic terminal settings."""
        # Set default font
        self.set_font_size(12)

        # Set scrollback length from config
        scrollback_lines = config_manager.get("terminal.scrollback_lines", 10000)
        self.set_scrollback_length(scrollback_lines)

        # Set cursor settings
        self.terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.SYSTEM)
        self.terminal.set_cursor_shape(Vte.CursorShape.BLOCK)

        # Set mouse settings
        self.terminal.set_mouse_autohide(True)

        # Set word char exceptions
        self.terminal.set_word_char_exceptions("-A-Za-z0-9,./?%&#:_=+@~")

        # Enable VTE-native OSC 8 hyperlinks and conservative plain-text matches.
        self._configure_hyperlinks()

        # Set transparency from config
        transparency = config_manager.get("terminal.transparency", 1.0)
        self.set_transparency(transparency)

        # Apply initial theme
        self.apply_theme(self._current_theme)

    def _create_context_menu(self) -> Gtk.Menu:
        """Create the terminal context menu."""
        menu = Gtk.Menu()

        self._open_target_menu_item = Gtk.MenuItem(label="Open Link")
        self._open_target_menu_item.connect("activate", lambda _item: self._open_context_target())
        menu.append(self._open_target_menu_item)

        self._copy_target_menu_item = Gtk.MenuItem(label="Copy Link")
        self._copy_target_menu_item.connect("activate", lambda _item: self._copy_context_target())
        menu.append(self._copy_target_menu_item)

        self._target_separator_menu_item = Gtk.SeparatorMenuItem()
        menu.append(self._target_separator_menu_item)

        self._copy_menu_item = Gtk.MenuItem(label="Copy")
        self._copy_menu_item.connect("activate", lambda _item: self.copy_clipboard())
        menu.append(self._copy_menu_item)

        self._paste_menu_item = Gtk.MenuItem(label="Paste")
        self._paste_menu_item.connect("activate", lambda _item: self.paste_clipboard())
        menu.append(self._paste_menu_item)

        menu.append(Gtk.SeparatorMenuItem())

        self._select_all_menu_item = Gtk.MenuItem(label="Select All")
        self._select_all_menu_item.connect("activate", lambda _item: self.select_all())
        menu.append(self._select_all_menu_item)

        menu.show_all()
        self._set_target_menu_visible(False)
        return menu

    def _configure_hyperlinks(self) -> None:
        """Enable OSC 8 hyperlinks and add conservative URL/path matching."""
        try:
            self.terminal.set_allow_hyperlink(True)
        except Exception as e:
            logger.warning(f"Failed to enable terminal hyperlinks: {e}")

        for pattern in (URL_MATCH_PATTERN, FILE_PATH_MATCH_PATTERN):
            try:
                regex = Vte.Regex.new_for_match(pattern, -1, VTE_REGEX_COMPILE_FLAGS)
                tag = self.terminal.match_add_regex(regex, 0)
                self.terminal.match_set_cursor_name(tag, "pointer")
            except Exception as e:
                logger.warning(f"Failed to configure terminal match pattern {pattern}: {e}")

    def _setup_text_drag_and_drop(self) -> None:
        """Accept plain text drops as terminal paste input."""
        self.terminal.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.terminal.drag_dest_add_text_targets()
        self.terminal.connect("drag-data-received", self._on_drag_data_received)

    def _on_drag_data_received(
        self,
        _widget: Vte.Terminal,
        context: Gdk.DragContext,
        _x: int,
        _y: int,
        selection_data: Gtk.SelectionData,
        _info: int,
        time: int,
    ) -> None:
        """Paste dropped text into the terminal and reject non-text drops."""
        handled = self._paste_dropped_text(selection_data)

        try:
            context.finish(handled, False, time)
        except Exception as e:
            logger.debug(f"Failed to finish terminal drop context: {e}")

        if handled:
            GLib.idle_add(self._focus_after_drop, time)

    def _paste_dropped_text(self, selection_data: Gtk.SelectionData) -> bool:
        """Return whether text was extracted and pasted from a drop."""
        try:
            text = selection_data.get_text()
        except Exception as e:
            logger.debug(f"Failed to read dropped terminal text: {e}")
            return False

        if text is None:
            return False

        try:
            self.terminal.paste_text(text)
            return True
        except Exception as e:
            logger.warning(f"Failed to paste dropped terminal text: {e}")
            return False

    def _focus_after_drop(self, time: int) -> bool:
        """Present this window and focus VTE after GTK has finished the drop."""
        toplevel = self.get_toplevel()
        present_with_time = getattr(toplevel, "present_with_time", None)

        if callable(present_with_time):
            try:
                present_with_time(time)
            except Exception as e:
                logger.debug(f"Failed to present terminal window after drop: {e}")

        self.grab_focus()
        return False

    def _on_button_press(self, terminal: Vte.Terminal, event: Gdk.EventButton) -> bool:
        """Show the terminal context menu on right click."""
        if (
            event.type != Gdk.EventType.BUTTON_PRESS
            or event.button != Gdk.BUTTON_SECONDARY
        ):
            return False

        self._popup_context_menu(event)
        return True

    def _popup_context_menu(self, event: Gdk.EventButton) -> None:
        """Display the context menu at the pointer position."""
        self._context_menu_target = self._target_from_event(event)
        has_target = self._context_menu_target is not None

        if has_target:
            self._update_target_menu_labels(self._context_menu_target)
        self._set_target_menu_visible(has_target)
        self._copy_menu_item.set_sensitive(self.has_selection())

        if hasattr(self._context_menu, "popup_at_pointer"):
            self._context_menu.popup_at_pointer(event)
        else:
            self._context_menu.popup(
                None,
                None,
                None,
                None,
                event.button,
                event.time,
            )

    def _set_target_menu_visible(self, visible: bool) -> None:
        """Show link/path context actions only when the pointer is over a target."""
        self._open_target_menu_item.set_visible(visible)
        self._copy_target_menu_item.set_visible(visible)
        self._target_separator_menu_item.set_visible(visible)

    def _update_target_menu_labels(self, target: str) -> None:
        """Label target actions according to whether the target is a URL or path."""
        if urlparse(target).scheme:
            self._open_target_menu_item.set_label("Open Link")
            self._copy_target_menu_item.set_label("Copy Link")
        else:
            self._open_target_menu_item.set_label("Open File")
            self._copy_target_menu_item.set_label("Copy Path")

    def _target_from_event(self, event: Gdk.EventButton) -> Optional[str]:
        """Return an OSC 8 hyperlink or plain-text match for the pointer event."""
        try:
            target = self.terminal.hyperlink_check_event(event)
        except Exception as e:
            logger.debug(f"Failed to check terminal hyperlink under pointer: {e}")
            target = None

        if target:
            return self._clean_context_target(target)

        try:
            target, _tag = self.terminal.match_check_event(event)
        except Exception as e:
            logger.debug(f"Failed to check terminal text match under pointer: {e}")
            target = None

        if target:
            return self._clean_context_target(target)

        return None

    def _clean_context_target(self, target: str) -> Optional[str]:
        """Trim terminal-adjacent punctuation from detected links and paths."""
        cleaned = target.strip().rstrip(".,;:!?)")
        return cleaned or None

    def _open_context_target(self) -> None:
        """Open the link or file path currently associated with the context menu."""
        if not self._context_menu_target:
            return

        uri = self._target_to_uri(self._context_menu_target)
        if not uri:
            return

        toplevel = self.get_toplevel()
        parent = toplevel if isinstance(toplevel, Gtk.Window) else None

        try:
            Gtk.show_uri_on_window(parent, uri, Gdk.CURRENT_TIME)
        except Exception as e:
            logger.warning(f"Failed to open terminal target {uri}: {e}")

    def _copy_context_target(self) -> None:
        """Copy the link or path currently associated with the context menu."""
        if not self._context_menu_target:
            return

        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(self._context_menu_target, -1)
            clipboard.store()
        except Exception as e:
            logger.warning(f"Failed to copy terminal target: {e}")

    def _target_to_uri(self, target: str) -> Optional[str]:
        """Convert a detected context target to a URI suitable for GTK opening."""
        parsed = urlparse(target)
        if parsed.scheme:
            return target

        try:
            path = Path(os.path.expanduser(target))
            if not path.is_absolute():
                cwd = self.get_current_directory() or os.getcwd()
                path = Path(cwd) / path
            return path.resolve(strict=False).as_uri()
        except Exception as e:
            logger.debug(f"Failed to convert terminal target to URI: {e}")
            return None

    def has_selection(self) -> bool:
        """Return whether the terminal currently has selected text."""
        try:
            return bool(self.terminal.get_has_selection())
        except Exception as e:
            logger.debug(f"Failed to read terminal selection state: {e}")
            return False

    def copy_clipboard(self) -> None:
        """Copy selected terminal text to the clipboard."""
        try:
            self.terminal.copy_clipboard()
        except Exception as e:
            logger.warning(f"Failed to copy terminal selection: {e}")

    def paste_clipboard(self) -> None:
        """Paste clipboard text into the terminal."""
        try:
            self.terminal.paste_clipboard()
        except Exception as e:
            logger.warning(f"Failed to paste into terminal: {e}")

    def select_all(self) -> None:
        """Select all visible terminal scrollback text."""
        try:
            self.terminal.select_all()
        except Exception as e:
            logger.warning(f"Failed to select terminal contents: {e}")

    def spawn_shell(self, argv: Optional[List[str]] = None, cwd: Optional[str] = None) -> bool:
        """
        Spawn a shell in the terminal.

        Args:
            argv: Command and arguments to execute. If None, uses $SHELL or /bin/bash.
            cwd: Working directory. If None, uses current directory.

        Returns:
            True if spawn was successful, False otherwise.
        """
        if argv is None:
            # Use $SHELL environment variable, fallback to /bin/bash
            shell = os.environ.get("SHELL", "/bin/bash")
            argv = [shell]

        if cwd is None:
            cwd = os.getcwd()

        # Ensure working directory exists
        if not os.path.isdir(cwd):
            logger.warning(f"Working directory {cwd} does not exist, using home directory")
            cwd = os.path.expanduser("~")

        # Set up environment
        env = os.environ.copy()

        # Set TERM if not already set
        if "TERM" not in env:
            env["TERM"] = "xterm-256color"

        try:
            # Convert environment to the format expected by spawn_async
            envv = [f"{key}={value}" for key, value in env.items()]

            # Create a new PTY for the terminal
            pty = Vte.Pty.new_sync(Vte.PtyFlags.DEFAULT)
            self.terminal.set_pty(pty)

            # Store spawn arguments for the async callback
            self._spawn_argv = argv
            self._spawn_cwd = cwd
            self._last_spawn_cwd = cwd

            # Spawn the process using the modern async method
            pty.spawn_async(
                cwd,                     # working_directory
                argv,                    # argv
                envv,                    # envv
                GLib.SpawnFlags.DEFAULT, # spawn_flags
                None,                    # child_setup
                None,                    # child_setup_data
                -1,                      # timeout (-1 = no timeout)
                None,                    # cancellable
                self._on_spawn_complete  # callback
            )

            # Return True immediately - actual success is handled in callback
            return True

        except Exception as e:
            logger.error(f"Error spawning shell: {e}")
            return False

    def set_font_size(self, size: int) -> None:
        """Set the terminal font size."""
        try:
            from gi.repository import Pango

            font_desc = Pango.FontDescription()
            font_desc.set_family("monospace")
            font_desc.set_size(size * Pango.SCALE)
            self.terminal.set_font(font_desc)
        except Exception as e:
            logger.warning(f"Failed to set font size {size}: {e}")

    def set_scrollback_length(self, length: int) -> None:
        """Set the scrollback buffer length."""
        self.terminal.set_scrollback_lines(length)

    def get_window_title(self) -> str:
        """Get the current window title."""
        title = self.terminal.get_window_title()
        return title if title else "Terminal"

    def get_current_directory(self) -> Optional[str]:
        """Get the current working directory of the terminal."""
        try:
            directory_uri = self.terminal.get_current_directory_uri()
        except Exception as e:
            logger.debug(f"Failed to get terminal current directory URI: {e}")
            directory_uri = None

        if directory_uri:
            parsed_uri = urlparse(directory_uri)
            if parsed_uri.scheme == "file":
                directory = unquote(parsed_uri.path)
                if os.path.isdir(directory):
                    return directory

        if self.pid:
            try:
                directory = os.readlink(f"/proc/{self.pid}/cwd")
                if os.path.isdir(directory):
                    return directory
            except OSError as e:
                logger.debug(f"Failed to read terminal process cwd: {e}")

        return getattr(self, "_last_spawn_cwd", None)

    def close(self) -> None:
        """Close the terminal and clean up resources."""
        if self.pid:
            try:
                # Send SIGTERM to the process
                os.kill(self.pid, 15)
            except (OSError, ProcessLookupError):
                # Process might already be dead
                pass

    def _on_child_exited(self, terminal: Vte.Terminal, status: int) -> None:
        """Handle child process exit."""
        logger.info(f"Child process exited with status {status}")
        self.pid = None

        # Emit a custom signal that can be caught by parent widgets
        # For now, we'll just log it

    def _on_spawn_complete(self, pty: Vte.Pty, task: object, user_data=None) -> None:
        """Callback when spawning is complete."""
        try:
            success, child_pid = pty.spawn_finish(task)
            if success:
                # Store the PTY file descriptor for reference
                self.pty_fd = pty.get_fd()
                self.pid = child_pid
                
                logger.info(f"Successfully spawned shell in directory {self._spawn_cwd}")
            else:
                logger.error("Failed to spawn shell")
                self.pid = None
                self.pty_fd = None
        except Exception as e:
            logger.error(f"Error in spawn completion: {e}")
            self.pid = None
            self.pty_fd = None

        # Clean up temporary spawn arguments
        if hasattr(self, '_spawn_argv'):
            delattr(self, '_spawn_argv')
        if hasattr(self, '_spawn_cwd'):
            delattr(self, '_spawn_cwd')

    def _on_title_changed(self, terminal: Vte.Terminal) -> None:
        """Handle terminal title change."""
        title = self.get_window_title()
        logger.debug(f"Terminal title changed to: {title}")

        # Emit a custom signal that can be caught by parent widgets
        # For now, we'll just log it

    def apply_theme(self, theme_name: str) -> None:
        """Apply a color theme to the terminal."""
        self._current_theme = theme_name

        if theme_name == "dark":
            self._apply_dark_theme()
        else:
            self._apply_light_theme()

    def _apply_dark_theme(self) -> None:
        """Apply dark theme colors to the terminal."""
        try:
            # Get transparency value
            alpha = getattr(self, '_transparency', 1.0)

            # Dark theme colors with transparency
            bg_color = Gdk.RGBA()
            bg_color.parse("#000000")  # Dark background
            bg_color.alpha = alpha  # Apply transparency

            fg_color = Gdk.RGBA()
            fg_color.parse("#ffffff")  # White text

            # Standard 16-color palette for dark theme
            palette = [
                Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(),
                Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(),
                Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(),
                Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA()
            ]

            # Dark theme color palette
            colors = [
                "#2e3436", "#cc0000", "#4e9a06", "#c4a000",
                "#3465a4", "#75507b", "#06989a", "#d3d7cf",
                "#555753", "#ef2929", "#8ae234", "#fce94f",
                "#729fcf", "#ad7fa8", "#34e2e2", "#eeeeec"
            ]

            for i, color_str in enumerate(colors):
                palette[i].parse(color_str)

            # Apply colors to terminal
            self.terminal.set_colors(fg_color, bg_color, palette)

            logger.debug("Applied dark theme to terminal")

        except Exception as e:
            logger.warning(f"Failed to apply dark theme: {e}")

    def _apply_light_theme(self) -> None:
        """Apply light theme colors to the terminal."""
        try:
            # Get transparency value
            alpha = getattr(self, '_transparency', 1.0)

            # Light theme colors with transparency
            bg_color = Gdk.RGBA()
            bg_color.parse("#ffffff")  # White background
            bg_color.alpha = alpha  # Apply transparency

            fg_color = Gdk.RGBA()
            fg_color.parse("#000000")  # Black text

            # Standard 16-color palette for light theme
            palette = [
                Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(),
                Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(),
                Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(),
                Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA(), Gdk.RGBA()
            ]

            # Light theme color palette
            colors = [
                "#000000", "#cc0000", "#4e9a06", "#c4a000",
                "#3465a4", "#75507b", "#06989a", "#2e3436",
                "#555753", "#ef2929", "#8ae234", "#fce94f",
                "#729fcf", "#ad7fa8", "#34e2e2", "#d3d7cf"
            ]

            for i, color_str in enumerate(colors):
                palette[i].parse(color_str)

            # Apply colors to terminal
            self.terminal.set_colors(fg_color, bg_color, palette)

            logger.debug("Applied light theme to terminal")

        except Exception as e:
            logger.warning(f"Failed to apply light theme: {e}")

    def set_transparency(self, value: float) -> None:
        """
        Set the terminal transparency.

        Args:
            value: Transparency value between 0.0 (fully transparent) and 1.0 (fully opaque)
        """
        if not (0.0 <= value <= 1.0):
            logger.warning(f"Invalid transparency value {value}, must be between 0.0 and 1.0")
            return

        self._transparency = value
        logger.debug(f"Set terminal transparency to {value}")

        # Re-apply current theme with new transparency
        self.apply_theme(self._current_theme)
