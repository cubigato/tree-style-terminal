#!/usr/bin/env python3
"""
Default configuration values for Tree Style Terminal.
"""

# Default configuration values
DEFAULT_CONFIG = {
    "app": {
        # Runtime diagnostic verbosity: "debug", "info", "warning", "error", or "critical"
        "log_level": "warning",
    },

    # Theme for the entire GUI: "light", "dark", or "automatic"
    "theme": "dark",

    "terminal": {
        # Scrollback buffer size (number of lines to keep in history)
        "scrollback_lines": 10000,
        # Terminal transparency (0.0 = fully transparent, 1.0 = fully opaque)
        "transparency": 1.0,
    },

    "ui": {
        # Initial width of the sidebar in pixels
        "sidebar_width": 250,
    },

    "display": {
        # UI scaling factor (1.0 = 100%, 1.5 = 150%, etc.)
        # Set to "auto" to use system DPI detection
        "dpi_scale": "auto",
    },

    "shortcuts": {
        # Open search for the active terminal scrollback
        "terminal_search": "<Control><Shift>f",
    }
}

# Example configuration file content with comments
DEFAULT_CONFIG_TEMPLATE = """# Tree Style Terminal Configuration
# This file is automatically created with default values if it doesn't exist
# Uncomment and modify the values below to customize your terminal

# Theme for the entire GUI: "light", "dark", or "automatic"
# "automatic" follows system theme
#theme: "dark"

#app:
#  # Runtime diagnostic verbosity: "debug", "info", "warning", "error", or "critical"
#  log_level: "warning"

#terminal:
#  # Scrollback buffer size (number of lines to keep in history)
#  scrollback_lines: 10000
#  # Terminal transparency (0.0 = fully transparent, 1.0 = fully opaque)
#  transparency: 1.0

#ui:
#  # Initial width of the sidebar in pixels
#  sidebar_width: 250

#display:
#  # UI scaling factor (1.0 = 100%, 1.5 = 150%, etc.)
#  # Set to "auto" to use system DPI detection and apply automatic scaling
#  dpi_scale: "auto"

#shortcuts:
#  # Open search for the active terminal scrollback
#  # GTK accelerator syntax, e.g. "<Control><Shift>f"
#  terminal_search: "<Control><Shift>f"
"""

# Validation constraints
VALIDATION_RULES = {
    "theme": {
        "type": str,
        "allowed_values": ["light", "dark", "automatic"],
        "description": "Theme must be 'light', 'dark', or 'automatic'"
    },
    "app.log_level": {
        "type": str,
        "allowed_values": ["debug", "info", "warning", "error", "critical"],
        "description": "Log level must be 'debug', 'info', 'warning', 'error', or 'critical'"
    },
    "terminal.scrollback_lines": {
        "type": int,
        "min_value": 100,
        "max_value": 100000,
        "description": "Scrollback lines must be between 100 and 100000"
    },
    "terminal.transparency": {
        "type": float,
        "min_value": 0.0,
        "max_value": 1.0,
        "description": "Terminal transparency must be between 0.0 and 1.0"
    },
    "ui.sidebar_width": {
        "type": int,
        "min_value": 50,
        "max_value": 1000,
        "description": "Sidebar width must be between 50 and 1000 pixels"
    },
    "display.dpi_scale": {
        "type": [str, float],
        "allowed_values": ["auto"],
        "min_value": 0.5,
        "max_value": 3.0,
        "description": "UI scale factor must be 'auto' or a float between 0.5 and 3.0"
    },
    "shortcuts.terminal_search": {
        "type": str,
        "description": "Terminal search shortcut must be a GTK accelerator string"
    }
}
