"""
Tree Style Terminal - A Python/GTK3 terminal application with tree-based session navigation.

This package provides a terminal emulator that organizes terminal sessions in a tree
structure instead of traditional tabs, making it easier to manage complex workflows
with multiple related terminal sessions.
"""

__author__ = "Tree Style Terminal Contributors"
__license__ = "Apache-2.0"

from ._metadata import APPLICATION_ID
from ._version import __version__
from .main import MainWindow, TreeStyleTerminalApp, main

__all__ = [
    "APPLICATION_ID",
    "MainWindow",
    "TreeStyleTerminalApp",
    "__version__",
    "main",
]
