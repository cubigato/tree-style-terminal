---
id: TASK-14
title: Define YAML layout templates for session trees
status: To Do
assignee: []
created_date: '2026-05-26 22:10'
updated_date: '2026-05-27 22:25'
labels:
  - feature
  - 'effort:medium'
  - 'area:workspace'
  - 'area:config'
dependencies: []
references:
  - 'https://zellij.dev/features/'
priority: medium
ordinal: 150
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a documented YAML format for reusable Tree Style Terminal layouts. Layouts should describe a tree of sessions with title, cwd, command, and children, and should be usable by the workspace starter.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 YAML layout schema is documented in CONFIG.md or a linked project doc
- [ ] #2 Layouts support nested children
- [ ] #3 Layout validation reports useful errors for malformed entries
<!-- AC:END -->
