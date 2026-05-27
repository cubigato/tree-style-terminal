---
id: TASK-3
title: Add scrollback search for the active terminal
status: next
assignee: []
created_date: '2026-05-26 22:08'
updated_date: '2026-05-27 21:46'
labels:
  - feature
  - 'effort:small'
  - 'area:terminal'
dependencies: []
references:
  - 'https://gnome.pages.gitlab.gnome.org/vte/gtk3/class.Terminal.html'
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a simple search UI for the active VTE terminal scrollback, with next/previous navigation and clear search state. Keep this scoped to the active terminal; no cross-session indexing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 User can open a search field for the current terminal
- [ ] #2 Search can move to next and previous match
- [ ] #3 Search state is cleared cleanly when closing the search UI
<!-- AC:END -->
