---
id: TASK-39
title: Streamline README for current installation and usage
status: In Progress
assignee:
  - Codex
created_date: '2026-07-23 23:22'
updated_date: '2026-07-23 23:25'
labels:
  - documentation
  - cleanup
dependencies: []
documentation:
  - README.md
  - PACKAGING.md
  - CONFIG.md
modified_files:
  - README.md
priority: medium
ordinal: 3300
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refocus the project README on current end-user value and supported entry points. Remove manually maintained dependency and internal architecture prose that has become inaccurate or redundant, make the native Debian package the recommended installation path, retain uv tool installation as the concise alternative, and direct live project status to Backlog.md instead of duplicating it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The README recommends installation from the project-provided Debian package and gives a concise `uv tool install` alternative without distribution-specific dependency recipes.
- [x] #2 The duplicated current-status checklist, requirements list, and architecture overview are removed, and ongoing work points readers to the Backlog.md board.
- [x] #3 Remaining feature, configuration, usage, development, and packaging statements are consistent with the current code and repository.
- [x] #4 Verbose troubleshooting and duplicated reference material are removed or replaced with links to the authoritative project documents.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Replace the installation section with a short Debian-package recommendation and a concise `uv tool install` source/PyPI-style alternative, linking detailed packaging guidance instead of maintaining native dependency recipes in README.
2. Remove the Current Status, Architecture, and Requirements sections; add a short development-status pointer to the Backlog.md board.
3. Consolidate configuration, workspace-profile, DPI, theming, session-management, and development prose where authoritative details already exist elsewhere, while preserving useful first-use examples.
4. Verify remaining claims against current CLI options, configuration defaults, project scripts, and repository paths; run markdown/link-oriented sanity checks and project-required Ruff before handoff.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Rewrote README.md as a concise end-user entry point. The Debian .deb is the recommended installation path, with `uv tool install .` retained as a short alternative and a clear note that native GTK/VTE/PyGObject must already be compatible on that route. Removed distribution-specific dependency recipes, PyGObject build troubleshooting, the Current Status checklist, Architecture and Requirements sections, absent pre-commit setup, obsolete multi-tool quality instructions, and verbose copies of configuration/workspace/DPI/theme/AI details. Current roadmap information points to the Backlog.md board; CONFIG.md and PACKAGING.md remain authoritative for details.

Accuracy verification: compared installation claims with the current Debian/Podman build workflow and pyproject scripts; compared usage examples with live `.venv/bin/tst --help`; compared shortcuts with ShortcutController defaults; verified all local README paths exist. README reduced from 471 lines / roughly 1,900 words to 165 lines / 532 words. Ruff and git diff --check pass, and no removed stale dependency/status/architecture/tooling terms remain.
<!-- SECTION:NOTES:END -->
