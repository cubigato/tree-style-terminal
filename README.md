# Tree Style Terminal

A Python/GTK3 terminal application featuring a collapsible tree-based session navigator instead of traditional tabs.
It is roughly inspired by tree-style-tabs add-on for Firefox.

![Tree Style Terminal showing a nested terminal session tree](assets/screenshots/tree-style-terminal.png)
*Tree Style Terminal with hierarchical session organization and a transparent background*

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
- ✅ Optional AI-assisted shell command drafting with review-before-run behavior
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
- **App Diagnostics**: Configure runtime log verbosity
- **Display Scaling**: Configure DPI scaling for high-resolution displays
- **Terminal Settings**: Customize scrollback buffer size
- **UI Settings**: Adjust sidebar width and other interface elements
- **AI Command Drafting**: Configure an OpenAI-compatible endpoint, model, API key, and shortcut

**Example configuration:**
```yaml
theme: "dark"
app:
  log_level: "warning"
display:
  dpi_scale: 2.0  # 200% scaling for 4K displays
ui:
  sidebar_width: 300
terminal:
  scrollback_lines: 20000
ai:
  endpoint: "https://api.openai.com/v1/chat/completions"
  api_key: "sk-..."
  model: "gpt-5.6-terra"
shortcuts:
  ai_command_draft: "<Control><Shift>a"
```

For complete configuration documentation, see [CONFIG.md](CONFIG.md).

AI command drafting sends the current editable input and a bounded portion of
recent terminal history to the configured provider. Use the sparkle button or
configured shortcut to request a draft. The returned command is inserted but
never executed automatically. The integration remains inactive and makes no
request until all required AI settings are present.

Normal requests use up to 40 recent terminal rows. Right-click the sparkle
button to make a one-shot request with 200 rows, 1,000 rows, or selected
terminal text without changing the everyday default.

Explanation and diagnosis requests are inserted as a single shell comment
beginning with `# ` rather than as a command that prints prose.

## Usage

### Basic Application Launch

```bash
# Standard launch with automatic font scaling
tree-style-terminal
# or shorthand
tst
```

### Opening In A Directory

Tree Style Terminal can create the first root session in a requested directory:

```bash
tree-style-terminal /tmp
tree-style-terminal --working-directory /tmp
tree-style-terminal --workdir /tmp
```

Relative paths are resolved from the caller's current working directory. Invalid
paths fail clearly instead of silently falling back to `$HOME`.

### Opening A Workspace Profile

Tree Style Terminal can create a startup session tree from a self-contained YAML
profile file:

```bash
tst --profile examples/workspace-profiles/simple.yml
tst -p examples/workspace-profiles/linux-overview.yml
```

With no session open, the welcome screen also provides a **Load Profile** button.
It opens a chooser limited to `.yml` and `.yaml` files and loads the selected
profile through the same validation and session-creation flow as `--profile`.
The chooser starts in the user's home directory unless
`workspace_profiles.default_directory` is set in `config.yaml`; see
[`CONFIG.md`](CONFIG.md#workspace-profiles).

A profile defines one or more root sessions and optional child sessions. Each
session can set a title, working directory, and optional command:

```yaml
version: 1
name: "Simple Example"
workdir: "/tmp"

root:
  title: "tmp shell"
  children:
    - title: "hello"
      command: "echo hello"
      selected: true
```

Use `roots` instead of `root` to start multiple independent trees:

```yaml
version: 1
workdir: "/tmp"

roots:
  - title: "first"
  - title: "second"
```

Exactly one of `root` or `roots` must be present.

An optional `selected: true` on one node selects that session after the whole
profile has started. At most one node across all roots may be selected.

Sessions without `command` start a normal interactive shell. Sessions with
`command` run it through the user's normal shell, then leave a shell open for
follow-up work. Relative `workdir` values are resolved from the nearest inherited
`workdir`.

Example files are available in
[`examples/workspace-profiles/`](examples/workspace-profiles/):

- [`simple.yml`](examples/workspace-profiles/simple.yml): one root shell in
  `/tmp` with a child that runs `echo hello`
- [`linux-overview.yml`](examples/workspace-profiles/linux-overview.yml):
  a nested tree using common Linux paths such as `/tmp`, `/etc`, `/var/log`,
  and `/usr`

To create a profile from running sessions, use the save button beside the
session controls in the header bar. Choose either the selected session plus its
children or all sessions, then select a YAML destination. Exported profiles are
only written on this explicit action and can be loaded later with `--profile`.

`--profile` cannot be combined with a startup directory or `--workdir`.

This is useful for file manager actions such as "Open Terminal Here". Some file
managers pass the selected directory as an argument, while others start the
terminal process with the target directory as its current working directory. For
the second style, use `.`:

```bash
tree-style-terminal --workdir .
```

#### PCManFM

PCManFM/libfm's advanced "Terminal emulator" setting is one of the file managers
that launches the terminal with the target directory as the process working
directory. Its historical `%s` placeholder is not the folder path for "Open
Current Folder in Terminal"; libfm treats it as an old command-execution
placeholder and may ignore or strip it.

In PCManFM, open `Edit > Preferences > Advanced` and set "Terminal emulator" to:

```bash
/home/you/.local/bin/tree-style-terminal --workdir .
```

Adjust the executable path for your installation. Do not append `%s` for this
PCManFM use case.

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
tree-style-terminal --log-level info    # Show runtime diagnostics for this launch
tree-style-terminal /tmp                # Open one root session in /tmp
tree-style-terminal --workdir .         # Open in the caller's current directory
tree-style-terminal --profile examples/workspace-profiles/simple.yml
tst -p examples/workspace-profiles/linux-overview.yml

# Combined options
tree-style-terminal --dpi 180 --quiet   # Launch with custom DPI, no startup message
tree-style-terminal --show-info --dpi 240  # Test DPI without starting GUI
tree-style-terminal --log-level debug --dpi 192  # Debug launch with custom DPI

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
- **Navigate Sessions**: Click on sessions in the sidebar or use `Alt+Left`/`Alt+Right` or `Ctrl+Shift+Left`/`Ctrl+Shift+Right`
- **Terminal Clipboard**: `Ctrl+Shift+C` / `Ctrl+Shift+V` - Copy/paste in the terminal
- **Terminal Search**: `Ctrl+Shift+F` opens active-terminal search. In the search field, `Enter` jumps to the next match, `Shift+Enter` jumps to the previous match, and `Escape` closes search.

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

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
