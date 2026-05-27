"""
Domain model for terminal sessions.

A TerminalSession represents a single terminal process with its metadata,
including process information, working directory, display title, and child sessions.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TerminalSession:
    """
    Represents a single terminal session with its process and metadata.
    
    Attributes:
        pid: Process ID of the terminal process
        pty_fd: File descriptor for the pseudo-terminal
        cwd: Current working directory of the session
        title: Display title for the session (defaults to cwd in __post_init__)
        children: List of child sessions
    """
    pid: int
    pty_fd: int
    cwd: str
    title: Optional[str] = None
    auto_title: Optional[str] = None
    custom_title: Optional[str] = None
    children: List[TerminalSession] = field(default_factory=list, compare=False)
    
    def __post_init__(self) -> None:
        """Initialize display and automatic titles."""
        if self.auto_title is None:
            self.auto_title = self._get_short_path_title(self.cwd)

        if self.title is not None and self.custom_title is None and self.title != self.auto_title:
            self.custom_title = self.title

        if self.title is None:
            self.title = self.custom_title or self.auto_title

    def rename(self, title: str) -> None:
        """Set a custom title, or clear it if the title is blank."""
        cleaned_title = title.strip()
        if cleaned_title:
            self.custom_title = cleaned_title
            self.title = cleaned_title
        else:
            self.clear_custom_title()

    def clear_custom_title(self) -> None:
        """Return the session title to automatic naming."""
        self.custom_title = None
        self.title = self.auto_title or self._get_short_path_title(self.cwd)

    def set_automatic_title(self, title: str) -> bool:
        """
        Update the automatic title.

        Returns True when the visible title changed.
        """
        self.auto_title = title
        if self.custom_title is not None:
            return False

        if self.title == title:
            return False

        self.title = title
        return True
    
    def _get_short_path_title(self, path: str) -> str:
        """
        Get a short title from a path showing last two components.
        
        Args:
            path: The full path
            
        Returns:
            A short title like "parent/current" or just "current" for root paths
        """
        if not path or path == "/":
            return path
        
        # Split path and remove empty components
        parts = [p for p in path.split("/") if p]
        
        if len(parts) == 0:
            return "/"
        elif len(parts) == 1:
            return parts[0]
        else:
            # Return last two components
            return "/".join(parts[-2:])
    
    def parse_terminal_title(self, terminal_title: str) -> str:
        """
        Parse terminal title and format as "path/components (user@host)".
        
        Args:
            terminal_title: Terminal title like "user@host: /path/to/dir"
            
        Returns:
            Formatted title like "path/dir (user@host)"
        """
        if not terminal_title:
            return self._get_short_path_title(self.cwd)
        
        # Try to parse format: "user@host: /path/to/directory"
        if ": " in terminal_title:
            parts = terminal_title.split(": ", 1)
            if len(parts) == 2:
                user_host = parts[0].strip()
                path = parts[1].strip()
                
                # Get short path (last two components)
                short_path = self._get_short_path_title(path)
                
                # Format as "path (user@host)"
                return f"{short_path} ({user_host})"
        
        # Fallback: just return the terminal title as-is
        return terminal_title
    
    def __hash__(self) -> int:
        """Make session hashable based on pid and pty_fd."""
        return hash((self.pid, self.pty_fd))
    
    def __eq__(self, other: object) -> bool:
        """Two sessions are equal if they have the same pid and pty_fd."""
        if not isinstance(other, TerminalSession):
            return False
        return self.pid == other.pid and self.pty_fd == other.pty_fd
