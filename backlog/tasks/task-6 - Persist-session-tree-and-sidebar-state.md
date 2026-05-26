---
id: TASK-6
title: Persist session tree and sidebar state
status: To Do
assignee: []
created_date: '2026-05-26 22:08'
labels:
  - feature
  - 'effort:medium'
  - 'area:session'
dependencies: []
references:
  - ARCHITECTURE.md
priority: high
ordinal: 40
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Persist the session tree structure, titles, cwd values, selected session, and expanded/collapsed sidebar state under XDG state. Restore structure on startup without pretending to restore live process state.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Session tree metadata is saved after structural changes
- [ ] #2 Startup restores saved roots, children, titles, cwd values, selection, and expanded rows
- [ ] #3 Missing or invalid state falls back to a clean first session
<!-- AC:END -->
