import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

from tree_style_terminal.main import TreeStyleTerminalApp, MainWindow


class TestThemeIntegration(unittest.TestCase):
    """Integration tests for theme functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = TreeStyleTerminalApp()
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'window') and self.window:
            self.window.destroy()
    
    def test_app_has_css_loader(self):
        """Test that application has CSS loader instance."""
        self.assertIsNotNone(self.app.css_loader)
    
    @patch('tree_style_terminal.main.CSSLoader.load_base_css')
    @patch('tree_style_terminal.main.CSSLoader.load_theme')
    def test_css_loaded_on_startup(self, mock_load_theme, mock_load_base):
        """Test that CSS is loaded during application startup."""
        self.app._on_startup(self.app)
        
        mock_load_base.assert_called_once()
        # Theme is automatically detected, so we just check it was called once
        mock_load_theme.assert_called_once()
    
    @patch('tree_style_terminal.main.CSSLoader.load_base_css')
    @patch('tree_style_terminal.main.CSSLoader.load_theme')
    def test_main_window_has_theme_toggle_button(self, mock_load_theme, mock_load_base):
        """Test that main window has theme toggle button."""
        self.app._on_startup(self.app)
        
        self.window = MainWindow(self.app)
        
        # Check that theme toggle button exists
        self.assertTrue(hasattr(self.window, 'theme_toggle_button'))
        self.assertIsInstance(self.window.theme_toggle_button, Gtk.Button)
    
    @patch('tree_style_terminal.main.CSSLoader.load_base_css')
    @patch('tree_style_terminal.main.CSSLoader.load_theme')
    @patch('tree_style_terminal.main.CSSLoader.toggle_theme')
    def test_theme_toggle_button_callback(self, mock_toggle_theme, mock_load_theme, mock_load_base):
        """Test that theme toggle button callback works."""
        self.app._on_startup(self.app)
        self.window = MainWindow(self.app)
        
        # Simulate button click
        self.window._on_theme_toggle_clicked(self.window.theme_toggle_button)
        
        mock_toggle_theme.assert_called_once()
    
    @patch('tree_style_terminal.main.CSSLoader.load_base_css')
    @patch('tree_style_terminal.main.CSSLoader.load_theme')
    def test_theme_toggle_updates_button_icon(self, mock_load_theme, mock_load_base):
        """Test that theme toggle updates button icon."""
        self.app._on_startup(self.app)
        self.window = MainWindow(self.app)
        
        # Mock the CSS loader current theme
        self.app.css_loader.current_theme = "dark"
        
        # Trigger callback
        self.window._on_theme_toggle_clicked(self.window.theme_toggle_button)
        
        # Check that button image was updated
        button_image = self.window.theme_toggle_button.get_image()
        self.assertIsNotNone(button_image)
    
    @patch('tree_style_terminal.main.CSSLoader.load_base_css')
    @patch('tree_style_terminal.main.CSSLoader.load_theme')
    def test_window_has_css_classes(self, mock_load_theme, mock_load_base):
        """Test that main window has proper CSS classes."""
        self.app._on_startup(self.app)
        self.window = MainWindow(self.app)
        
        # Check main window has CSS class
        style_context = self.window.get_style_context()
        self.assertTrue(style_context.has_class("main-window"))
    
    @patch('tree_style_terminal.main.CSSLoader.load_base_css')
    @patch('tree_style_terminal.main.CSSLoader.load_theme')
    def test_sidebar_has_css_classes(self, mock_load_theme, mock_load_base):
        """Test that sidebar elements have proper CSS classes."""
        self.app._on_startup(self.app)
        self.window = MainWindow(self.app)
        
        # Check session sidebar has the sidebar-tree CSS class (added by SessionSidebar itself)
        session_sidebar_context = self.window.session_sidebar.get_style_context()
        self.assertTrue(session_sidebar_context.has_class("sidebar-tree"))
        
        # Verify sidebar elements exist (basic structure test)
        self.assertIsNotNone(self.window.sidebar_revealer)
        self.assertIsNotNone(self.window.session_sidebar)
    
    @patch('tree_style_terminal.main.CSSLoader.load_base_css')
    @patch('tree_style_terminal.main.CSSLoader.load_theme')
    def test_sidebar_transparency_css_rules(self, mock_load_theme, mock_load_base):
        """Test that sidebar transparency CSS rules are properly loaded."""
        self.app._on_startup(self.app)
        self.window = MainWindow(self.app)
        
        # Check that sidebar has the sidebar-tree class needed for transparency
        session_sidebar_context = self.window.session_sidebar.get_style_context()
        self.assertTrue(session_sidebar_context.has_class("sidebar-tree"))
        
        # Verify CSS file contains transparency rules by reading the file
        import os
        css_file_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'src', 
            'tree_style_terminal', 'resources', 'css', 'style.css'
        )
        
        self.assertTrue(os.path.exists(css_file_path), "CSS file should exist")
        
        with open(css_file_path, 'r') as f:
            css_content = f.read()
        
        # Check that our transparency rules are present
        self.assertIn('.sidebar-tree', css_content)
        self.assertIn('background-color: transparent', css_content)
    
    @patch('tree_style_terminal.main.CSSLoader.load_base_css')
    @patch('tree_style_terminal.main.CSSLoader.load_theme')
    def test_sidebar_view_class_removal(self, mock_load_theme, mock_load_base):
        """Test that .view class is removed from sidebar for transparency to work."""
        self.app._on_startup(self.app)
        self.window = MainWindow(self.app)
        
        # Check that sidebar has sidebar-tree class but NOT view class
        session_sidebar_context = self.window.session_sidebar.get_style_context()
        
        # Critical for transparency: view class must be removed
        self.assertFalse(session_sidebar_context.has_class("view"), 
                        "The .view class must be removed for transparency to work")
        
        # Our custom class should still be present
        self.assertTrue(session_sidebar_context.has_class("sidebar-tree"),
                       "The .sidebar-tree class should be present")


if __name__ == '__main__':
    unittest.main()