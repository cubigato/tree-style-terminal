---
id: TASK-24
title: Keep full terminal multiplexer replacement out of scope
status: To Do
assignee: []
created_date: '2026-05-26 22:11'
labels:
  - research
  - not-now
  - 'effort:large'
  - 'area:architecture'
dependencies: []
references:
  - 'https://zellij.dev/features/'
priority: low
ordinal: 320
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Record that Tree Style Terminal should not become a full tmux or Zellij replacement. Features can borrow ideas, but the app should focus on GUI tree-based session organization over terminal multiplexing internals.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document the distinction between TST session trees and terminal multiplexers
- [ ] #2 List multiplexer-like features that are acceptable versus out of scope
- [ ] #3 Use this decision to guide split pane and resurrection work
<!-- AC:END -->
