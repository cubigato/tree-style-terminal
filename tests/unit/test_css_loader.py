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
    @patch('tree_style_terminal.main.logger')
    def test_load_base_css_file_not_found(self, mock_logger, mock_exists):
        """Test handling of missing CSS file."""
        mock_exists.return_value = False
        
        # Should not raise exception
        self.css_loader.load_base_css()
        
        warning_messages = [call[0][0] for call in mock_logger.warning.call_args_list]
        self.assertTrue(any("Base CSS file not found" in arg for arg in warning_messages))
    
    @patch('tree_style_terminal.main.Path.exists')
    @patch.object(CSSLoader, '_add_provider_to_screen')
    @patch('tree_style_terminal.main.logger')
    def test_load_base_css_success(self, mock_logger, mock_add_provider, mock_exists):
        """Test successful CSS loading."""
        mock_exists.return_value = True
        mock_provider = MagicMock()
        self.css_loader.css_provider = mock_provider
        
        self.css_loader.load_base_css()
        
        mock_provider.load_from_path.assert_called_once()
        # Should be called for base CSS and system CSS
        self.assertGreaterEqual(mock_add_provider.call_count, 1)
        info_messages = [call[0][0] for call in mock_logger.info.call_args_list]
        self.assertTrue(any("Loaded base CSS" in arg for arg in info_messages))
    
    @patch('tree_style_terminal.main.Path.exists')
    @patch.object(CSSLoader, '_add_provider_to_screen')
    @patch('tree_style_terminal.main.logger')
    def test_load_base_css_error(self, mock_logger, mock_add_provider, mock_exists):
        """Test CSS loading error handling."""
        mock_exists.return_value = True
        mock_provider = MagicMock()
        mock_provider.load_from_path.side_effect = GLib.Error("Mock error")
        self.css_loader.css_provider = mock_provider
        
        self.css_loader.load_base_css()
        
        warning_messages = [call[0][0] for call in mock_logger.warning.call_args_list]
        self.assertTrue(any("Error loading base CSS" in arg for arg in warning_messages))
    
    @patch('tree_style_terminal.main.Path.exists')
    @patch('tree_style_terminal.main.logger')
    def test_load_theme_file_not_found(self, mock_logger, mock_exists):
        """Test handling of missing theme file."""
        mock_exists.return_value = False
        
        self.css_loader.load_theme("dark")
        
        mock_logger.warning.assert_called_once()
        self.assertIn("Theme file not found", mock_logger.warning.call_args[0][0])
        self.assertIn("dark", str(mock_logger.warning.call_args))
    
    @patch('tree_style_terminal.main.Path.exists')
    @patch.object(CSSLoader, '_add_provider_to_screen')
    @patch('tree_style_terminal.main.Gdk.Screen.get_default')
    @patch('tree_style_terminal.main.Gtk.StyleContext')
    @patch('tree_style_terminal.main.Gtk.CssProvider')
    @patch('tree_style_terminal.main.logger')
    def test_load_theme_success(self, mock_logger, mock_css_provider_class, mock_style_context, mock_screen, mock_add_provider, mock_exists):
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
        # Should be called for theme and system CSS reload
        self.assertGreaterEqual(mock_add_provider.call_count, 1)
        mock_add_provider.assert_any_call(mock_new_provider)
        self.assertEqual(self.css_loader.current_theme, "dark")
        info_messages = [call[0][0] for call in mock_logger.info.call_args_list]
        self.assertTrue(any("Loaded %s theme" in arg for arg in info_messages))
    
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

    @patch('tree_style_terminal.main.Path.exists')
    @patch.object(CSSLoader, '_add_provider_to_screen')
    @patch('tree_style_terminal.main.Gdk.Screen.get_default')
    @patch('tree_style_terminal.main.Gtk.StyleContext')
    @patch('tree_style_terminal.main.Gtk.CssProvider')
    def test_load_theme_updates_current_theme_before_runtime_css(self, mock_css_provider_class, mock_style_context, mock_screen, mock_add_provider, mock_exists):
        """Test runtime CSS is regenerated with the newly loaded theme."""
        mock_exists.return_value = True
        mock_screen.return_value = MagicMock()
        mock_style_context.return_value = MagicMock()
        mock_css_provider_class.return_value = MagicMock()
        self.css_loader.current_theme = "dark"

        seen_themes = []

        def capture_theme():
            seen_themes.append(self.css_loader.current_theme)

        with patch.object(self.css_loader, '_load_system_css', side_effect=capture_theme):
            self.css_loader.load_theme("light")

        self.assertEqual(seen_themes, ["light"])
        self.assertEqual(self.css_loader.current_theme, "light")
    
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

    @patch('tree_style_terminal.main.config_manager.get')
    def test_sidebar_transparency_css_uses_terminal_alpha(self, mock_config_get):
        """Test sidebar runtime CSS follows terminal transparency."""
        mock_config_get.return_value = 0.42
        self.css_loader.current_theme = "dark"

        css = self.css_loader._generate_sidebar_transparency_css()

        self.assertIn("rgba(37, 37, 37, 0.420)", css)
        self.assertIn(".sidebar treeview.view", css)
        self.assertIn("background-image: none", css)

    @patch('tree_style_terminal.main.config_manager.get')
    def test_sidebar_transparency_css_clamps_invalid_alpha(self, mock_config_get):
        """Test sidebar transparency CSS clamps out-of-range alpha values."""
        mock_config_get.return_value = 2.0
        self.css_loader.current_theme = "light"

        css = self.css_loader._generate_sidebar_transparency_css()

        self.assertIn("rgba(248, 248, 248, 1.000)", css)


if __name__ == '__main__':
    unittest.main()
