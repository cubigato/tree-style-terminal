# Tree Style Terminal

> **⚠️ Work in Progress**: This project is currently under active development. Many features described below are planned but not yet implemented. See [TODO.md](TODO.md) for current development status.

A Python/GTK3 terminal application featuring a collapsible tree-based session navigator instead of traditional tabs.

## Overview

Tree Style Terminal reimagines terminal session management by organizing sessions in an infinitely nestable tree structure displayed in a hideable sidebar. Instead of managing dozens of tabs, you can create hierarchical relationships between terminal sessions, making it easier to organize complex workflows and development environments.

## Key Features

- **Tree-based Session Management**: Organize terminal sessions in a hierarchical tree structure
- **Collapsible Sidebar**: Toggle the session navigator to maximize terminal space
- **Session Adoption**: When a parent session closes, child sessions are automatically adopted by the grandparent
- **Modern GTK3 Interface**: Native Wayland and X11 support with CSS theming
- **VTE Terminal Engine**: Same high-performance terminal engine used by GNOME Terminal
- **Keyboard-First Navigation**: Comprehensive keybinding support for efficient workflow
- **Session Persistence**: Automatically save and restore session tree structure

## Current Status

This project is in early development (Milestone 0-6). The core application is not yet functional. Currently available:

- ✅ Project structure and configuration
- ✅ Architecture documentation
- ✅ Development environment setup
- ✅ Basic GTK application with theming support
- ✅ CSS Foundation with Light/Dark themes
- ⏳ Terminal embedding (in progress)
- ❌ Session management
- ❌ Tree-based navigation

See [TODO.md](TODO.md) for detailed development milestones.
</edits>

## Display and Font Scaling

Tree Style Terminal automatically detects your system's DPI and font settings to provide optimal scaling on high-resolution displays like 4K monitors.

### Automatic Font Scaling

The application automatically:
- Detects your system's DPI settings
- Uses your system's default font preferences
- Scales fonts appropriately for high-DPI displays
- Ensures minimum readable font sizes on 4K+ displays

### Manual DPI Override

If fonts appear too small or large, you can override the DPI detection using command-line arguments or environment variables:

```bash
# Using command-line arguments (recommended)
python -m tree_style_terminal --dpi 144    # 1.5x scaling for 1440p displays
python -m tree_style_terminal --dpi 192    # 2x scaling for 4K displays
python -m tree_style_terminal --dpi 240    # 2.5x scaling for high-DPI 4K

# Using environment variables
TST_DPI=192 python -m tree_style_terminal
```

### Testing Font Scaling

Check your system's font scaling and test different DPI values:

```bash
# Show system font information with the GUI
python -m tree_style_terminal --show-info

# Test font scaling without starting the GUI
python -m tree_style_terminal --test-fonts
python -m tree_style_terminal --test-fonts --dpi 192

# Quick system check (standalone utility)
python font_test.py
TST_DPI=180 python font_test.py
```

### Complete Command-Line Reference

```bash
python -m tree_style_terminal --help              # Show all options and examples
python -m tree_style_terminal                     # Launch with automatic scaling
python -m tree_style_terminal --dpi 192           # Set DPI for font scaling
python -m tree_style_terminal --show-info         # Display system font information
python -m tree_style_terminal --test-fonts        # Show font scaling test and exit
python -m tree_style_terminal --quiet             # Suppress startup messages

# Combined options
python -m tree_style_terminal --dpi 180 --quiet   # Launch with custom DPI, no messages
python -m tree_style_terminal --show-info --dpi 240  # Test DPI without starting GUI

# Environment variable alternative
TST_DPI=192 python -m tree_style_terminal          # Set DPI via environment
```

## Theming

Tree Style Terminal supports light and dark themes through GTK CSS:

- **Default**: Light theme
- **Toggle**: Click the theme button (🌙/☀️ icon) in the header bar or use keyboard shortcut
- **Custom CSS**: Place custom styles in `~/.config/tree-style-terminal/custom.css` (planned)

### CSS Variables

The application uses CSS custom properties for consistent theming:

- `--bg-primary`, `--bg-secondary`: Background colors
- `--fg-primary`, `--fg-secondary`: Foreground colors  
- `--accent-color`: Highlight color
- `--terminal-bg`, `--terminal-fg`: Terminal colors
- `--sidebar-bg`, `--sidebar-selected`: Sidebar colors

### Theme Files

CSS themes are located in `src/tree_style_terminal/resources/css/`:
- `style.css`: Base styles and CSS variables
- `light-theme.css`: Light theme color overrides
- `dark-theme.css`: Dark theme color overrides

See [TODO.md](TODO.md) for detailed development milestones.

## Planned Installation (Future)

Once the application is functional, installation will be:

### System Dependencies (Required)

**Important**: GTK, VTE, and PyGObject must be installed via system package manager, not pip.

**Ubuntu/Debian:**
```bash
sudo apt install python3-dev libgirepository1.0-dev libcairo2-dev pkg-config
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-vte-2.91
```

**Fedora:**
```bash
sudo dnf install python3-devel gobject-introspection-devel cairo-devel pkgconfig
sudo dnf install python3-gobject gtk3-devel vte291-devel
```

**Arch Linux:**
```bash
sudo pacman -S python gobject-introspection cairo pkgconf
sudo pacman -S python-gobject gtk3 vte3
```

### Python Package

After installing system dependencies:

```bash
git clone https://github.com/tree-style-terminal/tree-style-terminal.git
cd tree-style-terminal
pip install -e ".[dev]"
```

**Note**: The pyproject.toml intentionally does not include GTK/VTE dependencies as they must be installed system-wide.

## Current Usage

### Basic Application Launch

```bash
# Standard launch with automatic font scaling
python -m tree_style_terminal

# Launch with custom DPI for 4K displays
python -m tree_style_terminal --dpi 192

# Quiet launch (suppress startup messages)
python -m tree_style_terminal --quiet
```

### Font and Display Testing

```bash
# Show system font and display information
python -m tree_style_terminal --show-info

# Test font scaling without starting GUI
python -m tree_style_terminal --test-fonts

# Test specific DPI settings
python -m tree_style_terminal --test-fonts --dpi 180
```

### Planned Operations (Future)

- **New Child Session**: `Ctrl+Shift+N` - Create a new session as a child of the current session
- **New Sibling Session**: `Ctrl+Alt+N` - Create a new session at the same level as the current session
- **Close Session**: `Ctrl+Shift+W` - Close the current session (children are adopted by parent)
- **Toggle Sidebar**: `Ctrl+Shift+E` - Show/hide the session tree sidebar
- **Navigate Sessions**: Click on sessions in the sidebar or use `Ctrl+PageUp`/`Ctrl+PageDown`

### Session Tree Navigation (Planned)

The sidebar will display terminal sessions in a tree structure:

- **Root Sessions**: Top-level sessions with no parent
- **Child Sessions**: Sessions created from within other sessions
- **Session Adoption**: When you close a session with children, those children become children of the closed session's parent

## Development

### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/tree-style-terminal/tree-style-terminal.git
cd tree-style-terminal
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install system dependencies first (see Installation section above), then install in development mode:
```bash
pip install -e ".[dev]"
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

### Running Tests

```bash
pytest
```

Note: Tests are not yet implemented. This is part of the development roadmap.

### Code Quality

The project uses several tools to maintain code quality:

- **ruff**: Fast Python linter and code formatter
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Static type checking

Run all checks (once implemented):
```bash
ruff check .
black --check .
isort --check-only .
mypy src/
```

## Architecture

Tree Style Terminal follows a clean architecture with clear separation of concerns:

- **Models**: Core domain objects (`TerminalSession`, `SessionTree`)
- **Controllers**: Business logic and event handling
- **Widgets**: GTK3 UI components and terminal integration
- **Resources**: UI definitions, CSS themes, and assets

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).


## Requirements

- Python 3.11+
- GTK 3.0+
- VTE 2.91+
- PyGObject
- PyCairo

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Development Roadmap

For detailed development milestones, see [TODO.md](TODO.md).
