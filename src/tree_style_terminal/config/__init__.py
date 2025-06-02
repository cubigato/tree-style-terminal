#!/usr/bin/env python3
"""
Configuration module for Tree Style Terminal.

This module provides configuration management functionality.
"""

from .manager import ConfigManager, ConfigError, get_config_manager

# Export the global config manager instance
config_manager = get_config_manager()

__all__ = ['ConfigManager', 'ConfigError', 'config_manager', 'get_config_manager']