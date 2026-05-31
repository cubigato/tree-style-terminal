---
id: TASK-27.13.2
title: Apply Ruff import cleanup
status: To Do
assignee: []
created_date: '2026-05-31 13:06'
labels:
  - cleanup
dependencies:
  - TASK-27.13.1
parent_task_id: TASK-27.13
ordinal: 17700
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Child of TASK-27.13. Apply the normal Ruff import cleanup after whitespace noise is gone. Scope this to I001 import sorting and F401 unused imports produced by standard .venv/bin/python -m ruff check src tests --fix. Review exported-package files before accepting removed imports.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 I001 import sorting is applied
- [ ] #2 F401 unused imports are removed only when they are not part of the public package surface
- [ ] #3 No typing modernization or behavior-sensitive changes are mixed in
- [ ] #4 Test suite passes after the cleanup
<!-- AC:END -->
