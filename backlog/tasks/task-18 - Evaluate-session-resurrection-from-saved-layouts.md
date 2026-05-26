---
id: TASK-18
title: Evaluate session resurrection from saved layouts
status: To Do
assignee: []
created_date: '2026-05-26 22:10'
labels:
  - feature
  - 'effort:large'
  - 'area:session'
  - research
dependencies: []
references:
  - 'https://zellij.dev/features/'
priority: low
ordinal: 220
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Evaluate a constrained version of session resurrection: restore tree layout, cwd, titles, and configured startup commands, but do not attempt to restore arbitrary live process state. Decide what should be implemented after persistence and layouts exist.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document what can and cannot be restored with VTE
- [ ] #2 Define expected behavior for commands that should rerun on restore
- [ ] #3 Depends conceptually on session persistence and layout templates
<!-- AC:END -->
