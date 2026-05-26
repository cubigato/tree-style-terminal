# Tree Style Terminal

A Python/GTK3 terminal application featuring a collapsible tree-based session navigator instead of traditional tabs.
It is roughly inspired by tree-style-tabs add-on for Firefox.

![Tree Style Terminal Screenshot](screenshot-dark-transparent.png)
*Tree Style Terminal in action with dark theme, showing hierarchical session organization and transparent background*

## Overview

Tree Style Terminal reimagines terminal session management by organizing sessions in an infinitely nestable tree structure displayed in a hideable sidebar. Instead of managing dozens of tabs, you can create hierarchical relationships between terminal sessions, making it easier to organize complex workflows and development environments.

## Key Features

- **Tree-based Session Management**: Organize terminal sessions in a hierarchical tree structure
- **Collapsible Sidebar**: Toggle the session navigator to maximize terminal space
- **Session Adoption**: When a parent session closes, child sessions are automatically adopted by the grandparent
- **Smart Font Scaling**: Automatic DPI detection and scaling for high-resolution displays
- **Modern GTK3 Interface**: Native Wayland and X11 support with CSS theming
- **VTE Terminal Engine**: Same high-performance terminal engine used by GNOME Terminal
- **Light/Dark Themes**: Toggle between light and dark themes with CSS theming system
- **Flexible Configuration**: Comprehensive YAML configuration file for customizing themes, UI settings, and display scaling

## Current Status

This project is in active development.

Currently implemented:

- ✅ Core application structure with GTK3 interface
- ✅ Session management system (`TerminalSession`, `SessionTree`, `SessionManager`)
- ✅ Tree-based sidebar with navigation (`SessionSidebar`)
- ✅ VTE terminal integration with spawn functionality
- ✅ Automatic font scaling and DPI detection for high-resolution displays
- ✅ Complete theming system with light/dark CSS themes
- ✅ Command-line interface with DPI override options
- ✅ YAML configuration system with validation and automatic template creation
- ✅ Comprehensive test suite with unit and integration tests
- ✅ Smart terminal naming based on working directory
- ✅ Keyboard shortcuts for session creation, navigation, focus, and terminal clipboard
- ✅ Terminal/sidebar transparency support via configuration

Remaining work:

- ⏳ Session persistence and tree state management
- ⏳ Packaging and distribution
- ⏳ Ongoing quality assurance and regression coverage

## Installation

### System Dependencies (Required)

**Critical**: These system packages MUST be installed before attempting to install the Python package. PyGObject requires native libraries that cannot be installed via pip alone.

**Ubuntu/Debian:**
```bash
sudo apt install python3-dev libgirepository-2.0-dev libcairo2-dev pkg-config python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-vte-2.91
```

**Fedora/RHEL:**
```bash
sudo dnf install gobject-introspection-devel cairo-devel pkg-config python3-devel gtk3-devel vte291-devel
```

**Arch Linux:**
```bash
sudo pacman -S gobject-introspection cairo pkgconf python gtk3 vte3
```

### Python Package

After installing system dependencies, you can install Tree Style Terminal:

#### Method 1: Using uv tool install

```bash
# First install system dependencies (see above), then:
git clone <repository-url>
cd tree-style-terminal
uv tool install .
```

**If you get "ModuleNotFoundError: No module named 'gi'"**: This means PyGObject compilation failed. Common causes:
- Missing `libgirepository-2.0-dev` (newer systems need version 2.0, not 1.0)
- Missing other system dependencies listed above

Make sure all system dependencies are installed, then try:

```bash
# Clear uv cache if needed, then retry
uv cache clean
uv tool install .
```

#### Method 2: Using uv for development

```bash
# Install from source for development
git clone <repository-url>
cd tree-style-terminal
uv sync --extra dev
```

#### Method 3: Using system Python (Most reliable for GTK apps)

```bash
# Use system Python which has better access to GTK libraries
git clone <repository-url>
cd tree-style-terminal
python3 -m pip install --user .
```

**Note**: PyGObject (the `gi` module) requires compilation against system GTK libraries. If installation fails, ensure all system dependencies above are installed, then try Method 3.

## Configuration

Tree Style Terminal supports extensive customization through a YAML configuration file located at `~/.config/tree-style-terminal/config.yaml`. The configuration file is automatically created with default values on first run.
Also see [CONFIG.md](CONFIG.md)

### Key Configuration Options

- **Theme**: Choose between light, dark, or automatic (follows system theme)
- **Display Scaling**: Configure DPI scaling for high-resolution displays
- **Terminal Settings**: Customize scrollback buffer size
- **UI Settings**: Adjust sidebar width and other interface elements

**Example configuration:**
```yaml
theme: "dark"
display:
  dpi_scale: 2.0  # 200% scaling for 4K displays
ui:
  sidebar_width: 300
terminal:
  scrollback_lines: 20000
```

For complete configuration documentation, see [CONFIG.md](CONFIG.md).

## Usage

### Basic Application Launch

```bash
# Standard launch with automatic font scaling
tree-style-terminal
# or shorthand
tst
```

### Font and Display Configuration

Tree Style Terminal automatically detects your system's DPI and font settings to provide optimal scaling on high-resolution displays.

#### Automatic Font Scaling

The application automatically:
- Detects your system's DPI settings
- Uses your system's default font preferences
- Scales fonts appropriately for high-DPI displays
- Ensures minimum readable font sizes on 4K+ displays

#### Manual DPI Override

If fonts appear too small or large, you can override the DPI detection:

```bash
# Using command-line arguments (recommended)
tree-style-terminal --dpi 144    # 1.5x scaling for 1440p displays
tree-style-terminal --dpi 192    # 2x scaling for 4K displays
tree-style-terminal --dpi 240    # 2.5x scaling for high-DPI 4K

# Using environment variables
TST_DPI=192 tree-style-terminal
```

#### Testing Font Scaling

Check your system's font scaling and test different DPI values:

```bash
# Show system font information with the GUI
tree-style-terminal --show-info

# Test font scaling without starting the GUI
tree-style-terminal --test-fonts
tree-style-terminal --test-fonts --dpi 192
```

#### Complete Command-Line Reference

```bash
tree-style-terminal --help              # Show all options and examples
tree-style-terminal                     # Launch with automatic scaling
tree-style-terminal --dpi 192           # Set DPI for font scaling
tree-style-terminal --show-info         # Display system font information
tree-style-terminal --test-fonts        # Show font scaling test and exit
tree-style-terminal --quiet             # Suppress startup messages

# Combined options
tree-style-terminal --dpi 180 --quiet   # Launch with custom DPI, no messages
tree-style-terminal --show-info --dpi 240  # Test DPI without starting GUI

# Environment variable alternative
TST_DPI=192 tree-style-terminal                    # Set DPI via environment
```

## Theming

Tree Style Terminal supports light and dark themes through GTK CSS:

- **Default**: Dark theme, unless configured otherwise
- **Automatic**: Set `theme: "automatic"` to follow the detected GTK/system theme
- **Toggle**: Click the theme button in the header bar to switch between light and dark themes

### CSS Styling

The application loads a base GTK CSS file, a light or dark theme CSS file, and runtime-generated CSS for DPI scaling and sidebar transparency.

### Theme Files

CSS themes are located in `src/tree_style_terminal/resources/css/`:
- `style.css`: Base GTK widget styles
- `light-theme.css`: Light theme color overrides
- `dark-theme.css`: Dark theme color overrides

## Session Management

### Keyboard Navigation
- **New Child Session**: `Ctrl+Alt+T` - Create a new session as a child of the current session
- **New Sibling Session**: `Ctrl+Shift+T` - Create a new session at the same level as the current session
- **Close Session**: `Ctrl+Q` - Close the current session (children are adopted by parent)
- **Toggle Sidebar**: `F9` or `Ctrl+Shift+O` - Show/hide the session tree sidebar
- **Focus Sidebar**: `Ctrl+Shift+S` - Move keyboard focus to the session tree
- **Focus Terminal**: `Ctrl+Shift+F` - Move keyboard focus back to the terminal
- **Navigate Sessions**: Click on sessions in the sidebar or use `Alt+Left`/`Alt+Right` or `Ctrl+Shift+Left`/`Ctrl+Shift+Right`
- **Terminal Clipboard**: `Ctrl+Shift+C` / `Ctrl+Shift+V` - Copy/paste in the terminal

### Session Tree Navigation
The sidebar displays terminal sessions in a tree structure:
- **Root Sessions**: Top-level sessions with no parent
- **Child Sessions**: Sessions created from within other sessions
- **Session Adoption**: When you close a session with children, those children become children of the closed session's parent

### Smart Terminal Naming
Terminal sessions are automatically named based on your current working directory and shell context:
- **Directory-based Names**: Session names show the last two path components (e.g., `projects/myapp`)
- **User Context**: Session names include user@host information when available
- **Real-time Updates**: Session names and working directories update when VTE reports changes
- **Intelligent Parsing**: Handles various shell prompt formats with graceful fallbacks

## Development

### Setup Development Environment

1. Clone the repository and set up the environment:
```bash
git clone <repository-url>
cd tree-style-terminal
```

2. Install system dependencies (see Installation section above), then install the project and development dependencies:
```bash
uv sync --extra dev
```

3. Install pre-commit hooks:
```bash
uv run pre-commit install
```

### Running Tests

```bash
uv run pytest
```

The project includes comprehensive unit and integration tests covering:
- Session management and tree operations
- UI component integration
- Theme and CSS functionality
- Font scaling and DPI detection

### Code Quality

The project uses several tools to maintain code quality:

- **ruff**: Fast Python linter and code formatter
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Static type checking

Run all checks:
```bash
uv run ruff check .
uv run black --check .
uv run isort --check-only .
uv run mypy src/
```

## Architecture

Tree Style Terminal follows a clean architecture with clear separation of concerns:

- **Models**: Core domain objects (`TerminalSession`, `SessionTree`)
- **Controllers**: Business logic and event handling (`SessionManager`, `SidebarController`)
- **Widgets**: GTK3 UI components and terminal integration (`SessionSidebar`, `VteTerminal`)
- **Resources**: CSS themes and configuration files

The application uses the Model-View-Controller pattern with GTK3 widgets as views, dedicated controller classes for business logic, and clean model classes for data representation.

## Requirements

- Python 3.11+
- GTK 3.0+
- VTE 2.91+
- PyGObject
- PyCairo
- PyYAML

## Author & Contact

**Author:** Jannik Winkel
**Copyright:** cubigato GmbH
**Contact:** See imprint on [cubigato.de](https://cubigato.de/impressum/)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
