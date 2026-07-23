#!/usr/bin/env python3
"""
Unit tests for the ConfigManager class.

Tests configuration loading, validation, default creation, and error handling.
"""

import os
import stat
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from tree_style_terminal.config import ConfigError, ConfigManager, get_config_manager
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

    def test_get_config_path_uses_absolute_xdg_config_home(
        self, monkeypatch, tmp_path
    ):
        """An absolute XDG config root takes precedence over the default."""
        config_home = tmp_path / "xdg-config"
        monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))

        config_manager = ConfigManager()

        assert config_manager.get_config_path() == (
            config_home / "tree-style-terminal" / "config.yaml"
        )
        assert not config_home.exists()

    @pytest.mark.parametrize("xdg_config_home", ["", "relative/config"])
    def test_get_config_path_ignores_invalid_xdg_config_home(
        self, monkeypatch, tmp_path, xdg_config_home
    ):
        """Empty and relative XDG paths fall back to ~/.config."""
        monkeypatch.setenv("XDG_CONFIG_HOME", xdg_config_home)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        config_manager = ConfigManager()

        assert config_manager.get_config_path() == (
            tmp_path / ".config" / "tree-style-terminal" / "config.yaml"
        )
        assert not (tmp_path / ".config").exists()

    def test_get_config_path_defaults_to_home_config(self, monkeypatch, tmp_path):
        """An unset XDG config root preserves the existing native path."""
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        config_manager = ConfigManager()

        assert config_manager.get_config_path() == (
            tmp_path / ".config" / "tree-style-terminal" / "config.yaml"
        )
        assert not (tmp_path / ".config").exists()

    def test_import_does_not_create_config_storage(self, tmp_path):
        """Importing the config package has no filesystem side effects."""
        config_home = tmp_path / "xdg-config"
        environment = os.environ.copy()
        environment["XDG_CONFIG_HOME"] = str(config_home)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"

        subprocess.run(
            [sys.executable, "-c", "import tree_style_terminal.config"],
            check=True,
            env=environment,
        )

        assert not config_home.exists()

    def test_load_config_creates_default_when_missing(self):
        """Test that load_config creates default config when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager()
            config_manager._config_path = (
                Path(temp_dir) / "nested" / "config" / "config.yaml"
            )

            # Load config - should create default
            config_manager.load_config()

            # Check file was created
            assert config_manager._config_path.exists()
            assert config_manager._loaded
            assert config_manager._config == DEFAULT_CONFIG
            assert config_manager._config["terminal"] is not DEFAULT_CONFIG["terminal"]

    def test_new_config_directory_is_private_to_current_user(self, tmp_path):
        """Fresh application config directories are created with mode 0700."""
        config_manager = ConfigManager()
        config_manager._config_path = tmp_path / "config" / "config.yaml"

        previous_umask = os.umask(0)
        try:
            config_manager.load_config()
        finally:
            os.umask(previous_umask)

        mode = stat.S_IMODE(config_manager._config_path.parent.stat().st_mode)
        assert mode == 0o700

    def test_loaded_defaults_cannot_mutate_default_config(self):
        """Loaded configuration owns independent nested default values."""
        original_defaults = deepcopy(DEFAULT_CONFIG)
        config_manager = ConfigManager()

        merged = config_manager._merge_with_defaults({"theme": "light"})
        merged["terminal"]["scrollback_lines"] = 123
        merged["shortcuts"]["terminal_search"] = "F1"

        assert original_defaults == DEFAULT_CONFIG

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

            original_content = yaml.dump(custom_config)
            config_path.write_text(original_content, encoding="utf-8")

            config_manager = ConfigManager()
            config_manager._config_path = config_path
            config_manager.load_config()

            # Check custom values were loaded and merged with defaults
            assert config_manager._config["theme"] == "light"
            assert config_manager._config["terminal"]["scrollback_lines"] == 5000
            assert config_manager._config["ui"]["sidebar_width"] == 300
            # Check default values still present
            assert config_manager._config["app"]["log_level"] == "warning"
            assert config_manager._config["terminal"]["transparency"] == 1.0
            assert config_manager._config["display"]["dpi_scale"] == "auto"
            assert config_manager._config["shortcuts"]["terminal_search"] == "<Control><Shift>f"
            assert config_manager._config["workspace_profiles"]["default_directory"] == ""
            assert config_manager._config["ai"] == {
                "endpoint": "",
                "api_key": "",
                "model": "",
            }
            assert config_manager._config["shortcuts"]["ai_command_draft"] == (
                "<Control><Shift>a"
            )
            assert config_path.read_text(encoding="utf-8") == original_content

    def test_new_default_config_is_private_to_current_user(self):
        """Fresh config files are created with mode 0600 regardless of umask."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager()
            config_manager._config_path = Path(temp_dir) / "config.yaml"

            previous_umask = os.umask(0)
            try:
                config_manager.load_config()
            finally:
                os.umask(previous_umask)

            mode = stat.S_IMODE(config_manager._config_path.stat().st_mode)
            assert mode == 0o600

    def test_load_config_only_loads_once(self):
        """Test that load_config only loads once unless explicitly reloaded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager()
            config_manager._config_path = Path(temp_dir) / "config.yaml"

            # First load
            config_manager.load_config()

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
            "app": {"log_level": "debug"},
            "theme": "light",
            "terminal": {"scrollback_lines": 5000, "transparency": 0.8},
            "ui": {"sidebar_width": 300},
            "display": {"dpi_scale": 1.5},
            "shortcuts": {"terminal_search": "<Control><Alt>f"}
        }

        # Should not raise any exceptions
        config_manager._validate_config()

    def test_validation_invalid_shortcut_type(self):
        """Test validation rejects non-string shortcut values."""
        config_manager = ConfigManager()
        config_manager._config = {"shortcuts": {"terminal_search": 123}}

        with pytest.raises(ConfigError, match="terminal_search.*must be of type str"):
            config_manager._validate_config()

    @pytest.mark.parametrize("field", ["endpoint", "api_key", "model"])
    def test_validation_invalid_ai_config_type(self, field):
        config_manager = ConfigManager()
        config_manager._config = {"ai": {field: 123}}

        with pytest.raises(ConfigError, match=rf"ai\.{field}.*must be of type str"):
            config_manager._validate_config()

    def test_validation_invalid_workspace_profile_directory_type(self):
        """Test workspace profile directory accepts only user path strings."""
        config_manager = ConfigManager()
        config_manager._config = {"workspace_profiles": {"default_directory": 123}}

        with pytest.raises(ConfigError, match="default_directory.*must be of type str"):
            config_manager._validate_config()

    def test_validation_invalid_theme(self):
        """Test validation rejects invalid theme values."""
        config_manager = ConfigManager()
        config_manager._config = {"theme": "invalid_theme"}

        with pytest.raises(ConfigError, match="theme.*must be one of.*light.*dark.*automatic"):
            config_manager._validate_config()

    def test_validation_invalid_log_level(self):
        """Test validation rejects invalid log level values."""
        config_manager = ConfigManager()
        config_manager._config = {"app": {"log_level": "verbose"}}

        with pytest.raises(ConfigError, match="log_level.*must be one of.*debug.*info.*warning.*error.*critical"):
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
        assert merged["app"]["log_level"] == DEFAULT_CONFIG["app"]["log_level"]
        assert merged["terminal"]["transparency"] == DEFAULT_CONFIG["terminal"]["transparency"]
        assert merged["ui"]["sidebar_width"] == DEFAULT_CONFIG["ui"]["sidebar_width"]
        assert merged["shortcuts"]["terminal_search"] == DEFAULT_CONFIG["shortcuts"]["terminal_search"]

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

    @patch("pathlib.Path.mkdir", side_effect=OSError("Permission denied"))
    def test_load_config_directory_creation_error(self, mock_mkdir):
        """Test handling of errors while creating the config directory."""
        config_manager = ConfigManager()
        config_manager._config_path = Path("/nonexistent/config.yaml")

        with pytest.raises(ConfigError, match="Cannot create config directory"):
            config_manager.load_config()

    @patch("os.open", side_effect=OSError("Permission denied"))
    def test_load_config_file_creation_error(self, mock_open, tmp_path):
        """Test handling of errors while creating the config file."""
        config_manager = ConfigManager()
        config_manager._config_path = tmp_path / "config" / "config.yaml"

        with pytest.raises(ConfigError, match="Cannot create config file"):
            config_manager.load_config()

    @patch("builtins.open", side_effect=OSError("Permission denied"))
    def test_load_config_read_error(self, mock_file, tmp_path):
        """Test handling of IO errors while reading an existing config."""
        config_path = tmp_path / "config.yaml"
        config_path.touch()
        config_manager = ConfigManager()
        config_manager._config_path = config_path

        with pytest.raises(ConfigError, match="Cannot read config file"):
            config_manager.load_config()

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
