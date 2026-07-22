# Configuration Guide

Tree Style Terminal supports configuration via a YAML file that allows you to customize various aspects of the application.

## Configuration File Location

The configuration file is located at:
```
~/.config/tree-style-terminal/config.yaml
```

The configuration file will be automatically created with default (commented) values when you first run the application.
New configuration files are created with mode `0600`, so only the current user
can read or modify them.

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
  # Draft a shell command from the current editable input
  ai_command_draft: "<Control><Shift>a"
```

**Options:**
- `terminal_search`: Keyboard shortcut that opens search for the active terminal
  - Default: `<Control><Shift>f`
  - Uses GTK accelerator syntax
- `ai_command_draft`: Draft a shell command without submitting it
  - Default: `<Control><Shift>a`
  - Uses GTK accelerator syntax

### AI Command Drafting

AI command drafting is opt-in and uses an OpenAI-compatible Chat Completions
endpoint. Configure all three required values to enable requests:

```yaml
ai:
  endpoint: "https://api.openai.com/v1/chat/completions"
  api_key: "sk-..."
  model: "gpt-5.6-terra"

shortcuts:
  ai_command_draft: "<Control><Shift>a"
```

Type a natural-language request at the active shell prompt, then use the
sparkle button in the header bar or the configured shortcut. The generated
single-line command replaces the editable input but is never submitted; review
or edit it and press Enter yourself.

If the request asks for an explanation or diagnosis rather than an executable
action, the result is inserted as one non-executable shell comment beginning
with `# ` instead of an artificial `printf` or `echo` command.

A normal click or shortcut sends up to 40 recent terminal rows. Right-click the
sparkle button for a one-shot request using 200 rows, 1,000 rows, or explicitly
selected terminal text (limited to its most recent 1,000 lines). The larger
choice applies only to that request and does not change the default.

If `endpoint`, `api_key`, or `model` is missing or empty, no request is made and
the application shows a short configuration hint. The API key is stored as
plain text in `config.yaml`, so keep that file private. Tree Style Terminal does
not write the key, transmitted terminal history, or editable input to its logs.

For each request, the configured provider receives the current editable input
and up to 40 recent terminal lines. This may include commands, output, paths,
hostnames, or other sensitive shell content. Only use the feature with a
provider whose data handling you accept.

## Workspace Profiles

Workspace profiles are self-contained YAML files for creating one or more
startup session trees. They are loaded explicitly and are separate from the normal
`~/.config/tree-style-terminal/config.yaml` file.

When no session is open, **Load Profile** on the welcome screen opens a chooser
for `.yml` and `.yaml` profiles. It starts in the user's home directory by
default. An optional user path (including `~`) can set another initial directory:

```yaml
workspace_profiles:
  default_directory: "~/Documents/workspace-profiles"
```

An unset, empty, missing, or unusable directory falls back to the user's home
directory. The chooser still allows navigation to other directories.

```bash
tst --profile my-java-project.yml
tst -p my-java-project.yml
```

Profile files use format version `1`:

```yaml
version: 1
name: "My Java Project"
workdir: "~/dev/my-java-project"

root:
  title: "project"
  children:
    - title: "server"
      command: "./gradlew bootRun"

    - title: "tests"
      command: "./gradlew test"
      selected: true

    - title: "logs"
      workdir: "build/logs"
```

For multiple independent root sessions, replace `root` with a non-empty `roots`
list:

```yaml
version: 1
workdir: "~/dev"

roots:
  - title: "project"
    workdir: "my-project"
    children:
      - title: "tests"

  - title: "scratch"
    workdir: "/tmp"
```

**Options:**
- `version`: Required profile format version. The current version is `1`.
- `name`: Optional display name for the profile.
- Top-level `workdir`: Optional base directory inherited by all session nodes.
- `root`: One root session node for a single-tree profile.
- `roots`: A non-empty list of root session nodes for a multi-tree profile.
  Exactly one of `root` or `roots` must be present.
- Node `title`: Optional session title. If omitted, normal automatic title generation is used.
- Node `workdir`: Optional working directory for this node and its children.
- Node `command`: Optional command to run in this session.
- Node `selected`: Optional boolean. When `true`, this session is selected after
  the complete profile has started. It may be `true` on at most one node across
  the whole profile; omission means `false`.
- Node `children`: Optional list of child session nodes.

**Working directory resolution:**
- `~` is expanded to the user's home directory.
- Absolute paths are used as-is.
- Relative node paths are resolved against the nearest inherited `workdir`.
- If no `workdir` is specified anywhere, the process start directory is used.
- Missing or unusable working directories are reported as profile validation errors.

When `command` is omitted, the session starts the same normal interactive shell
used by regular new sessions. When `command` is present, it is started through
the user's normal shell in the resolved working directory; after the command
exits, the shell remains available for follow-up interactive work.

`--profile` cannot be combined with a positional startup directory,
`--working-directory`, or `--workdir`.

### Exporting a Workspace Profile

The save button beside the new-sibling, new-child, and close-session controls
opens a menu with two export scopes:

- **Selected Session and Children** writes the selected session and its
  descendants as one `root` tree.
- **All Sessions** writes all current root trees, using `roots` when more than
  one root exists.

After choosing the scope, select the destination `.yml` or `.yaml` file. Export
is always explicit; Tree Style Terminal does not automatically save or restore
session state. The generated profile contains the current titles, working
directories, tree structure, and selection. It does not invent startup
`command` values for already-running sessions.

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
