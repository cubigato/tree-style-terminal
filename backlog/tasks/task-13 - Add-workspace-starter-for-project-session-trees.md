---
id: TASK-13
title: Add workspace starter for project session trees
status: To Do
assignee: []
created_date: '2026-05-26 22:10'
updated_date: '2026-05-27 22:25'
labels:
  - feature
  - 'effort:medium'
  - 'area:workspace'
dependencies: []
references:
  - 'https://wezterm.org/'
  - 'https://zellij.dev/features/'
priority: medium
ordinal: 140
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow users to start a predefined project workspace as a tree of sessions, for example repo root, test session, server session, and logs session. This should build on session creation and cwd inheritance rather than a multiplexer.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A workspace can create multiple sessions in a parent/child tree
- [ ] #2 Each workspace node can define title, cwd, and optional command
- [ ] #3 Failed child creation does not leave the app unusable
<!-- AC:END -->
