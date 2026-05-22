# Changelog

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
