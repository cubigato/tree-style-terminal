---
id: TASK-37
title: Load a workspace profile from the welcome screen
status: Done
assignee: []
created_date: '2026-07-22 21:27'
updated_date: '2026-07-22 21:49'
labels:
  - feature
  - 'area:workspace'
  - 'area:ui'
  - 'area:config'
dependencies: []
modified_files:
  - CHANGELOG.md
  - CONFIG.md
  - README.md
  - pyproject.toml
  - src/tree_style_terminal/__init__.py
  - src/tree_style_terminal/config/defaults.py
  - src/tree_style_terminal/main.py
  - src/tree_style_terminal/ui/main_window.ui
  - tests/test_basic.py
  - tests/test_main_window.py
  - tests/unit/test_config.py
priority: medium
ordinal: 500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When Tree Style Terminal starts without --profile and has no open session, add a Load profile button directly below the existing New Terminal button. The button opens a YAML file chooser and loads the selected workspace through the existing profile validation and session-creation path. The chooser starts in the user home directory by default, or in an optional profile directory configured in config.yaml. Keep this as a direct file-loading action rather than adding a profile manager.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The empty welcome screen shows a Load profile button directly below New Terminal, without changing the existing New Terminal behavior.
- [x] #2 The file chooser is limited to YAML profile files while still allowing the user to navigate to another directory.
- [x] #3 The optional config key workspace_profiles.default_directory accepts a user path with tilde expansion; when it is unset, empty, missing, or not a usable directory, the chooser starts in the user home directory.
- [x] #4 Confirming a valid file uses the same parser, validation, multi-root creation, and selected-session behavior as the existing --profile startup path.
- [x] #5 Cancelling the chooser leaves the application on the unchanged welcome screen with no session created.
- [x] #6 Unreadable or invalid profiles show a clear error and leave the welcome screen usable without partially created profile sessions.
- [x] #7 Automated coverage verifies button placement and activation, configured and fallback start directories, successful loading, cancellation, and error handling.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added a welcome-screen Load Profile action for both the Glade and manual fallback UIs. The GTK open chooser uses only .yml/.yaml filters and starts in a usable tilde-expanded workspace_profiles.default_directory, falling back to the user's home. Selected files go through load_workspace_profile before the existing multi-root session creation path; cancellation and validation/read errors leave the welcome page unchanged.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented direct workspace-profile loading from the empty welcome screen, including configurable chooser start directory, YAML filtering, shared validation/session creation, load-specific error feedback, documentation, and automated coverage. Updated CHANGELOG.md and bumped the minor package version from 0.6.0 to 0.7.0 after review. Full suite: 299 passed. Ruff: clean.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 The new configuration key and welcome-screen loading flow are documented in CONFIG.md and README.md.
- [x] #2 Ruff and the relevant unit and GTK integration tests pass.
<!-- DOD:END -->
