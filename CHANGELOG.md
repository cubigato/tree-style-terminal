# Changelog

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
