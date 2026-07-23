---
id: TASK-36.10
title: Keep AppImage runtime variables out of host shell sessions
status: next
assignee: []
created_date: '2026-07-23 13:39'
labels:
  - packaging
  - appimage
  - terminal
  - release
  - 'blocker:1.0'
dependencies:
  - TASK-36.1
  - TASK-36.2
references:
  - 'https://docs.appimage.org/packaging-guide/environment-variables.html'
  - 'https://docs.appimage.org/reference/runtime-environment-variables.html'
modified_files:
  - src/tree_style_terminal/widgets/terminal.py
  - src/tree_style_terminal/controllers/session_manager.py
  - tests/test_terminal_widget.py
  - tests/unit/test_session_actions.py
parent_task_id: TASK-36
priority: high
ordinal: 2400
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Introduce a clear environment boundary for AppImage execution. Tree Style Terminal itself must use its bundled Python, GTK, PyGObject, VTE, typelib, and data paths, while shells and workspace commands launched inside VTE must run directly on the host without inheriting AppImage-only library or Python paths. Native Debian and development launches must retain their current behavior.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AppImage launches use the bundled application runtime, but spawned shells and workspace commands do not inherit AppImage-only LD_LIBRARY_PATH, PYTHONHOME, PYTHONPATH, GI_TYPELIB_PATH, GTK module, or bundled data-path entries.
- [ ] #2 The user's configured host shell, PATH, locale, SSH/GPG agent sockets, D-Bus session, working directory, and other ordinary host environment values remain available to terminal sessions without routing through a sandbox bridge.
- [ ] #3 Native Debian, source, and development launches retain their existing process and environment behavior.
- [ ] #4 Environment construction is centralized behind a small testable boundary rather than duplicated across terminal and workspace-session code.
- [ ] #5 Automated tests cover AppImage detection, removal of bundle-only values, preservation of host values, native behavior, workspace commands, and safe fallbacks when expected AppImage variables are absent.
<!-- AC:END -->
