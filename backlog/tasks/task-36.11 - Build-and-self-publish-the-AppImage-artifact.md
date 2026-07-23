---
id: TASK-36.11
title: Build and self-publish the AppImage artifact
status: next
assignee: []
created_date: '2026-07-23 13:40'
labels:
  - packaging
  - appimage
  - release
  - 'blocker:1.0'
dependencies:
  - TASK-36.1
  - TASK-36.2
  - TASK-36.10
references:
  - 'https://docs.appimage.org/packaging-guide/introduction.html'
  - 'https://docs.appimage.org/packaging-guide/from-source/native-binaries.html'
  - 'https://docs.appimage.org/reference/best-practices.html'
  - 'https://docs.appimage.org/packaging-guide/distribution.html'
modified_files:
  - packaging/appimage/AppRun
  - packaging/appimage/README.md
  - README.md
parent_task_id: TASK-36
priority: high
ordinal: 2500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provide a portable, directly downloadable AppImage for 1.0 that runs Tree Style Terminal with its native Python, GTK3, PyGObject, and VTE stack bundled while starting normal host shell sessions without a sandbox bridge. Publish it under cubigato's control without depending on an application store or catalog.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A versioned and reviewable AppDir recipe builds from a clean checkout in a pinned, documented baseline environment; AppImage build tools, GTK deployment helpers, runtime inputs, and downloaded artifacts are fixed to immutable versions or commits and verified by checksum.
- [ ] #2 The AppImage contains the required Python 3.11+, application package, PyYAML, PyGObject, GTK3, VTE, GI typelibs, schemas, loaders, desktop assets, and applicable license notices, and runs on a supported clean system without those application dependencies preinstalled.
- [ ] #3 The artifact uses de.cubigato.TreeStyleTerminal and the shared version, icon, desktop entry, AppStream metadata, and license information consistently.
- [ ] #4 Clean-environment smoke coverage starts the AppImage, opens the real host shell in the requested working directory, runs a host command without bundled-runtime contamination, and exits cleanly on the documented X11 and Wayland support matrix.
- [ ] #5 The supported glibc/distribution and CPU-architecture baseline, FUSE expectations and extract-and-run fallback, installation/menu-integration limitations, security model, configuration persistence, and uninstall procedure are documented.
- [ ] #6 A tagged build produces a directly downloadable versioned AppImage plus SHA-256 checksum, verification material, bundled-component/license inventory, and optional zsync metadata without requiring AppImageHub or another catalog.
<!-- AC:END -->
