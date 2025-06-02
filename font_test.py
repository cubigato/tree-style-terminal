#!/usr/bin/env python3
"""
Simple Font Scaling Test Utility for Tree Style Terminal

This is a basic standalone version. For full functionality, use:
  python -m tree_style_terminal --test-fonts
  python -m tree_style_terminal --test-fonts --dpi 192

Usage:
  python font_test.py              # Show current system settings
  TST_DPI=144 python font_test.py  # Test with specific DPI
"""

import sys
import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

def main():
    """Simple font test - for full functionality use the main application."""
    print("=== Simple Font Test ===")
    print("For full font testing functionality, use:")
    print("  python -m tree_style_terminal --test-fonts")
    print("  python -m tree_style_terminal --test-fonts --dpi 192")
    print()
    
    try:
        Gtk.init([])
        settings = Gtk.Settings.get_default()
        
        font_name = settings.get_property("gtk-font-name")
        dpi = settings.get_property("gtk-xft-dpi")
        manual_dpi = os.environ.get('TST_DPI')
        
        print(f"System font: {font_name or 'not set'}")
        print(f"GTK DPI: {dpi/1024.0 if dpi else 'not set'}")
        print(f"TST_DPI override: {manual_dpi or 'not set'}")
        
        if manual_dpi:
            try:
                effective_dpi = float(manual_dpi)
                scale = effective_dpi / 96.0
                print(f"Scale factor: {scale:.2f}")
            except ValueError:
                print(f"Invalid TST_DPI value: {manual_dpi}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()