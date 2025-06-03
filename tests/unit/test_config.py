#!/usr/bin/env python3
"""
Unit tests for the ConfigManager class.

Tests configuration loading, validation, default creation, and error handling.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from tree_style_terminal.config import ConfigManager, ConfigError, get_config_manager
from tree_style_terminal.config.defaults import DEFAULT_CONFIG


class TestConfigManager:
    """Test cases for ConfigManager."""
    
    def test_init(self):
        """Test ConfigManager initialization."""
        config_manager = ConfigManager()
        assert config_manager._config == {}
        assert not config_manager._loaded
        assert isinstance(config_manager._config_path, Path)
    
    def test_get_config_path(self):
        """Test configuration path generation."""
        config_manager = ConfigManager()
        path = config_manager._get_config_path()
        
        assert isinstance(path, Path)
        assert path.name == "config.yaml"
        assert "tree-style-terminal" in str(path)
    
    def test_load_config_creates_default_when_missing(self):
        """Test that load_config creates default config when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager()
            config_manager._config_path = Path(temp_dir) / "config.yaml"
            
            # Load config - should create default
            config_manager.load_config()
            
            # Check file was created
            assert config_manager._config_path.exists()
            assert config_manager._loaded
            assert config_manager._config == DEFAULT_CONFIG
    
    def test_load_config_from_existing_file(self):
        """Test loading configuration from existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            
            # Create custom config file
            custom_config = {
                "theme": "light",
                "terminal": {"scrollback_lines": 5000},
                "ui": {"sidebar_width": 300}
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(custom_config, f)
            
            config_manager = ConfigManager()
            config_manager._config_path = config_path
            config_manager.load_config()
            
            # Check custom values were loaded and merged with defaults
            assert config_manager._config["theme"] == "light"
            assert config_manager._config["terminal"]["scrollback_lines"] == 5000
            assert config_manager._config["ui"]["sidebar_width"] == 300
            # Check default values still present
            assert config_manager._config["terminal"]["transparency"] == 1.0
            assert config_manager._config["display"]["dpi_scale"] == "auto"
    
    def test_load_config_only_loads_once(self):
        """Test that load_config only loads once unless explicitly reloaded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager()
            config_manager._config_path = Path(temp_dir) / "config.yaml"
            
            # First load
            config_manager.load_config()
            first_config = config_manager._config.copy()
            
            # Modify the config in memory
            config_manager._config["theme"] = "modified"
            
            # Load again - should not reload from file
            config_manager.load_config()
            assert config_manager._config["theme"] == "modified"
    
    def test_reload_config(self):
        """Test that reload forces a fresh load from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            
            # Create initial config
            with open(config_path, 'w') as f:
                yaml.dump({"theme": "light"}, f)
            
            config_manager = ConfigManager()
            config_manager._config_path = config_path
            config_manager.load_config()
            
            assert config_manager._config["theme"] == "light"
            
            # Modify file
            with open(config_path, 'w') as f:
                yaml.dump({"theme": "dark"}, f)
            
            # Reload should pick up changes
            config_manager.reload()
            assert config_manager._config["theme"] == "dark"
    
    def test_get_simple_value(self):
        """Test getting simple configuration values."""
        config_manager = ConfigManager()
        config_manager._config = {"theme": "dark", "test": "value"}
        config_manager._loaded = True
        
        assert config_manager.get("theme") == "dark"
        assert config_manager.get("test") == "value"
    
    def test_get_nested_value(self):
        """Test getting nested configuration values with dot notation."""
        config_manager = ConfigManager()
        config_manager._config = {
            "terminal": {"scrollback_lines": 10000},
            "ui": {"sidebar_width": 250}
        }
        config_manager._loaded = True
        
        assert config_manager.get("terminal.scrollback_lines") == 10000
        assert config_manager.get("ui.sidebar_width") == 250
    
    def test_get_with_default(self):
        """Test getting values with default fallback."""
        config_manager = ConfigManager()
        config_manager._config = {}
        config_manager._loaded = True
        
        assert config_manager.get("nonexistent", "default") == "default"
        assert config_manager.get("nested.nonexistent", 42) == 42
    
    def test_get_loads_config_if_not_loaded(self):
        """Test that get() loads config if not already loaded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager()
            config_manager._config_path = Path(temp_dir) / "config.yaml"
            
            # Get should trigger load
            value = config_manager.get("theme")
            assert config_manager._loaded
            assert value == DEFAULT_CONFIG["theme"]
    
    def test_validation_valid_values(self):
        """Test validation with valid configuration values."""
        config_manager = ConfigManager()
        config_manager._config = {
            "theme": "light",
            "terminal": {"scrollback_lines": 5000, "transparency": 0.8},
            "ui": {"sidebar_width": 300},
            "display": {"dpi_scale": 1.5}
        }
        
        # Should not raise any exceptions
        config_manager._validate_config()
    
    def test_validation_invalid_theme(self):
        """Test validation rejects invalid theme values."""
        config_manager = ConfigManager()
        config_manager._config = {"theme": "invalid_theme"}
        
        with pytest.raises(ConfigError, match="theme.*must be one of.*light.*dark.*automatic"):
            config_manager._validate_config()
    
    def test_validation_invalid_scrollback_lines(self):
        """Test validation rejects invalid scrollback line values."""
        config_manager = ConfigManager()
        config_manager._config = {"terminal": {"scrollback_lines": 50}}  # Too low
        
        with pytest.raises(ConfigError, match="scrollback_lines.*must be >= 100"):
            config_manager._validate_config()
        
        config_manager._config = {"terminal": {"scrollback_lines": 200000}}  # Too high
        with pytest.raises(ConfigError, match="scrollback_lines.*must be <= 100000"):
            config_manager._validate_config()
    
    def test_validation_invalid_transparency(self):
        """Test validation rejects invalid transparency values."""
        config_manager = ConfigManager()
        config_manager._config = {"terminal": {"transparency": -0.1}}  # Too low
        
        with pytest.raises(ConfigError, match="transparency.*must be >= 0.0"):
            config_manager._validate_config()
        
        config_manager._config = {"terminal": {"transparency": 1.5}}  # Too high
        with pytest.raises(ConfigError, match="transparency.*must be <= 1.0"):
            config_manager._validate_config()
    
    def test_validation_invalid_sidebar_width(self):
        """Test validation rejects invalid sidebar width values."""
        config_manager = ConfigManager()
        config_manager._config = {"ui": {"sidebar_width": 20}}  # Too small
        
        with pytest.raises(ConfigError, match="sidebar_width.*must be >= 50"):
            config_manager._validate_config()
    
    def test_validation_dpi_scale_auto(self):
        """Test validation accepts 'auto' for DPI scale."""
        config_manager = ConfigManager()
        config_manager._config = {"display": {"dpi_scale": "auto"}}
        
        # Should not raise any exceptions
        config_manager._validate_config()
    
    def test_validation_dpi_scale_numeric(self):
        """Test validation accepts numeric DPI scale values."""
        config_manager = ConfigManager()
        config_manager._config = {"display": {"dpi_scale": 1.5}}
        
        # Should not raise any exceptions
        config_manager._validate_config()
    
    def test_validation_dpi_scale_string_conversion(self):
        """Test that string numeric DPI scale values are converted to float."""
        config_manager = ConfigManager()
        config_manager._config = {"display": {"dpi_scale": "2.0"}}
        
        config_manager._validate_config()
        
        # Should be converted to float
        assert isinstance(config_manager._config["display"]["dpi_scale"], float)
        assert config_manager._config["display"]["dpi_scale"] == 2.0
    
    def test_validation_invalid_dpi_scale(self):
        """Test validation rejects invalid DPI scale values."""
        config_manager = ConfigManager()
        config_manager._config = {"display": {"dpi_scale": "invalid"}}
        
        with pytest.raises(ConfigError, match="dpi_scale.*must be 'auto' or a numeric value"):
            config_manager._validate_config()
    
    def test_save_config(self):
        """Test saving configuration to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            
            config_manager = ConfigManager()
            config_manager._config_path = config_path
            config_manager._config = {"theme": "light", "test": "value"}
            
            config_manager.save_config()
            
            # Verify file was created and contains correct data
            assert config_path.exists()
            with open(config_path, 'r') as f:
                saved_config = yaml.safe_load(f)
            
            assert saved_config["theme"] == "light"
            assert saved_config["test"] == "value"
    
    def test_merge_with_defaults(self):
        """Test merging loaded config with defaults."""
        config_manager = ConfigManager()
        
        loaded_config = {
            "theme": "light",
            "terminal": {"scrollback_lines": 5000},
            "new_section": {"new_value": "test"}
        }
        
        merged = config_manager._merge_with_defaults(loaded_config)
        
        # Custom values should override defaults
        assert merged["theme"] == "light"
        assert merged["terminal"]["scrollback_lines"] == 5000
        
        # Default values should be preserved
        assert merged["terminal"]["transparency"] == DEFAULT_CONFIG["terminal"]["transparency"]
        assert merged["ui"]["sidebar_width"] == DEFAULT_CONFIG["ui"]["sidebar_width"]
        
        # New sections should be added
        assert merged["new_section"]["new_value"] == "test"
    
    def test_load_config_yaml_error(self):
        """Test handling of invalid YAML in config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            
            # Create invalid YAML
            with open(config_path, 'w') as f:
                f.write("invalid: yaml: content: [")
            
            config_manager = ConfigManager()
            config_manager._config_path = config_path
            
            with pytest.raises(ConfigError, match="Invalid YAML"):
                config_manager.load_config()
    
    @patch("builtins.open", side_effect=OSError("Permission denied"))
    def test_load_config_io_error(self, mock_file):
        """Test handling of IO errors when loading config."""
        config_manager = ConfigManager()
        config_manager._config_path = Path("/nonexistent/config.yaml")
        
        with pytest.raises(ConfigError, match="Unexpected error loading config"):
            config_manager.load_config()
    
    @patch("builtins.open", side_effect=OSError("Permission denied"))
    def test_save_config_io_error(self, mock_file):
        """Test handling of IO errors when saving config."""
        config_manager = ConfigManager()
        config_manager._config = {"theme": "dark"}
        
        with pytest.raises(ConfigError, match="Cannot save config file"):
            config_manager.save_config()
    
    def test_get_config_path_method(self):
        """Test get_config_path() method."""
        config_manager = ConfigManager()
        path = config_manager.get_config_path()
        
        assert isinstance(path, Path)
        assert path == config_manager._config_path


class TestGlobalConfigManager:
    """Test cases for global config manager functionality."""
    
    def test_get_config_manager_singleton(self):
        """Test that get_config_manager returns the same instance."""
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        
        assert manager1 is manager2
        assert isinstance(manager1, ConfigManager)
    
    def test_get_config_manager_instance_type(self):
        """Test that get_config_manager returns a ConfigManager instance."""
        manager = get_config_manager()
        assert isinstance(manager, ConfigManager)