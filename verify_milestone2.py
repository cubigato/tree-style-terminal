#!/usr/bin/env python3
"""
Verification script for Milestone 2 - Terminal Embedding

This script tests the VTE terminal integration.
"""

import sys
import os
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")

from gi.repository import Gtk, GLib
from src.tree_style_terminal.widgets.terminal import VteTerminal


def test_vte_import():
    """Test that VTE can be imported."""
    try:
        from gi.repository import Vte
        print("✓ VTE import successful")
        return True
    except ImportError as e:
        print(f"✗ VTE import failed: {e}")
        return False


def test_terminal_widget_creation():
    """Test that terminal widget can be created."""
    try:
        terminal = VteTerminal()
        print("✓ VteTerminal widget creation successful")
        return True
    except Exception as e:
        print(f"✗ VteTerminal widget creation failed: {e}")
        return False


def test_spawn_shell():
    """Test spawning a shell in the terminal."""
    try:
        terminal = VteTerminal()
        # Test with echo command to avoid interactive shell
        success = terminal.spawn_shell(argv=["/bin/echo", "test"])
        if success:
            print("✓ Shell spawn successful")
            return True
        else:
            print("✗ Shell spawn failed")
            return False
    except Exception as e:
        print(f"✗ Shell spawn failed with exception: {e}")
        return False


def test_font_configuration():
    """Test font configuration."""
    try:
        terminal = VteTerminal()
        terminal.set_font_size(12)
        terminal.set_scrollback_length(1000)
        print("✓ Font and scrollback configuration successful")
        return True
    except Exception as e:
        print(f"✗ Font configuration failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("Verifying Milestone 2 - Terminal Embedding")
    print("=" * 40)
    
    tests = [
        test_vte_import,
        test_terminal_widget_creation,
        test_spawn_shell,
        test_font_configuration,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Milestone 2 implementation is working.")
        return 0
    else:
        print("✗ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())