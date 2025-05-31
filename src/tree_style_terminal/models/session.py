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
    children: List[TerminalSession] = field(default_factory=list, compare=False)
    
    def __post_init__(self) -> None:
        """Initialize title to cwd if not provided."""
        if self.title is None:
            # Use basename of cwd for a cleaner display
            self.title = os.path.basename(self.cwd) or self.cwd
    
    def __hash__(self) -> int:
        """Make session hashable based on pid and pty_fd."""
        return hash((self.pid, self.pty_fd))
    
    def __eq__(self, other: object) -> bool:
        """Two sessions are equal if they have the same pid and pty_fd."""
        if not isinstance(other, TerminalSession):
            return False
        return self.pid == other.pid and self.pty_fd == other.pty_fd