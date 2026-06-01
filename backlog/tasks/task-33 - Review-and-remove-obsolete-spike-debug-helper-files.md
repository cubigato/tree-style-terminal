---
id: TASK-33
title: Review and remove obsolete spike/debug helper files
status: Done
assignee: []
created_date: '2026-05-31 13:29'
updated_date: '2026-06-01 12:55'
labels:
  - cleanup
dependencies: []
priority: low
ordinal: 36500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Review the top-level spike and debug helper files that are outside the normal src/tests Ruff cleanup scope: spikes/gtk.py, spikes/qt.py, and util/debug_transparency.py. Determine whether they are still useful. If they are obsolete, remove them; if any are still useful, either bring them under current lint expectations or document why they should remain outside normal checks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 spikes/gtk.py, spikes/qt.py, and util/debug_transparency.py are reviewed for current usefulness
- [x] #2 Obsolete files are removed from the repository
- [x] #3 Any retained file is either lint-clean under the project Ruff configuration or has a documented reason to remain out of scope
- [x] #4 Ruff repo-wide output no longer includes avoidable safe-fix noise from obsolete spike/debug helpers
<!-- AC:END -->
