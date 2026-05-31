---
id: TASK-27.13.1
title: Apply whitespace-only Ruff fixes
status: To Do
assignee: []
created_date: '2026-05-31 13:06'
labels:
  - cleanup
dependencies: []
parent_task_id: TASK-27.13
ordinal: 17600
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Child of TASK-27.13. Apply only whitespace and newline Ruff fixes with normal Ruff fixes, limited to W293, W291, and W292. This should be a review-noise-only diff: blank-line whitespace, trailing whitespace, and final newlines.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Only W293, W291, and W292 style cleanup is included
- [ ] #2 No import, typing, or behavior-related changes are mixed in
- [ ] #3 Test suite passes after the cleanup
<!-- AC:END -->
