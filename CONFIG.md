# Configuration Guide

Tree Style Terminal supports configuration via a YAML file that allows you to customize various aspects of the application.

## Configuration File Location

The configuration file is located at:
```
~/.config/tree-style-terminal/config.yaml
```

The configuration file will be automatically created with default (commented) values when you first run the application.

## Configuration Options

### Theme
Controls the overall appearance of the application.

```yaml
# Theme for the entire GUI: "light", "dark", or "automatic"
# "automatic" follows system theme
theme: "dark"
```

**Options:**
- `"dark"` - Dark theme (default)
- `"light"` - Light theme  
- `"automatic"` - Follows system theme

### Application Diagnostics

```yaml
app:
  # Runtime diagnostic verbosity
  log_level: "warning"
```

**Options:**
- `log_level`: Controls runtime logging verbosity
  - `"debug"` - Very detailed diagnostics
  - `"info"` - Normal runtime diagnostics
  - `"warning"` - Warnings and errors only (default)
  - `"error"` - Errors only
  - `"critical"` - Critical failures only

**Priority:**
1. Command-line `--log-level` argument
2. `app.log_level` config file setting
3. Default `"warning"`

Use `--quiet` to suppress the startup message for a launch. It does not replace `log_level`.

### Terminal Settings

```yaml
terminal:
  # Scrollback buffer size (number of lines to keep in history)
  scrollback_lines: 10000
```

**Options:**
- `scrollback_lines`: Number of lines to keep in terminal history
  - Range: 100 - 100,000
  - Default: 10,000

### User Interface

```yaml
ui:
  # Initial width of the sidebar in pixels
  sidebar_width: 250
```

**Options:**
- `sidebar_width`: Initial width of the session sidebar
  - Range: 50 - 1,000 pixels
  - Default: 250 pixels

### Shortcuts

```yaml
shortcuts:
  # Open search for the active terminal scrollback
  terminal_search: "<Control><Shift>f"
```

**Options:**
- `terminal_search`: Keyboard shortcut that opens search for the active terminal
  - Default: `<Control><Shift>f`
  - Uses GTK accelerator syntax

### Display Settings

```yaml
display:
  # UI scaling factor (1.0 = 100%, 1.5 = 150%, etc.)
  # Set to "auto" to use system DPI detection and apply automatic scaling
  dpi_scale: "auto"
```

**Options:**
- `dpi_scale`: Controls UI scaling factor for high-DPI displays
  - `"auto"` - Intelligent automatic detection with comfort scaling (default)
    - Prioritizes monitor DPI over conservative system settings
    - **Calibrated 2.0x scaling for ~250 DPI displays (MacBook-style retina)**
    - Ensures minimum 1.8x scaling for other 4K+ displays (≥180 DPI)
    - Ensures minimum 1.25x scaling for 1440p displays (≥120 DPI)
    - Standard 1.0x scaling for 96 DPI displays
  - Float value: 0.5 - 3.0 (1.0 = normal size, 1.5 = 150% size, 2.0 = 200% size, etc.)

**Font Scaling Priority:**
DPI scaling follows this priority order (highest to lowest):
1. Command-line `--dpi` argument
2. `TST_DPI` environment variable
3. `display.dpi_scale` config file setting
4. Automatic system detection

This allows temporary overrides while maintaining persistent config preferences.

## Example Configurations

### 4K/High-DPI Display
```yaml
theme: "dark"
display:
  dpi_scale: 2.0  # 200% scaling - fonts and UI will be twice the normal size
ui:
  sidebar_width: 300
terminal:
  scrollback_lines: 20000
shortcuts:
  terminal_search: "<Control><Shift>f"
app:
  log_level: "warning"
```

### Light Theme with Large Sidebar
```yaml
theme: "light"
ui:
  sidebar_width: 400
terminal:
  scrollback_lines: 15000
```

### Minimal Configuration (only non-defaults)
```yaml
theme: "light"
app:
  log_level: "error"
terminal:
  scrollback_lines: 5000
```

## Validation

The configuration file is validated when loaded. Invalid values will cause the application to exit with an error message. This ensures configuration problems are caught early rather than causing unexpected behavior.

**Common validation errors:**
- Invalid theme names (must be "light", "dark", or "automatic")
- Invalid log levels (must be "debug", "info", "warning", "error", or "critical")
- Scrollback lines outside valid range (100-100,000)
- Sidebar width outside valid range (50-1,000)
- UI scale factor outside valid range (0.5-3.0) or not "auto"

## Reloading Configuration

Configuration is only loaded when the application starts. To apply changes, restart the application.

## Fallback Behavior

If the configuration file doesn't exist or has missing values:
- Missing file: Default values are used, and a template file is created
- Missing keys: Default values are used for missing options
- Invalid values: Application exits with error message

## File Creation

When you first run Tree Style Terminal, a configuration template will be automatically created at `~/.config/tree-style-terminal/config.yaml` with all options commented out. Uncomment and modify the values you want to change.
