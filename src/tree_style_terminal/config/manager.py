#!/usr/bin/env python3
"""
Configuration manager for Tree Style Terminal.

This module handles loading, validating, and saving configuration files.
"""

import logging
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from .defaults import DEFAULT_CONFIG, DEFAULT_CONFIG_TEMPLATE, VALIDATION_RULES

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Exception raised for configuration errors."""

    pass


class ConfigManager:
    """
    Manages application configuration with YAML file support.
    """

    def __init__(self):
        self._config: dict[str, Any] = {}
        self._config_path: Path = self._get_config_path()
        self._loaded = False

    def _get_config_path(self) -> Path:
        """Get the path to the configuration file."""
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home and Path(xdg_config_home).is_absolute():
            config_home = Path(xdg_config_home)
        else:
            config_home = Path.home() / ".config"

        return config_home / "tree-style-terminal" / "config.yaml"

    def load_config(self) -> None:
        """
        Load configuration from file or create default if it doesn't exist.

        Raises:
            ConfigError: If configuration is invalid or cannot be loaded.
        """
        if self._loaded:
            return

        try:
            if not self._config_path.exists():
                logger.info(f"Config file not found, creating default at {self._config_path}")
                self._create_default_config()
                self._config = deepcopy(DEFAULT_CONFIG)
            else:
                logger.info(f"Loading config from {self._config_path}")
                with open(self._config_path, encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f) or {}

                # Merge with defaults
                self._config = self._merge_with_defaults(loaded_config)

            # Validate configuration
            self._validate_config()
            self._loaded = True

            logger.info("Configuration loaded successfully")

        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config file {self._config_path}: {e}") from e
        except OSError as e:
            raise ConfigError(f"Cannot read config file {self._config_path}: {e}") from e
        except ConfigError:
            raise
        except Exception as e:
            raise ConfigError(f"Unexpected error loading config: {e}") from e

    def _create_default_config(self) -> None:
        """Create a default configuration file with commented examples."""
        try:
            self._config_path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        except OSError as e:
            raise ConfigError(
                f"Cannot create config directory {self._config_path.parent}: {e}"
            ) from e

        try:
            descriptor = os.open(
                self._config_path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
            with os.fdopen(descriptor, 'w', encoding='utf-8') as f:
                f.write(DEFAULT_CONFIG_TEMPLATE)
            logger.info(f"Created default config file at {self._config_path}")
        except OSError as e:
            raise ConfigError(f"Cannot create config file {self._config_path}: {e}") from e

    def _merge_with_defaults(self, loaded_config: dict[str, Any]) -> dict[str, Any]:
        """Merge loaded configuration with defaults."""
        def deep_merge(default: dict, loaded: dict) -> dict:
            result = deepcopy(default)
            for key, value in loaded.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        return deep_merge(DEFAULT_CONFIG, loaded_config)

    def _validate_config(self) -> None:
        """
        Validate the loaded configuration against validation rules.

        Raises:
            ConfigError: If configuration values are invalid.
        """
        for key, rule in VALIDATION_RULES.items():
            value = self._get_nested_value(key)

            if value is None:
                continue  # Skip validation for missing optional values

            # Special handling for DPI scale - convert string numbers to float
            if key == "display.dpi_scale" and isinstance(value, str):
                if value == "auto":
                    continue  # "auto" is valid
                else:
                    # Try to convert string to float
                    try:
                        value = float(value)
                        # Update the config with the converted value
                        self._set_nested_value(key, value)
                    except ValueError as e:
                        raise ConfigError(f"Config value '{key}' must be 'auto' or a numeric value, got '{value}'. {rule['description']}") from e

            # Type validation
            expected_types = rule["type"] if isinstance(rule["type"], list) else [rule["type"]]
            if not any(isinstance(value, t) for t in expected_types):
                type_names = [t.__name__ for t in expected_types]
                raise ConfigError(f"Config value '{key}' must be of type {'/'.join(type_names)}, got {type(value).__name__}")

            # String validation (allowed values) - only for actual strings
            if (
                isinstance(value, str)
                and "allowed_values" in rule
                and value not in rule["allowed_values"]
            ):
                raise ConfigError(f"Config value '{key}' must be one of {rule['allowed_values']}, got '{value}'. {rule['description']}")

            # Numeric validation
            if isinstance(value, int | float):
                if "min_value" in rule and value < rule["min_value"]:
                    raise ConfigError(f"Config value '{key}' must be >= {rule['min_value']}, got {value}. {rule['description']}")
                if "max_value" in rule and value > rule["max_value"]:
                    raise ConfigError(f"Config value '{key}' must be <= {rule['max_value']}, got {value}. {rule['description']}")

    def _get_nested_value(self, key: str) -> Any:
        """Get a nested configuration value using dot notation."""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value

    def _set_nested_value(self, key: str, value: Any) -> None:
        """Set a nested configuration value using dot notation."""
        keys = key.split('.')
        config = self._config

        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the final value
        config[keys[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation for nested values)
            default: Default value if key is not found

        Returns:
            Configuration value or default
        """
        if not self._loaded:
            self.load_config()

        value = self._get_nested_value(key)
        return value if value is not None else default

    def get_config_path(self) -> Path:
        """Get the path to the configuration file."""
        return self._config_path

    def reload(self) -> None:
        """Reload configuration from file."""
        self._loaded = False
        self.load_config()


# Global config manager instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
