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

This project is in early development (Milestone 0-1). The core application is not yet functional. Currently available:

- ✅ Project structure and configuration
- ✅ Architecture documentation
- ✅ Development environment setup
- ⏳ Basic GTK application (in progress)
- ❌ Terminal embedding
- ❌ Session management
- ❌ Tree-based navigation

See [TODO.md](TODO.md) for detailed development milestones.

## Planned Installation (Future)

Once the application is functional, installation will be:

### System Dependencies

**Ubuntu/Debian:**
```bash
apt install python3-dev libgirepository1.0-dev libcairo2-dev pkg-config
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

```bash
git clone https://github.com/tree-style-terminal/tree-style-terminal.git
cd tree-style-terminal
pip install -e ".[dev]"
```

## Planned Usage (Future)

### Basic Operations (Planned)

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

3. Install in development mode:
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Development Roadmap

**Current Phase (Milestone 0-1):**
- [ ] Complete basic infrastructure setup
- [ ] Implement basic GTK application
- [ ] Create minimal terminal embedding

**Future Features:**
- [ ] Tree-based session management
- [ ] Collapsible sidebar navigation
- [ ] Session adoption algorithm
- [ ] Split panes (horizontal/vertical)
- [ ] Session templates and profiles
- [ ] Scrollback search and hyperlink navigation
- [ ] OSC 8 support for clickable paths
- [ ] Plugin system
- [ ] Configuration GUI
- [ ] Session export/import
- [ ] Remote session support

For detailed development milestones, see [TODO.md](TODO.md).
