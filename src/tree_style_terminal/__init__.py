"""
Tree Style Terminal - A Python/GTK4 terminal application with tree-based session navigation.

This package provides a terminal emulator that organizes terminal sessions in a tree
structure instead of traditional tabs, making it easier to manage complex workflows
with multiple related terminal sessions.
"""

__version__ = "0.1.0"
__author__ = "Tree Style Terminal Contributors"
__license__ = "GPL-3.0"

from .main import TreeStyleTerminalApp, MainWindow, main

__all__ = ["TreeStyleTerminalApp", "MainWindow", "main"]