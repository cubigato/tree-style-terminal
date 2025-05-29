# TODO — **tree-style-terminal**

A fine-grained roadmap: Each task is small, clearly defined and can be worked on individually – by hand or with AI assistance.

---

## Milestone 0  Bootstrapping & Infrastructure

1. **Repository & Base**

   * [x] Create GitLab project `tree-style-terminal`.
   * [x] Initialize local repo and push first commit.
   * [x] Create `README.md` with project brief description.
2. **License**

   * [x] Add license file (`LICENSE`) (GPL v3).
3. **Python Setup**

   * [x] Create `pyproject.toml` with PEP 621 fields (Name, Version, Authors).
   * [x] Configure `[build-system]` with `requires = ["setuptools>=61.0"]` and `build-backend = "setuptools.build_meta"`.
   * [ ] Add example `setup.cfg` or `setup.py` for pip installation.
4. **Work Environment**

   * [x] Install `uv` and briefly describe in README.
   * [x] Create virtual environment (`python -m venv .venv`).
   * [x] Add dependencies in `pyproject.toml`: `pycairo`, `PyGObject`, `pytest`, `pytest-gtk`, `ruff`, `black`, `isort`, `mypy`.
5. **Code Quality**

   * [-] Configure `pre-commit` with hooks: `ruff`, `black`, `isort`, `mypy`.
6. **CI Scaffolding**

   * [-] Create `.gitlab-ci.yml`.
   * [-] Job `lint`: runs `ruff`, `black --check`, `isort --check`, `mypy`.
   * [-] Job `test`: runs `pytest` (unit tests) via Docker image `python:3.11`.

---

## Milestone 1  Basic GTK Application

1. **Project Structure**

   * [x] Create `src/tree_style_terminal/`.
   * [x] Create `__init__.py` and `main.py`.
2. **Gtk.Application & Window**

   * [x] Define `Gtk.Application` class in `main.py`.
   * [x] Initialize `MainWindow` (inheriting from `Gtk.ApplicationWindow`) with `HeaderBar`.
   * [x] `python -m tree_style_terminal` starts empty window.
3. **GtkBuilder Layout**

   * [x] Create `ui/main_window.ui` with Glade or manually.
   * [x] Integrate HeaderBar + central `Gtk.Box` placeholder.
   * [x] Implement loading of UI file in `main.py`.
4. **Wayland/X11 Test**

   * [x] Start app under X11 and briefly check functionality.
   * [-] Start app under Wayland and check.

---

## Milestone 2  Terminal Embedding

1. **VTE Dependency**

   * [x] Install `gir1.2-vte-2.91` (GTK3)
2. **Terminal Widget**

   * [x] Create file `widgets/terminal.py`.
   * [x] Define class `VteTerminal(Gtk.Widget)` that embeds `Vte.Terminal`.
3. **Spawn Function**

   * [x] Implement method `spawn_shell(self, argv=None)`, uses `spawn_sync()`.
   * [x] `$SHELL` as default, fallback `/bin/bash`.
4. **Layout Integration**

   * [x] Place terminal widget centrally in `MainWindow`.
   * [x] Start application → terminal is displayed.
5. **Basic Configuration**

   * [x] Add methods for font size and scrollback length (set via property).
   * [x] Unit test: Terminal widget instantiable without error message.

---

## Milestone 3  Domain Model & Sessions

1. **Session Object**

   * [ ] `models/session.py`: `@dataclass TerminalSession` with fields `pid`, `pty_fd`, `cwd`, `title`, `children`.
   * [ ] `__post_init__` initially sets `title` to `cwd`.
2. **SessionTree**

   * [ ] `models/tree.py`: Class `SessionTree`, holds root nodes and methods `add_node`, `remove_node`.
   * [ ] Implement adoption: When removing, parent adopts the children.
3. **Unit Tests**

   * [ ] Scenario: Remove root with children → children become new roots.
   * [ ] Scenario: Remove leaf → no side effects.
   * [ ] Scenario: Deep nesting removed → structure remains consistent.

---

## Milestone 4  Sidebar Tree Navigator

1. **TreeStore Setup**

   * [ ] In `controllers/sidebar.py` `Gtk.TreeStore` with columns \[`object`, `title`].
   * [ ] Bind `SessionTree` events (`node-added`, `node-removed`) to TreeStore updates.
2. **Gtk.TreeView**

   * [ ] `widgets/sidebar.py`: Class `SessionSidebar(Gtk.Box)` with `Gtk.TreeView`.
   * [ ] Display column for `title`.
3. **Revealer & Paned**

   * [ ] Layout in `MainWindow`: `Gtk.Paned` with sidebar and terminal area.
   * [ ] `Gtk.Revealer` to make sidebar collapsible.
   * [ ] Button in HeaderBar for expanding/collapsing.
4. **Selection & Focus**

   * [ ] Callback for row selection: Focus switches to corresponding `TerminalSession`.
   * [ ] Show active session in terminal area.

---

## Milestone 5  Session Control & Shortcuts

1. **Define Actions**

   * [ ] Create `new_sibling`, `new_child`, `close_session` in `controllers/shortcuts.py`.
2. **ShortcutController**

   * [ ] Set up `Gtk.ShortcutController`, map key combinations to actions.
3. **UI Integration**

   * [ ] Buttons in HeaderBar or Toolbar for new and close.
   * [ ] Connect actions with tree and terminal controller.
4. **Test Behavior**

   * [ ] `new_child` under active session creates child node.
   * [ ] `close_session` removes node and adopts children.

---

## Milestone 6  Theming & Packaging Base

1. **CSS Foundation**

   * [ ] `resources/css/style.css` with variables for Light/Dark.
   * [ ] Load CSS in `main.py`.
2. **pip Wheel**

   * [ ] Configure `setup.cfg` or `pyproject.toml` so that `pip wheel .` works.
   * [ ] GitLab CI job `wheel`: artifact `tree-style-terminal-*.whl`.

---

## Milestone 7  Debian Package

1. **Debian Directory**

   * [ ] Initially create `debian/control`, `debian/rules`, `debian/changelog`.
2. **Build Scripts**

   * [ ] Add `dpkg-buildpackage -us -uc` as job in GitLab CI.
3. **Test Installation**

   * [ ] Dockerfile for Debian Stable: Install `.deb` → test startup.

---

## Milestone 8  Flatpak Package

1. **Manifest**

   * [ ] `flatpak/tree-style-terminal.json` with runtime `org.gnome.Platform 45`.
2. **Build**

   * [ ] GitLab CI job `flatpak` for x86\_64 & aarch64 via `flatpak-builder`.

---

## Milestone 9  Quality Assurance

* [ ] Unit test coverage ≥ 80%.
* [ ] Integration smoke tests with `pytest-gtk` + `xvfb-run`.
* [ ] Lint & format checks in CI green light.
* [ ] `mypy --strict` successful.

---

## Milestone 10  First Release

* [ ] Fill `CHANGELOG.md`.
* [ ] Git tag `v0.1.0`.
* [ ] Publish wheel on PyPI.
* [ ] Publish Debian package in GitLab Package Registry.
* [ ] Submit Flatpak to Flathub Beta.

---

### Backlog / Nice-to-Have

* [ ] Session persistence across restart.
* [ ] Per-session environment variables.
* [ ] Tmux-like split panes.
* [ ] Scrollback search & regex filter.
* [ ] Plugin API via `entry_points` and `importlib.metadata`.
