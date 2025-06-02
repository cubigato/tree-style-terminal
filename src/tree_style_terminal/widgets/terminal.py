#!/usr/bin/env python3
"""
Terminal widget module for Tree Style Terminal.

This module provides a VTE terminal widget wrapper with spawn functionality.
"""

import os
import logging
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
        
        # Add terminal to a scrolled window
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )
        self.scrolled_window.add(self.terminal)
        
        # Pack into the box
        self.pack_start(self.scrolled_window, True, True, 0)
        
        # Show the terminal widgets explicitly
        self.terminal.show()
        self.scrolled_window.show()
        self.show()
        
        # Store process information
        self.pid: Optional[int] = None
        self.pty_fd: Optional[int] = None
        
        # Connect signals
        self.terminal.connect("child-exited", self._on_child_exited)
        self.terminal.connect("window-title-changed", self._on_title_changed)
        
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
        
        # Apply initial theme
        self.apply_theme(self._current_theme)
        
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
        if not self.pid:
            return None
        
        try:
            # Read the current working directory from /proc/PID/cwd
            cwd_link = f"/proc/{self.pid}/cwd"
            current_dir = os.readlink(cwd_link)
            return current_dir
        except (OSError, FileNotFoundError, PermissionError):
            # Process might not exist or we don't have permission
            return None
    
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
        
    def _on_spawn_complete(self, pty: Vte.Pty, task: object) -> None:
        """Callback when spawning is complete."""
        try:
            success = pty.spawn_finish(task)
            if success:
                # Store the PTY file descriptor for reference
                self.pty_fd = pty.get_fd()
                # Note: spawn_async doesn't directly provide PID like spawn_sync did
                # The actual child PID is managed internally by VTE
                self.pid = None  # Will be set by VTE's child-exited signal if needed
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
            # Dark theme colors
            bg_color = Gdk.RGBA()
            bg_color.parse("#1e1e1e")  # Dark background
            
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
            # Light theme colors
            bg_color = Gdk.RGBA()
            bg_color.parse("#ffffff")  # White background
            
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
    
    def get_current_theme(self) -> str:
        """Get the current theme name."""
        return self._current_theme