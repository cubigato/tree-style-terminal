---
id: TASK-27.13.2
title: Apply Ruff import cleanup
status: Done
assignee: []
created_date: '2026-05-31 13:06'
updated_date: '2026-05-31 13:20'
labels:
  - cleanup
dependencies:
  - TASK-27.13.1
parent_task_id: TASK-27.13
ordinal: 19500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Child of TASK-27.13. Apply the normal Ruff import cleanup after whitespace noise is gone. Scope this to I001 import sorting and F401 unused imports produced by standard .venv/bin/python -m ruff check src tests --fix. Review exported-package files before accepting removed imports.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 I001 import sorting is applied
- [x] #2 F401 unused imports are removed only when they are not part of the public package surface
- [x] #3 No typing modernization or behavior-sensitive changes are mixed in
- [x] #4 Test suite passes after the cleanup
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Applied scoped Ruff I001/F401 cleanup across src and tests, preserved public package exports, added explicit GTK3 Gdk version guards required after unused imports were removed, and verified with Ruff plus the full pytest suite.
<!-- SECTION:FINAL_SUMMARY:END -->
