---
id: TASK-36.11
title: Build and self-publish a production-ready AppImage
status: next
assignee: []
created_date: '2026-07-23 13:40'
updated_date: '2026-07-23 23:39'
labels:
  - packaging
  - appimage
  - release
  - 'blocker:1.0'
dependencies:
  - TASK-36.1
  - TASK-36.2
references:
  - 'https://docs.appimage.org/packaging-guide/introduction.html'
  - 'https://docs.appimage.org/packaging-guide/from-source/native-binaries.html'
  - 'https://docs.appimage.org/reference/best-practices.html'
  - 'https://docs.appimage.org/packaging-guide/distribution.html'
modified_files:
  - packaging/appimage/AppRun
  - packaging/appimage/README.md
  - packaging/appimage/
  - Makefile
  - src/tree_style_terminal/widgets/terminal.py
  - src/tree_style_terminal/controllers/session_manager.py
  - tests/test_terminal_widget.py
  - tests/unit/test_session_actions.py
  - README.md
  - PACKAGING.md
parent_task_id: TASK-36
priority: high
ordinal: 2400
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provide the complete portable AppImage required for 1.0 as one end-to-end packaging task. The artifact must bundle the application runtime while terminal sessions and workspace commands use the ordinary host shell environment without AppImage-only contamination. Build, validation, documentation, and a manual direct-download release path remain under cubigato's control; GitLab CI automation and application-catalog submission are explicitly out of scope.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A versioned and reviewable AppDir recipe builds the AppImage from a clean checkout in a pinned, documented baseline environment, with build tools and external inputs fixed to immutable versions or commits and verified by checksum.
- [ ] #2 The AppImage contains the required Python 3.11+, application package, PyYAML, PyGObject, GTK3, VTE, GI typelibs, schemas, loaders, shared desktop assets, and applicable license notices, and runs on a supported clean system without those application dependencies installed.
- [ ] #3 The application uses its bundled runtime, while terminal sessions and workspace commands start the real host shell in the requested working directory without inheriting AppImage-only library, Python, typelib, module, or data paths; ordinary host environment values remain available and native Debian and development launches remain unchanged.
- [ ] #4 Automated coverage verifies the AppImage environment boundary and failure fallbacks, and clean-environment smoke coverage starts the artifact, exercises a host command and requested working directory, and exits cleanly on the documented X11 and Wayland support matrix.
- [ ] #5 Documentation defines the supported glibc, distribution, and CPU baseline; FUSE expectations and extract-and-run fallback; security model; configuration persistence; desktop-integration limitations; verification; and uninstall procedure.
- [ ] #6 The documented manual release workflow produces a directly downloadable versioned AppImage, SHA-256 checksum, and bundled-component/license inventory without requiring GitLab CI, AppImageHub, or another catalog.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-07-24: Absorbed TASK-36.10. AppImage environment isolation is only meaningfully implemented and verified against the real AppRun/AppDir, so it is part of this single deliverable rather than a prerequisite.
<!-- SECTION:NOTES:END -->
