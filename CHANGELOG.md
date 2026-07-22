# Changelog

## 0.8.0 - 2026-07-23

### Added

- Add opt-in AI-assisted shell command drafting through a configurable shortcut and a theme-aware sparkle button.
- Add temporary context choices for the last 200 or 1000 terminal rows, or the current selection.
- Render explanatory AI responses as non-executable shell comments and show a spinner while requests are running.

### Changed

- Include bounded terminal input and output as context while keeping generated commands reviewable and preventing automatic submission.
- Create new configuration files with user-only permissions.
- Move AI UI and request orchestration into a dedicated controller to keep `MainWindow` focused.

### Fixed

- Capture current VTE terminal text reliably across supported VTE API variants.

## 0.7.0 - 2026-07-22

### Added

- Added a **Load Profile** action to the empty welcome screen that validates and
  creates `.yml` and `.yaml` workspace profiles through the existing startup
  profile flow.
- Added `workspace_profiles.default_directory` to choose the profile dialog's
  initial directory, with tilde expansion and fallback to the user's home.

### Fixed

- Isolated nested configuration defaults with deep copies so runtime changes to
  loaded configuration cannot mutate the global defaults.

## 0.6.0 - 2026-07-22

### Added

- Added workspace profiles with multiple independent root session trees through
  the top-level `roots` list while keeping existing single-root profiles valid.
- Added explicit workspace profile export from the header bar for either the
  selected session subtree or all current sessions.
- Added optional `selected: true` profile nodes to choose the active session
  after the complete profile has started.

### Changed

- Workspace profile exports preserve the current tree structure, titles,
  working directories, and selection without inventing startup commands.
- Profile files are written atomically so a failed export does not damage an
  existing destination file.

## 0.5.0 - 2026-06-08

### Added

- Added self-contained workspace profile YAML files for startup session trees.
- Added `--profile` / `-p` startup support for loading workspace profiles.
- Added nested workspace session creation with inherited working directories.
- Added optional profile commands that run through the user's normal shell.
- Added workspace profile documentation and example profile files.
- Added startup directory support via positional path, `--working-directory`, and `--workdir`.

### Fixed

- Fixed selecting the first character in a terminal line.

### Changed

- Improved sidebar width bounds so resizing keeps a useful terminal area.
- Retired legacy main-window terminal management paths and removed obsolete debug/spike files.

## 0.4.2 - 2026-05-28

### Added

- Added terminal search with shortcut support.
- Added fuzzy matching for terminal search.
- Added session rename and title lock actions.
- Added text drag-and-drop support for terminals.
- Added OSC8 hyperlink detection and link actions through VTE.

### Changed

- Migrated runtime diagnostics to Python logging with configurable `log_level`.
- Extracted CSS loading into a dedicated `CSSLoader` module.
- Standardized tests on package imports.

## 0.4.1 - 2026-05-27

### Fixed

- Fixed terminal focus after switching sessions with the mouse.

## 0.4.0 - 2026-05-26

### Added

- Added keyboard shortcuts for session navigation, focus switching, and terminal clipboard operations.

### Fixed

- Fixed duplicate sidebar controls and removed an unused sidebar menu button.
- Fixed child and sibling session creation so new terminals inherit the selected session's current working directory without echoing helper commands into the terminal.
- Fixed sidebar selection synchronization after creating or switching sessions.
- Fixed recursive sidebar selection callbacks that could spam session-switch messages and crash with `RecursionError`.

### Changed

- Changed the project license to Apache License 2.0.
- Updated README status, keyboard shortcut, installation, theming, and development documentation.
- Bumped the package version to 0.4.0.

## 0.3.0 - 2026-05-22

### Added

- Added terminal context menu with copy, paste, and select-all actions.
- Added default terminal copy/paste shortcuts: `Ctrl+Shift+C` and `Ctrl+Shift+V`.
- Added terminal session directory tracking so child sessions can inherit a useful working directory.
- Added runtime sidebar transparency CSS so the session sidebar follows terminal transparency.
- Added developer guidance to use the project virtual environment for Python commands.

### Fixed

- Fixed sidebar transparency in GTK by clearing opaque backgrounds on nested sidebar widgets.
- Fixed a theme toggle ordering bug where the sidebar could stay on the previous light/dark theme while the rest of the UI switched.

### Changed

- Improved installation documentation for PyGObject and native GTK dependencies.
- Closed the sidebar transparency bug report with implementation and test details.
