# Tree Style Terminal

Tree Style Terminal is a GTK 3 terminal emulator that organizes sessions in a
collapsible tree instead of a row of tabs. It is inspired by the Tree Style Tab
extension for Firefox.

![Tree Style Terminal showing a nested terminal session tree](assets/screenshots/tree-style-terminal.png)

Current work and planned changes are tracked on the repository's
[Backlog.md board](backlog/tasks/).

## Features

- Nested terminal sessions with multiple independent root trees
- Collapsible sidebar with keyboard and mouse navigation
- Native VTE terminals using the normal user shell environment
- Workspace profile import and export
- Launch in a requested working directory
- Terminal search, configurable shortcuts, and automatic session naming
- Light and dark themes, transparency, and DPI scaling
- Optional review-before-run AI command drafting

## Installation

### Debian package (recommended)

Install a downloaded release package with APT:

```sh
sudo apt install ./tree-style-terminal_*_all.deb
```

To build the package from a checkout:

```sh
make deb
sudo apt install ./build/debian/tree-style-terminal_*_all.deb
```

See [PACKAGING.md](PACKAGING.md) for build verification, package contents, and
release details.

### uv tool install

As an alternative, install directly from a checkout:

```sh
uv tool install .
```

This route expects a compatible GTK 3, VTE, and PyGObject runtime on the host.
The Debian package is preferred on Debian-based systems because it resolves the
native runtime through APT.

Both installation methods provide:

```text
tree-style-terminal
tst
```

## Usage

Start the application:

```sh
tree-style-terminal
# or
tst
```

Open the first session in a requested directory:

```sh
tst /tmp
tst --workdir .
```

Load a workspace profile:

```sh
tst --profile examples/workspace-profiles/simple.yml
tst -p examples/workspace-profiles/linux-overview.yml
```

Profiles can contain nested sessions, multiple root trees, working directories,
titles, commands, and an initially selected session. They can also be loaded
and exported through the application UI. See
[CONFIG.md](CONFIG.md#workspace-profiles) for the profile format.

Other command-line options, including DPI and logging overrides, are listed by:

```sh
tst --help
```

## Configuration

The native configuration file is:

```text
~/.config/tree-style-terminal/config.yaml
```

An absolute `XDG_CONFIG_HOME` changes the base directory. A commented template
is created when configuration is first loaded.

See [CONFIG.md](CONFIG.md) for themes, transparency, DPI scaling, shortcuts,
workspace profiles, logging, and AI command drafting.

AI command drafting is disabled until an endpoint, model, and API key are
configured. It sends terminal context to the configured provider and inserts
the returned command for review; it never executes the command automatically.

## Common shortcuts

- `Ctrl+Alt+T`: new child session
- `Ctrl+Shift+T`: new sibling session
- `Ctrl+Q`: close the current session
- `F9` or `Ctrl+Shift+O`: toggle the sidebar
- `Ctrl+Shift+S`: focus the sidebar
- `Alt+Left` / `Alt+Right`: navigate between sessions
- `Ctrl+Shift+C` / `Ctrl+Shift+V`: terminal copy and paste
- `Ctrl+Shift+F`: search the active terminal

Shortcuts that are configurable are documented in [CONFIG.md](CONFIG.md).

## Development

Create the development environment:

```sh
uv sync --extra dev
```

Run the project checks:

```sh
make test
make lint
```

Build and exercise the Debian package in a clean Podman environment:

```sh
make deb-check
```

## Project documentation

- [Configuration and workspace profiles](CONFIG.md)
- [Packaging and release workflow](PACKAGING.md)
- [Changelog](CHANGELOG.md)
- [Backlog and roadmap](backlog/tasks/)

## Author and contact

- Author: Jannik Winkel
- Copyright: cubigato GmbH
- Contact: [cubigato.de imprint](https://cubigato.de/impressum/)

## License

Tree Style Terminal is licensed under the
[Apache License 2.0](LICENSE).
