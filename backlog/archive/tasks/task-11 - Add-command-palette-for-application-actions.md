---
id: TASK-11
title: Add command palette for application actions
status: To Do
assignee: []
created_date: '2026-05-26 22:09'
updated_date: '2026-05-27 22:25'
labels:
  - feature
  - 'effort:medium'
  - 'area:ui'
dependencies: []
references:
  - 'https://learn.microsoft.com/en-us/windows/terminal/'
priority: medium
ordinal: 120
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a minimal command palette for existing app actions such as new child, new sibling, close session, toggle sidebar, focus terminal, search, rename, and save scrollback. This is an action launcher, not a fuzzy automation system.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Palette can be opened with a keyboard shortcut
- [ ] #2 Palette lists core existing actions
- [ ] #3 Selecting an action runs the same code path as the normal shortcut/menu action
<!-- AC:END -->
