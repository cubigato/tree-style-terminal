#!/usr/bin/env python3
"""
Simple test script to verify configuration functionality.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, 'src')

from tree_style_terminal.config import ConfigManager, ConfigError

def test_config_manager():
    """Test basic ConfigManager functionality."""
    
    # Create temporary config directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Override config path for testing
        config_manager = ConfigManager()
        config_manager._config_path = Path(temp_dir) / "config.yaml"
        
        print(f"Testing with config path: {config_manager._config_path}")
        
        # Test 1: Load config when no file exists (should create default)
        print("\n1. Testing default config creation...")
        config_manager.load_config()
        
        # Check if default file was created
        assert config_manager._config_path.exists(), "Default config file should be created"
        print("✓ Default config file created")
        
        # Test 2: Check default values
        print("\n2. Testing default values...")
        assert config_manager.get("theme") == "dark", f"Expected 'dark', got {config_manager.get('theme')}"
        assert config_manager.get("terminal.scrollback_lines") == 10000, f"Expected 10000, got {config_manager.get('terminal.scrollback_lines')}"
        assert config_manager.get("ui.sidebar_width") == 250, f"Expected 250, got {config_manager.get('ui.sidebar_width')}"
        assert config_manager.get("display.dpi_scale") == "auto", f"Expected 'auto', got {config_manager.get('display.dpi_scale')}"
        print("✓ All default values correct")
        
        # Test 3: Test fallback values
        print("\n3. Testing fallback values...")
        assert config_manager.get("nonexistent.key", "fallback") == "fallback"
        print("✓ Fallback values work")
        
        # Test 4: Create custom config file
        print("\n4. Testing custom config...")
        custom_config = """
theme: "light"
terminal:
  scrollback_lines: 5000
ui:
  sidebar_width: 300
display:
  dpi_scale: 1.5
"""
        with open(config_manager._config_path, 'w') as f:
            f.write(custom_config)
        
        # Reload config
        config_manager.reload()
        
        # Check custom values
        assert config_manager.get("theme") == "light", f"Expected 'light', got {config_manager.get('theme')}"
        assert config_manager.get("terminal.scrollback_lines") == 5000, f"Expected 5000, got {config_manager.get('terminal.scrollback_lines')}"
        assert config_manager.get("ui.sidebar_width") == 300, f"Expected 300, got {config_manager.get('ui.sidebar_width')}"
        assert config_manager.get("display.dpi_scale") == 1.5, f"Expected 1.5, got {config_manager.get('display.dpi_scale')}"
        print("✓ Custom config values loaded correctly")
        
        # Test 4.5: Test string DPI scale conversion
        print("\n4.5. Testing string DPI scale conversion...")
        string_dpi_config = """
display:
  dpi_scale: "2.0"
"""
        with open(config_manager._config_path, 'w') as f:
            f.write(string_dpi_config)
        
        # Reload config
        config_manager.reload()
        
        # Check that string "2.0" was converted to float 2.0
        dpi_value = config_manager.get("display.dpi_scale")
        assert isinstance(dpi_value, float), f"Expected float, got {type(dpi_value)}"
        assert dpi_value == 2.0, f"Expected 2.0, got {dpi_value}"
        print("✓ String DPI scale converted to float correctly")
        
        # Test 5: Test validation errors
        print("\n5. Testing validation...")
        
        # Test invalid theme
        invalid_config = """theme: "invalid_theme" """
        with open(config_manager._config_path, 'w') as f:
            f.write(invalid_config)
        
        try:
            config_manager.reload()
            assert False, "Should have raised ConfigError for invalid theme"
        except ConfigError as e:
            print(f"✓ Validation error caught: {e}")
        
        # Test invalid scrollback lines
        invalid_config = """
terminal:
  scrollback_lines: 50
"""
        with open(config_manager._config_path, 'w') as f:
            f.write(invalid_config)
        
        try:
            config_manager.reload()
            assert False, "Should have raised ConfigError for invalid scrollback lines"
        except ConfigError as e:
            print(f"✓ Validation error caught: {e}")
        
        print("\n🎉 All tests passed!")

if __name__ == "__main__":
    try:
        test_config_manager()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)