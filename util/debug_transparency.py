#!/usr/bin/env python3
"""
Transparency debugging script for Tree Style Terminal.

This script helps diagnose transparency issues in the sidebar TreeView
by checking CSS classes, widget hierarchy, and background settings.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from tree_style_terminal.main import TreeStyleTerminalApp, MainWindow


def print_separator(title):
    """Print a formatted separator with title."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def check_css_classes(widget, name):
    """Check and print CSS classes for a widget."""
    context = widget.get_style_context()
    classes = context.list_classes()
    
    print(f"\n{name}:")
    print(f"  CSS Classes: {classes}")
    print(f"  Has 'view' class: {context.has_class('view')}")
    print(f"  Has 'sidebar-tree' class: {context.has_class('sidebar-tree')}")
    print(f"  Has 'transparent-tree' class: {context.has_class('transparent-tree')}")
    print(f"  Has 'transparent-scroll' class: {context.has_class('transparent-scroll')}")


def check_widget_hierarchy(window):
    """Check the complete widget hierarchy and CSS classes."""
    print_separator("WIDGET HIERARCHY & CSS CLASSES")
    
    # Main sidebar container
    sidebar = window.sidebar_revealer.get_child()
    check_css_classes(sidebar, "Main Sidebar Container")
    
    # Session sidebar
    session_sidebar = window.session_sidebar
    check_css_classes(session_sidebar, "Session Sidebar (Box)")
    
    # TreeView
    treeview = session_sidebar.tree_view
    check_css_classes(treeview, "TreeView")
    
    # Walk through box children to find ScrolledWindow
    for child in session_sidebar.get_children():
        if isinstance(child, Gtk.ScrolledWindow):
            check_css_classes(child, "ScrolledWindow")
            
            # Check viewport inside scrolled window
            viewport = child.get_child()
            if viewport:
                check_css_classes(viewport, "Viewport (auto-created)")
            break


def check_css_files():
    """Check CSS file contents."""
    print_separator("CSS FILE ANALYSIS")
    
    css_dir = Path(__file__).parent / "src" / "tree_style_terminal" / "resources" / "css"
    style_css = css_dir / "style.css"
    
    if style_css.exists():
        print(f"✅ CSS file exists: {style_css}")
        
        with open(style_css, 'r') as f:
            content = f.read()
        
        # Check for transparency rules
        transparency_rules = [
            '.sidebar-tree',
            '.transparent-tree',
            '.transparent-scroll',
            'background-color: transparent'
        ]
        
        print("\nTransparency Rules Found:")
        for rule in transparency_rules:
            if rule in content:
                print(f"  ✅ {rule}")
            else:
                print(f"  ❌ {rule}")
    else:
        print(f"❌ CSS file not found: {style_css}")


def test_transparency_visual():
    """Create a visual test to check transparency."""
    print_separator("VISUAL TRANSPARENCY TEST")
    
    try:
        # Create test app
        app = TreeStyleTerminalApp()
        app._on_startup(app)
        
        # Create main window
        window = MainWindow(app)
        
        print("✅ Application created successfully")
        print("✅ Window created successfully")
        
        # Check widget hierarchy
        check_widget_hierarchy(window)
        
        # Check if transparency should be working
        treeview = window.session_sidebar.tree_view
        treeview_context = treeview.get_style_context()
        
        print_separator("TRANSPARENCY ANALYSIS")
        
        conditions = [
            (not treeview_context.has_class('view'), "TreeView .view class removed"),
            (treeview_context.has_class('transparent-tree'), "TreeView has transparent-tree class"),
            (window.session_sidebar.get_style_context().has_class('sidebar-tree'), "Sidebar has sidebar-tree class"),
        ]
        
        all_good = True
        for condition, description in conditions:
            if condition:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
                all_good = False
        
        if all_good:
            print("\n🎉 All transparency conditions met!")
            print("   If sidebar still appears opaque, the issue may be:")
            print("   1. CSS specificity conflict with theme")
            print("   2. Parent widget background override") 
            print("   3. Terminal transparency not configured")
        else:
            print("\n⚠️  Some transparency conditions not met - this explains the opacity")
        
        return window
        
    except Exception as e:
        print(f"❌ Error creating application: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main debugging function."""
    print("🔍 Tree Style Terminal Transparency Debugger")
    print("=" * 60)
    
    # Check CSS files first
    check_css_files()
    
    # Test application transparency setup
    window = test_transparency_visual()
    
    if window:
        print_separator("SUMMARY")
        print("Debugging complete. Check the analysis above for any issues.")
        print("\nTo test visually:")
        print("1. Run the main application")
        print("2. Check if sidebar background shows terminal transparency")
        print("3. If still opaque, check parent window transparency settings")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()