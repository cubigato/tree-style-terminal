---
id: TASK-36.2
title: Make configuration storage package-safe
status: Done
assignee:
  - Codex
created_date: '2026-07-23 13:16'
updated_date: '2026-07-23 19:39'
labels:
  - packaging
  - configuration
  - release
  - 'blocker:1.0'
dependencies:
  - TASK-36.1
documentation:
  - 'https://specifications.freedesktop.org/basedir-spec/latest/'
modified_files:
  - src/tree_style_terminal/config/manager.py
  - tests/unit/test_config.py
  - README.md
  - CONFIG.md
parent_task_id: TASK-36
priority: high
ordinal: 2200
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ensure native and sandboxed installations preserve user configuration across installs, upgrades, and normal uninstalls without writing outside the appropriate per-user location. Follow the XDG base-directory contract so Debian keeps the existing default path while Flatpak receives isolated persistent storage, and remove import-time filesystem side effects that can interfere with clean package builds and tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Configuration uses an absolute, non-empty XDG_CONFIG_HOME when set and otherwise remains compatible with the existing ~/.config/tree-style-terminal location; relative XDG_CONFIG_HOME values are ignored per the XDG Base Directory Specification.
- [x] #2 Importing the package or constructing the configuration manager creates no user directories or files; the commented configuration template is created only on the first actual configuration load when no file exists.
- [x] #3 Existing native configuration is discovered without being overwritten, and newly introduced defaults merge in memory without discarding user values or rewriting the file.
- [x] #4 Normal Debian and Flatpak upgrades and uninstalls preserve configuration according to each package manager's documented behavior.
- [x] #5 Automated tests cover XDG overrides, first-load creation, existing configuration, permissions, non-writing imports/construction, and failures; user-facing configuration documentation is updated.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Resolve config.yaml beneath an absolute, non-empty XDG_CONFIG_HOME; otherwise use ~/.config. Ignore relative XDG_CONFIG_HOME values as required by the XDG Base Directory Specification.
2. Make path resolution and ConfigManager construction side-effect free. Keep the existing global manager API, but create no directories or files during import/construction.
3. On the first actual load/get with no existing file, create the application directory with mode 0700 and the commented template with mode 0600, then load independent in-memory defaults. Never rewrite an existing file merely to add new defaults.
4. Remove save_config() because production code has no caller and there is currently no configuration UI. Add a purpose-built write API only if a future feature requires it.
5. Preserve and test deep merging of existing user values with new defaults in memory, plus clear ConfigError handling for directory creation, file creation, reads, invalid YAML, and permission failures.
6. Update README.md and CONFIG.md with native/XDG/Flatpak paths, first-load creation behavior, permissions, in-memory default merging, and Debian/Flatpak upgrade/uninstall persistence semantics.
7. Run focused configuration tests, the complete test suite, and `.venv/bin/python -m ruff check src tests`; record verified acceptance criteria and leave the task In Progress for human review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented XDG-aware config path resolution: absolute non-empty XDG_CONFIG_HOME wins; empty, unset, and relative values fall back to ~/.config.

Config imports and ConfigManager construction are now filesystem-side-effect free. The first actual load creates the application directory (0700) and commented template (0600). Existing files are deep-merged with defaults in memory and are not rewritten.

Removed the unused save_config() API after confirming it had no production callers; a future configuration editor can introduce a purpose-built persistence API.

Updated README.md and CONFIG.md with native, Debian, and Flatpak paths and persistence behavior.

Verification: `.venv/bin/python -m pytest tests/unit/test_config.py -q` (41 passed); `.venv/bin/python -m pytest -q` (345 passed); `.venv/bin/python -m ruff check src tests` (clean); `git diff --check` (clean). Ready for human review; status intentionally remains In Progress.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented package-safe, XDG-compliant configuration storage. Config path resolution now honors absolute XDG_CONFIG_HOME values and falls back to ~/.config for unset, empty, or relative values. Imports and ConfigManager construction no longer touch the filesystem; the first actual configuration load creates the private directory and commented template with modes 0700 and 0600. Existing user files remain unchanged while new defaults merge in memory. Removed the unused save_config() API and documented native, Debian, and Flatpak paths and persistence behavior.

Validation: 41 focused configuration tests and 345 full-suite tests passed; Ruff and git diff checks are clean.
<!-- SECTION:FINAL_SUMMARY:END -->
