# Architecture Overview

This document outlines the initial architecture of **tree-style-terminal** – a Python/GTK3 terminal application featuring a collapsible tree‑based session navigator instead of traditional tabs.

---

## 1  Goals

* **Tab‑less UX:** Represent sessions as an infinitely nestable tree shown in a hideable sidebar.
* **Minimal core dependencies:** PyGObject + VTE + pure-Python libs (open to adding other optional dependencies as needed).
* **Idiomatic modern Python:** type hints, ruff, mypy, pyproject‑only build.
* **Incremental growth:** clear layering and test coverage so features can be added step‑by‑step.

---

## 2  Technology Stack

| Layer           | Choice                                                                                 | Notes                                                                                    |
| --------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| GUI toolkit     | **GTK 3** via `PyGObject`                                                              | Native Wayland & X11, modern widgets, CSS theming.                                       |
| Terminal widget | **VTE ≥ 0.70**                                                                         | Same engine as GNOME Terminal; compiled C library – performance is isolated from Python. |
| Packaging       | `pyproject.toml`), setuptools/pip (`setup.cfg` or `setup.py`), or venv-based workflows | PEP 517/518 compatible; supports classic pip installs and optional Poetry-driven builds. |
| Testing         | **pytest + pytest‑gtk**                                                                | Unit tests for model logic, smoke tests for UI.                                          |
| Linting         | **ruff, black, isort, mypy**                                                           | Enforced by pre‑commit.                                                                  |
| CI/CD           | **GitLab CI**                                                                          | Lint, test, build `.deb` package, Flatpak, and nightly wheels.                           |

---

## 3  High‑Level Component Diagram

```
+───────────────────────────────────────────────────────────────+
| MainWindow (Gtk.ApplicationWindow)                            |
|                                                               |
|  +────────SidebarPane────────+  +───────TerminalPane────────+ |
|  | Gtk.Revealer (collapsible)|  | Vte.Terminal (active)     | |
|  |  └── Gtk.TreeView         |  | Overlay for status popups | |
|  +───────────────────────────+  +────────────────────────────+ |
+───────────────────────────────────────────────────────────────+
```

---

## 4  Core Domain Objects

| Object                          | Responsibility                                                                                | Signals/Callbacks                                        |
| ------------------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `TerminalSession` (`dataclass`) | Holds PTY handle, pid, cwd, custom title, creation time, list of children.                    | `closed`, `cwd-changed`, `title-changed`                 |
| `SessionTree`                   | Maintains parent/child relationships, implements *adoption* algorithm when a node is removed. | `node-added`, `node-removed`, `structure-changed`        |
| `SessionManager`                | High‑level API to create/close sessions and query current selection.                          | delegates to `SessionTree`; owns default shell selection |
| `SidebarController`             | Syncs `SessionTree` with `Gtk.TreeStore` & handles rename / selection events.                 | n/a                                                      |
| `ShortcutController`            | Central registry for `Gtk.ShortcutController` actions & keybindings.                          | n/a                                                      |

### Adoption Algorithm (pseudo)

```
close(node):
    parent = node.parent
    for child in node.children:
        child.parent = parent  # adopt
    delete node
```

---

## 5  Data & Event Flow

1. **User Action** → `SessionManager.new_child()/new_sibling()`
2. `Vte.Terminal.spawn_async()` starts PTY → returns pid & PTY fd.
3. `SessionTree.add()` emits `node-added` → `SidebarController` inserts row in `Gtk.TreeStore`.
4. When PTY exits, VTE emits `child-exited` → `SessionManager.close()` → `SessionTree.remove()` (adoption) → sidebar update.
5. Sidebar row activation sets `current_session` → brings linked `TerminalPane` to front.

---

## 6  Directory Layout (proposed)

```
tree-style-terminal/
│
├─ src/tree-style-terminal/
│   ├─ __init__.py
│   ├─ main.py              # Gtk.Application entry‑point
│   ├─ ui/
│   │   └─ main_window.ui    # GtkBuilder XML
│   ├─ models/
│   │   ├─ session.py
│   │   └─ tree.py
│   ├─ controllers/
│   │   ├─ sidebar.py
│   │   └─ shortcuts.py
│   ├─ widgets/
│   │   ├─ terminal.py       # VTE wrapper + helpers
│   │   └─ sidebar.py        # Collapsible TreeView widget
│   └─ resources/
│       └─ css/
├─ tests/
│   ├─ unit/
│   └─ ui/
├─ pyproject.toml
└─ README.md
```

---

## 7  Error Handling & Logging

* Use `logging` (switchable to `structlog` for JSON) at **DEBUG/INFO/WARN/ERROR** levels.
* Catch critical exceptions in `main.py` and show `Gtk.MessageDialog`.

---

## 8  Packaging & Distribution

* **Pure Python wheel** (no compiled extensions) + dynamic libvte runtime dependency.
* **Packaging priority:** pip (PEP 517/518), optional `.deb` for Debian-based distros, then Flatpak (X11-first with Wayland support).
* Versioning via **setuptools\_scm**, or manually maintained version field in `pyproject.toml` (compatible with pip/uv workflows).

---

## 9  Continuous Integration

* **ruff**, **black**, **isort**, **mypy** in *lint* job.
* **pytest** (with xvfb‑run) in *test* job.
* **.deb packaging job** using `dpkg-buildpackage`.
* **Flatpak build** matrix for x86\_64 & aarch64 using `flatpak-builder`.

---

## 10  Extensibility Hooks

* **Plugin entry points:** `tree-style-terminal.plugins` discovered via `importlib.metadata`.
* **Session persistence:** JSON file under `$XDG_STATE_HOME/tree-style-terminal/sessions.json`.
* **Theming:** GTK CSS bundled under `resources/css`. Users may override via settings.

---

## 11  Future Directions

* Split panes (row/column) like tmux.
* Scrollback search + hyperlink navigation.
* OSC 8 compatibility for clickable paths.
* GPU‑accelerated rendering experiment using WebKitGTK + xterm.js.
