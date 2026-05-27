---
id: TASK-9
title: Add duplicate session actions
status: To Do
assignee: []
created_date: '2026-05-26 22:09'
updated_date: '2026-05-27 22:25'
labels:
  - feature
  - 'effort:medium'
  - 'area:session'
dependencies: []
references:
  - 'https://learn.microsoft.com/en-us/windows/terminal/'
priority: medium
ordinal: 100
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add actions to duplicate the current session as a sibling or child using the same cwd and, if safely known, the same startup command. Keep the first version cwd-based if command capture is not reliable.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Current session can be duplicated as a sibling
- [ ] #2 Current session can be duplicated as a child
- [ ] #3 Duplicated sessions start in the source session's current directory
<!-- AC:END -->
