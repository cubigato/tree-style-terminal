---
id: TASK-36.2
title: Make configuration storage package-safe
status: next
assignee: []
created_date: '2026-07-23 13:16'
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
- [ ] #1 Configuration uses XDG_CONFIG_HOME when set and otherwise remains compatible with the existing ~/.config/tree-style-terminal location.
- [ ] #2 Importing the package or constructing the configuration manager does not create user directories or files; storage is created only when required for a write.
- [ ] #3 Existing native configuration is discovered without being overwritten, and newly introduced defaults merge without discarding user values.
- [ ] #4 Normal Debian and Flatpak upgrades and uninstalls preserve configuration according to each package manager's documented behavior.
- [ ] #5 Automated tests cover XDG overrides, first-run creation, existing configuration, permissions, and non-writing imports; user-facing configuration documentation is updated.
<!-- AC:END -->
