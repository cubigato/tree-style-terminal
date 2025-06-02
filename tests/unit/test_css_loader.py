import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from tree_style_terminal.main import CSSLoader


class TestCSSLoader(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.css_loader = CSSLoader()
    
    def test_css_loader_initialization(self):
        """Test CSS loader initializes correctly."""
        self.assertIsNotNone(self.css_loader.css_provider)
        self.assertIsNotNone(self.css_loader.theme_provider)
        # Theme is automatically detected from system, so just check it's set
        self.assertIn(self.css_loader.current_theme, ["light", "dark"])
    
    @patch('tree_style_terminal.main.Path.exists')
    @patch('tree_style_terminal.main.print')
    def test_load_base_css_file_not_found(self, mock_print, mock_exists):
        """Test handling of missing CSS file."""
        mock_exists.return_value = False
        
        # Should not raise exception
        self.css_loader.load_base_css()
        
        # Should print font scaling info and warning (2 calls)
        self.assertEqual(mock_print.call_count, 2)
        # Check that one of the calls contains the warning
        call_args = [call[0][0] for call in mock_print.call_args_list]
        self.assertTrue(any("Warning" in arg for arg in call_args))
    
    @patch('tree_style_terminal.main.Path.exists')
    @patch.object(CSSLoader, '_add_provider_to_screen')
    @patch('tree_style_terminal.main.print')
    def test_load_base_css_success(self, mock_print, mock_add_provider, mock_exists):
        """Test successful CSS loading."""
        mock_exists.return_value = True
        mock_provider = MagicMock()
        self.css_loader.css_provider = mock_provider
        
        self.css_loader.load_base_css()
        
        mock_provider.load_from_path.assert_called_once()
        # Should be called twice: once for system CSS, once for base CSS
        self.assertEqual(mock_add_provider.call_count, 2)
        # Should print font scaling info and success message (2 calls)
        self.assertEqual(mock_print.call_count, 2)
        call_args = [call[0][0] for call in mock_print.call_args_list]
        self.assertTrue(any("Loaded base CSS" in arg for arg in call_args))
    
    @patch('tree_style_terminal.main.Path.exists')
    @patch.object(CSSLoader, '_add_provider_to_screen')
    @patch('tree_style_terminal.main.print')
    def test_load_base_css_error(self, mock_print, mock_add_provider, mock_exists):
        """Test CSS loading error handling."""
        mock_exists.return_value = True
        mock_provider = MagicMock()
        mock_provider.load_from_path.side_effect = GLib.Error("Mock error")
        self.css_loader.css_provider = mock_provider
        
        self.css_loader.load_base_css()
        
        # Should print font scaling info and error message (2 calls)
        self.assertEqual(mock_print.call_count, 2)
        call_args = [call[0][0] for call in mock_print.call_args_list]
        self.assertTrue(any("Error loading base CSS" in arg for arg in call_args))
    
    @patch('tree_style_terminal.main.Path.exists')
    @patch('tree_style_terminal.main.print')
    def test_load_theme_file_not_found(self, mock_print, mock_exists):
        """Test handling of missing theme file."""
        mock_exists.return_value = False
        
        self.css_loader.load_theme("dark")
        
        mock_print.assert_called_once()
        self.assertIn("Warning", mock_print.call_args[0][0])
        self.assertIn("dark", mock_print.call_args[0][0])
    
    @patch('tree_style_terminal.main.Path.exists')
    @patch.object(CSSLoader, '_add_provider_to_screen')
    @patch('tree_style_terminal.main.Gdk.Screen.get_default')
    @patch('tree_style_terminal.main.Gtk.StyleContext')
    @patch('tree_style_terminal.main.Gtk.CssProvider')
    @patch('tree_style_terminal.main.print')
    def test_load_theme_success(self, mock_print, mock_css_provider_class, mock_style_context, mock_screen, mock_add_provider, mock_exists):
        """Test successful theme loading."""
        mock_exists.return_value = True
        mock_screen_instance = MagicMock()
        mock_screen.return_value = mock_screen_instance
        mock_context_instance = MagicMock()
        mock_style_context.return_value = mock_context_instance
        
        # Mock the new CSS provider instance
        mock_new_provider = MagicMock()
        mock_css_provider_class.return_value = mock_new_provider
        
        old_provider = self.css_loader.theme_provider
        
        self.css_loader.load_theme("dark")
        
        # Should remove old provider and add new one
        mock_context_instance.remove_provider_for_screen.assert_called_once_with(
            mock_screen_instance, old_provider
        )
        mock_new_provider.load_from_path.assert_called_once()
        mock_add_provider.assert_called_once_with(mock_new_provider)
        self.assertEqual(self.css_loader.current_theme, "dark")
        mock_print.assert_called_once()
        self.assertIn("Loaded dark theme", mock_print.call_args[0][0])
    
    def test_theme_toggle_light_to_dark(self):
        """Test theme toggling from light to dark."""
        self.css_loader.current_theme = "light"
        
        with patch.object(self.css_loader, 'load_theme') as mock_load:
            self.css_loader.toggle_theme()
            mock_load.assert_called_once_with("dark")
    
    def test_theme_toggle_dark_to_light(self):
        """Test theme toggling from dark to light."""
        self.css_loader.current_theme = "dark"
        
        with patch.object(self.css_loader, 'load_theme') as mock_load:
            self.css_loader.toggle_theme()
            mock_load.assert_called_once_with("light")
    
    @patch('tree_style_terminal.main.Gdk.Screen.get_default')
    @patch('tree_style_terminal.main.Gtk.StyleContext')
    def test_add_provider_to_screen(self, mock_style_context, mock_screen):
        """Test adding CSS provider to screen."""
        mock_screen_instance = MagicMock()
        mock_screen.return_value = mock_screen_instance
        mock_context_instance = MagicMock()
        mock_style_context.return_value = mock_context_instance
        mock_provider = MagicMock()
        
        self.css_loader._add_provider_to_screen(mock_provider)
        
        mock_context_instance.add_provider_for_screen.assert_called_once_with(
            mock_screen_instance,
            mock_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


if __name__ == '__main__':
    unittest.main()