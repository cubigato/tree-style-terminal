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

from gi.repository import Gtk, Vte, GLib


logger = logging.getLogger(__name__)


class VteTerminal(Gtk.Box):
    """
    A VTE terminal widget wrapper that provides spawn functionality
    and basic configuration options.
    """
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        # Create the VTE terminal
        self.terminal = Vte.Terminal()
        
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
        
        # Set scrollback length
        self.set_scrollback_length(10000)
        
        # Set cursor settings
        self.terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.SYSTEM)
        self.terminal.set_cursor_shape(Vte.CursorShape.BLOCK)
        
        # Set mouse settings
        self.terminal.set_mouse_autohide(True)
        
        # Set word char exceptions
        self.terminal.set_word_char_exceptions("-A-Za-z0-9,./?%&#:_=+@~")
        
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
            
            # Spawn the process using the sync version for GTK3
            success, pid = self.terminal.spawn_sync(
                Vte.PtyFlags.DEFAULT,  # pty_flags
                cwd,                   # working_directory
                argv,                  # argv
                envv,                  # envv
                GLib.SpawnFlags.DEFAULT,  # spawn_flags
                None,                  # child_setup
                None                   # child_setup_data
            )
            
            if success:
                self.pid = pid
                logger.info(f"Spawned shell with PID {pid} in directory {cwd}")
                return True
            else:
                logger.error("Failed to spawn shell")
                return False
                
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
        # This is a simplified implementation
        # In a real implementation, you might want to track directory changes
        # or use OSC sequences to get the actual CWD
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
        
    def _on_title_changed(self, terminal: Vte.Terminal) -> None:
        """Handle terminal title change."""
        title = self.get_window_title()
        logger.debug(f"Terminal title changed to: {title}")
        
        # Emit a custom signal that can be caught by parent widgets
        # For now, we'll just log it