# Architecture Overview

**tree-style-terminal** is a Python/GTK3 terminal application. Instead of tabs,
it shows sessions as an infinitely nestable tree in a collapsible sidebar.

This document describes the *working* architecture. A short
[Roadmap](#roadmap) at the end lists things that are intentionally not built yet.

---

## 1  Goals

* **Tab-less UX:** sessions form a nestable tree shown in a hideable sidebar.
* **Minimal core dependencies:** PyGObject + VTE + a small amount of pure Python.
* **Idiomatic modern Python:** type hints, `ruff`, `mypy`, `pyproject`-based build.
* **Incremental growth:** clear layering and test coverage.

---

## 2  Technology Stack

| Layer           | Choice                                  | Notes                                                        |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| GUI toolkit     | GTK 3 via `PyGObject` (`Gtk 3.0`)       | Native Wayland & X11, CSS theming.                           |
| Terminal widget | VTE via `gi.require_version('Vte', '2.91')` | Same engine as GNOME Terminal; C library, isolated from Python. |
| Config          | `PyYAML`                                | YAML config in `config/`.                                    |
| Packaging       | `setuptools` + `pyproject.toml`         | PEP 517/518; static version field.                           |
| Testing         | `pytest`                                | Unit tests for model/controller logic, UI smoke tests.       |
| Linting         | `ruff`, `black`, `isort`, `mypy`        | See `pyproject.toml` for the active rule set.                |

---

## 3  High-Level Component Diagram

```
+---------------------------------------------------------------+
| MainWindow (Gtk.ApplicationWindow)                            |
|                                                               |
|  +--------SidebarPane--------+  +-------TerminalPane--------+  |
|  | Gtk.Revealer (collapsible)|  | Vte.Terminal (active)     |  |
|  |  -> Gtk.TreeView          |  |                           |  |
|  +---------------------------+  +---------------------------+  |
+---------------------------------------------------------------+
```

`MainWindow` (`main.py`) wires the model, controllers, and widgets together.
It owns the `SessionManager` and `SidebarController` and connects them via
callbacks (see [§5](#5--data--event-flow)).

---

## 4  Core Objects

| Object               | Module                          | Responsibility                                                                 |
| -------------------- | ------------------------------- | ------------------------------------------------------------------------------ |
| `TerminalSession`    | `models/session.py`             | Plain dataclass: pid, pty_fd, cwd, children, and title logic (auto vs. custom). |
| `SessionTree`        | `models/tree.py`                | Parent/child relationships; adoption when a node is removed.                   |
| `SessionManager`     | `controllers/session_manager.py`| Create/close/select sessions; owns the VTE widget per session; fires callbacks. |
| `SidebarController`  | `controllers/sidebar.py`        | Mirrors the session tree into a `Gtk.TreeStore`.                               |
| `ShortcutController` | `controllers/shortcuts.py`      | Registers `Gio.SimpleAction`s and binds keys via `Gtk.AccelGroup`.             |
| `VteTerminal`        | `widgets/terminal.py`           | Wrapper around `Vte.Terminal` (spawn shell, theme, clipboard, search, title).  |
| `SessionSidebar`     | `widgets/sidebar.py`            | The `Gtk.TreeView` widget; handles selection and rename interactions.          |

Note: the domain objects are plain Python classes and **do not emit GObject
signals**. Coordination happens through `SessionManager` callbacks and direct
method calls.

### Adoption algorithm

When a node is removed, its children are re-parented to its parent (or become
roots if it was a root):

```
remove(node):
    parent = node.parent
    for child in node.children:
        child.parent = parent   # adopt (or promote to root)
    detach node
```

Implemented in `SessionTree.remove_node`.

---

## 5  Data & Event Flow

The flow is **callback-based**. `MainWindow._setup_session_callbacks` registers
four callbacks on the `SessionManager`, each of which updates the
`SidebarController`:

1. **User action** (shortcut/menu) -> `ShortcutController` activates a `Gio` action
   -> `SessionManager.new_child()` / `new_sibling()` / `close_current_session()`.
2. `SessionManager.new_session()` creates a `VteTerminal`, spawns the shell,
   creates a `TerminalSession`, and calls `SessionTree.add_node(...)`.
3. `SessionManager` invokes its callbacks; `MainWindow` forwards them to the
   `SidebarController`:
   * `session_created` -> `SidebarController.add_session(...)`
   * `session_closed`  -> `SidebarController.remove_session_with_adoption(...)`
   * `session_changed` -> `SidebarController.update_session(...)`
   * `session_selected`-> sidebar selection / terminal raise
4. When a shell exits, `Vte.Terminal` emits `child-exited` ->
   `SessionManager._on_terminal_exited` -> `close_session(...)` (which triggers
   adoption and the `session_closed` callback).
5. VTE `window-title-changed` -> `SessionManager._on_terminal_title_changed`
   updates the session's cwd/automatic title and fires `session_changed`.

---

## 6  Directory Layout

```
src/tree_style_terminal/
├─ __init__.py
├─ __main__.py            # `python -m tree_style_terminal`
├─ main.py                # Gtk.Application + MainWindow
├─ css_loader.py          # CSS / theme loading
├─ config/
│   ├─ defaults.py
│   └─ manager.py
├─ models/
│   ├─ session.py
│   └─ tree.py
├─ controllers/
│   ├─ session_manager.py
│   ├─ sidebar.py
│   └─ shortcuts.py
├─ widgets/
│   ├─ terminal.py        # VTE wrapper
│   └─ sidebar.py         # TreeView widget
├─ ui/
│   └─ main_window.ui     # GtkBuilder XML
└─ resources/
    └─ css/
tests/                    # unit/, ui/, integration/
```

---

## 7  Error Handling & Logging

* Standard library `logging` at DEBUG/INFO/WARN/ERROR levels.
* `SessionManager` and the controllers catch and log operation errors so a
  single failing session does not crash the application.

---

## 8  Packaging

* Pure-Python wheel (no compiled extensions); GTK3/VTE are system runtime
  dependencies. Console scripts: `tree-style-terminal` and `tst`.
* Static version field in `pyproject.toml`.

---

## Roadmap

Planned, not yet implemented:

* **CI/CD:** currently a lint-only GitLab CI job; planned to add `pytest`
  (with xvfb), `.deb` packaging, and Flatpak builds.
* **Packaging targets:** `.deb` and Flatpak distribution.
* **Plugin system:** entry points discovered via `importlib.metadata`.
* **Session persistence:** save/restore the tree under `$XDG_STATE_HOME`.
* **Terminal features:** split panes, scrollback search improvements, OSC 8
  clickable paths.
