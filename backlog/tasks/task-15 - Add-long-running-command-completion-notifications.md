---
id: TASK-15
title: Add long-running command completion notifications
status: To Do
assignee: []
created_date: '2026-05-26 22:10'
updated_date: '2026-05-28 14:26'
labels:
  - feature
  - 'effort:medium'
  - 'area:terminal'
  - 'area:notifications'
dependencies: []
references:
  - 'https://iterm2.com/documentation-shell-integration.html'
priority: medium
ordinal: 200
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Notify when a session exits or when a long-running command appears to finish, using conservative heuristics first. Start with child-exited notifications; command-level detection can wait for shell integration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 User can enable or disable terminal completion notifications
- [ ] #2 Terminal process exit can trigger a desktop notification
- [ ] #3 Notifications identify the relevant session title
<!-- AC:END -->
