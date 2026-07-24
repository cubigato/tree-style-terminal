---
id: TASK-36.11
title: Build and self-publish a production-ready AppImage
status: Done
assignee:
  - Codex
created_date: '2026-07-23 13:40'
updated_date: '2026-07-24 00:50'
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
  - Makefile
  - PACKAGING.md
  - README.md
  - packaging/appimage/AppRun
  - packaging/appimage/Containerfile
  - packaging/appimage/Containerfile.smoke
  - packaging/appimage/README.md
  - packaging/appimage/build.sh
  - packaging/appimage/container-build.sh
  - packaging/appimage/debian.sources
  - packaging/appimage/fontconfig-appimage.conf
  - packaging/appimage/smoke.sh
  - src/tree_style_terminal/runtime_environment.py
  - src/tree_style_terminal/widgets/terminal.py
  - tests/test_terminal_widget.py
  - tests/unit/test_runtime_environment.py
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
- [x] #1 A versioned and reviewable AppDir recipe builds the AppImage from a clean checkout in a pinned, documented baseline environment, with build tools and external inputs fixed to immutable versions or commits and verified by checksum.
- [x] #2 The AppImage contains the required Python 3.11+, application package, PyYAML, PyGObject, GTK3, VTE, GI typelibs, schemas, loaders, shared desktop assets, and applicable license notices, and runs on a supported clean system without those application dependencies installed.
- [x] #3 The application uses its bundled runtime, while terminal sessions and workspace commands start the real host shell in the requested working directory without inheriting AppImage-only library, Python, typelib, module, or data paths; ordinary host environment values remain available and native Debian and development launches remain unchanged.
- [x] #4 Automated coverage verifies the AppImage environment boundary and failure fallbacks, and clean-environment smoke coverage starts the artifact, exercises a host command and requested working directory, and exits cleanly on the documented X11 and Wayland support matrix.
- [x] #5 Documentation defines the supported glibc, distribution, and CPU baseline; FUSE expectations and extract-and-run fallback; security model; configuration persistence; desktop-integration limitations; verification; and uninstall procedure.
- [x] #6 The documented manual release workflow produces a directly downloadable versioned AppImage, SHA-256 checksum, and bundled-component/license inventory without requiring GitLab CI, AppImageHub, or another catalog.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Verify the current application entry points, resource installation, native dependencies, and release-version sources; choose and document the oldest practical Linux build baseline and pinned AppImage tooling.
2. Add a rootless Podman-based one-command AppImage build that creates a complete AppDir from a clean read-only checkout, bundles Python/GTK/PyGObject/VTE and required runtime data, and writes all artifacts under build/appimage/.
3. Add an AppRun boundary that starts the bundled GUI runtime but supplies terminal sessions and workspace commands with a sanitized host environment; centralize the environment construction and cover native and AppImage behavior with unit tests.
4. Add deterministic validation: metadata/resource checks, AppDir and extract-and-run smoke tests, host-shell/cwd/environment checks, checksums, and a bundled-component/license inventory; exercise graphical startup under the available disposable display environment.
5. Document supported systems, X11/Wayland expectations, FUSE and extract-and-run usage, configuration persistence, desktop integration, verification, uninstall, and the manual direct-download release procedure.
6. Run the complete Python test suite, Ruff, clean AppImage build, and package checks; record verified acceptance criteria and leave the task In Progress for human review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-07-24: Absorbed TASK-36.10. AppImage environment isolation is only meaningfully implemented and verified against the real AppRun/AppDir, so it is part of this single deliverable rather than a prerequisite.

2026-07-24: Implementation started after the user explicitly requested proceeding directly. The task will use the existing Podman pattern so a clean AppImage build remains a one-command local workflow.

2026-07-24: Implemented the rootless Podman AppImage workflow on a pinned Debian 12 snapshot. `make appimage` emits the versioned x86_64 AppImage, SHA-256 file, and bundled-component/license inventory under `build/appimage/`; `make appimage-check` additionally validates metadata and runs the artifact in a clean dependency-free smoke image.

2026-07-24: The GUI uses the bundled Python/GTK/VTE/GI/Fontconfig runtime. VTE now receives an exact sanitized environment with `SPAWN_NO_PARENT_ENVV`, restoring original host values while removing AppImage-only paths and variables from shells and workspace commands.

2026-07-24: Verified from a clean build: X11 via Xvfb, Wayland via headless Weston, extract-and-run fallback, requested cwd, host command execution, environment preservation/isolation, checksum, shell syntax, normal host FUSE execution, 350 Pytest tests, and Ruff. Task remains In Progress pending human review per project policy.

2026-07-24: Fixed the post-review Fontconfig warning caused by applying the read-only AppImage sysroot to cache directories. The AppImage now uses a dedicated relative font configuration with bundled/system/user font sources and a guaranteed writable runtime cache, while restoring the user's original XDG cache setting inside terminals. Both graphical smoke backends now fail on any Fontconfig error; X11, Wayland, and a real host FUSE launch pass without warnings.

2026-07-24: Human acceptance received after testing the rebuilt AppImage, including the Fontconfig cache correction. Task moved to Done.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Production-ready x86_64 AppImage implemented and accepted. The rootless Podman workflow produces a versioned artifact, checksum, and bundled-license inventory; clean X11 and Wayland smoke tests verify the bundled GUI runtime, host-shell environment boundary, working directory, extract fallback, and Fontconfig cache behavior. Documentation covers compatibility, security, verification, integration limits, uninstall, and manual publication.
<!-- SECTION:FINAL_SUMMARY:END -->
