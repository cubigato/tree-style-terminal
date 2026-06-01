---
id: TASK-1
title: 'Bug #001: Sidebar transparency not working with terminal transparency'
status: Done
assignee: []
created_date: '2026-05-26 22:04'
updated_date: '2026-06-01 12:55'
labels:
  - bug
  - legacy
dependencies: []
priority: medium
ordinal: 30500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Legacy bug migrated from bugs/closed/001-sidebar-transparency.md. Reported 2025-06-03 by kiney; fixed 2026-05-22. Sidebar remained opaque when terminal transparency was configured. Expected the sidebar to match terminal transparency; actual behavior was that the terminal area was transparent while sidebar and TreeView stayed opaque.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Configure terminal.transparency below 1.0 and launch the application
- [x] #2 Terminal area is transparent
- [x] #3 Sidebar and TreeView are transparent as well
<!-- AC:END -->



## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Root cause: base transparency CSS loaded before active theme CSS, and multiple GTK sidebar layers kept opaque backgrounds. Fix applied: runtime sidebar transparency CSS loaded after theme CSS, transparent backgrounds across the sidebar widget chain, explicit CSS hooks for outer sidebar containers, theme selection/hover/border colors preserved, and sidebar GtkScrolledWindow exposed for styling/tests.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Verified in the legacy ticket with .venv/bin/python -m pytest -q: 183 passed in 2.69s.
<!-- SECTION:FINAL_SUMMARY:END -->
