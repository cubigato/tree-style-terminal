#!/usr/bin/env python3
"""
Integration tests for font scaling functionality.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from tree_style_terminal.main import CSSLoader
from tree_style_terminal.config.manager import ConfigManager


class TestFontScalingIntegration(unittest.TestCase):
    """Integration tests for font scaling with real config files."""

    def setUp(self):
        """Set up test environment with temporary config."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.yaml"
        
        # Clear environment
        if 'TST_DPI' in os.environ:
            del os.environ['TST_DPI']

    def tearDown(self):
        """Clean up test environment."""
        if 'TST_DPI' in os.environ:
            del os.environ['TST_DPI']
        
        # Clean up temp files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('tree_style_terminal.main.config_manager')
    @patch('tree_style_terminal.main.Gtk')
    def test_config_file_dpi_scaling(self, mock_gtk, mock_config):
        """Test that DPI scaling from config file is applied."""
        # Mock config manager responses
        mock_config.load_config.return_value = None
        mock_config.get.side_effect = lambda key, default: {
            "theme": "dark",
            "display.dpi_scale": 1.5
        }.get(key, default)
        
        # Mock GTK settings
        mock_settings = MagicMock()
        mock_settings.get_property.return_value = "Sans 10"
        mock_gtk.Settings.get_default.return_value = mock_settings
        
        # Create CSS loader (should read our config)
        css_loader = CSSLoader()
        
        # Verify DPI scale is read correctly
        self.assertEqual(css_loader._config_dpi_scale, 1.5)
        
        # Verify effective scale calculation
        scale = css_loader._calculate_effective_dpi_scale()
        self.assertEqual(scale, 1.5)

    @patch('tree_style_terminal.main.config_manager')
    @patch('tree_style_terminal.main.Gtk')
    def test_priority_system_works(self, mock_gtk, mock_config):
        """Test that CLI override takes priority over config."""
        # Mock config manager responses
        mock_config.load_config.return_value = None
        mock_config.get.side_effect = lambda key, default: {
            "theme": "dark", 
            "display.dpi_scale": 1.2
        }.get(key, default)
        
        # Mock GTK
        mock_settings = MagicMock()
        mock_settings.get_property.return_value = "Sans 10"
        mock_gtk.Settings.get_default.return_value = mock_settings
        
        # Test CLI override
        css_loader = CSSLoader(override_dpi=192)  # Should be 2.0 scale
        scale = css_loader._calculate_effective_dpi_scale()
        self.assertEqual(scale, 2.0)  # 192/96
        
        # Test env override
        os.environ['TST_DPI'] = '144'
        css_loader = CSSLoader()  # No CLI override
        scale = css_loader._calculate_effective_dpi_scale()
        self.assertEqual(scale, 1.5)  # 144/96
        
        # Test config fallback
        del os.environ['TST_DPI']
        css_loader = CSSLoader()  # No CLI or env override
        scale = css_loader._calculate_effective_dpi_scale()
        self.assertEqual(scale, 1.2)  # From config


if __name__ == '__main__':
    unittest.main()