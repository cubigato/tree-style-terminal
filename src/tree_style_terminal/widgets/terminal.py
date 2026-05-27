#!/usr/bin/env python3
"""
Terminal widget module for Tree Style Terminal.

This module provides a VTE terminal widget wrapper with spawn functionality.
"""

import os
import logging
import re
from urllib.parse import unquote, urlparse
from typing import Optional, List

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
gi.require_version("Gdk", "3.0")

from gi.repository import Gtk, Vte, GLib, Gdk

from ..config import config_manager, ConfigError

logger = logging.getLogger(__name__)


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

        self.search_previous_button = Gtk.Button()
        self.search_previous_button.set_image(
            Gtk.Image.new_from_icon_name("go-up-symbolic", Gtk.IconSize.BUTTON)
        )
        self.search_previous_button.set_tooltip_text("Previous match")
        self.search_previous_button.connect("clicked", lambda _button: self.search_previous())
        self.search_bar.pack_start(self.search_previous_button, False, False, 0)

        self.search_next_button = Gtk.Button()
        self.search_next_button.set_image(
            Gtk.Image.new_from_icon_name("go-down-symbolic", Gtk.IconSize.BUTTON)
        )
        self.search_next_button.set_tooltip_text("Next match")
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

    def _on_search_key_press(self, _entry: Gtk.SearchEntry, event: Gdk.EventKey) -> bool:
        """Close search when Escape is pressed in the search field."""
        if event.keyval == Gdk.KEY_Escape:
            self.hide_search()
            return True

        return False

    def _set_search_text(self, text: str) -> None:
        """Set the literal search text used by VTE."""
        if not text:
            self.terminal.search_set_regex(None, 0)
            return

        try:
            pattern = re.escape(text)
            regex = Vte.Regex.new_for_search(pattern, -1, 0)
            self.terminal.search_set_regex(regex, 0)
            self.terminal.search_set_wrap_around(True)
            self.search_next()
        except Exception as e:
            logger.warning(f"Failed to set terminal search text: {e}")

    def search_next(self) -> None:
        """Move to the next search match."""
        try:
            self.terminal.search_find_next()
        except Exception as e:
            logger.debug(f"Failed to find next terminal search match: {e}")

    def search_previous(self) -> None:
        """Move to the previous search match."""
        try:
            self.terminal.search_find_previous()
        except Exception as e:
            logger.debug(f"Failed to find previous terminal search match: {e}")

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

        # Set transparency from config
        transparency = config_manager.get("terminal.transparency", 1.0)
        self.set_transparency(transparency)

        # Apply initial theme
        self.apply_theme(self._current_theme)

    def _create_context_menu(self) -> Gtk.Menu:
        """Create the terminal context menu."""
        menu = Gtk.Menu()

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
        return menu

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

    def force_update_directory_tracking(self) -> None:
        """
        Force an update of directory tracking by triggering a title change.
        This can be used to refresh the current working directory.
        """
        try:
            # Send escape sequence to request current directory in title
            # This should trigger a title-changed event that updates the session CWD
            command = b'\033]0;\007'  # Simple title update request
            self.terminal.feed_child(command)
        except Exception as e:
            logger.debug(f"Failed to send directory update command: {e}")

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

    def get_transparency(self) -> float:
        """Get the current transparency value."""
        return getattr(self, '_transparency', 1.0)

    def get_current_theme(self) -> str:
        """Get the current theme name."""
        return self._current_theme
