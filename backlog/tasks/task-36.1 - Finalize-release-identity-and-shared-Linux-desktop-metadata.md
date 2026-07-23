---
id: TASK-36.1
title: Finalize release identity and shared Linux desktop metadata
status: next
assignee: []
created_date: '2026-07-23 13:15'
labels:
  - packaging
  - release
  - desktop-integration
  - 'blocker:1.0'
dependencies: []
references:
  - 'https://docs.flathub.org/docs/for-app-authors/requirements'
  - 'https://www.freedesktop.org/software/appstream/docs/chap-Metadata.html'
modified_files:
  - pyproject.toml
  - src/tree_style_terminal/__init__.py
  - src/tree_style_terminal/main.py
  - tests/test_basic.py
parent_task_id: TASK-36
priority: high
ordinal: 2100
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Establish one stable, package-independent identity and metadata set for the 1.0 Linux release so Debian, Flatpak, PyPI metadata, the application runtime, and desktop software centers all describe the same application. cubigato GmbH controls cubigato.de; use the permanent reverse-DNS application ID de.cubigato.TreeStyleTerminal. Keep the shared desktop, icon, license, and release metadata upstream so packaging formats consume the same source files.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The runtime application ID, desktop file ID, icon name, and MetaInfo component ID all use de.cubigato.TreeStyleTerminal.
- [ ] #2 A release-quality application icon, desktop entry, and AppStream MetaInfo file are included as shared upstream assets and pass their standard validators.
- [ ] #3 Project version information has one authoritative source and is consistent across runtime and packaging metadata.
- [ ] #4 License, project URLs, release notes, categories, launch command, and screenshots referenced by the metadata are complete and consistent.
- [ ] #5 Automated tests cover the permanent application ID and version consistency, and the packaging/release documentation describes how shared metadata is updated.
<!-- AC:END -->
