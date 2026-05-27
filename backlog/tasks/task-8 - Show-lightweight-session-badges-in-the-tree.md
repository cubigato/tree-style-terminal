---
id: TASK-8
title: Show lightweight session badges in the tree
status: To Do
assignee: []
created_date: '2026-05-26 22:09'
updated_date: '2026-05-27 22:25'
labels:
  - feature
  - 'effort:medium'
  - 'area:sidebar'
dependencies: []
references:
  - 'https://iterm2.com/documentation-shell-integration.html'
priority: medium
ordinal: 90
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Display small, optional status badges in the sidebar, starting with stable low-cost metadata such as cwd basename, remote host when known, running/exited state, or exit code. Avoid expensive polling.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Sidebar can show at least one status badge per session
- [ ] #2 Exited sessions can show their exit status
- [ ] #3 Badge rendering remains readable in light and dark themes
<!-- AC:END -->
