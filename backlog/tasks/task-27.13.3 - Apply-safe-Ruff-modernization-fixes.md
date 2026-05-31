---
id: TASK-27.13.3
title: Apply safe Ruff modernization fixes
status: To Do
assignee: []
created_date: '2026-05-31 13:06'
labels:
  - cleanup
dependencies:
  - TASK-27.13.2
parent_task_id: TASK-27.13
ordinal: 17800
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Child of TASK-27.13. Apply the remaining standard Ruff fixes that are expected to be mechanical syntax modernization: UP006, UP007, UP015, UP024, UP037, SIM910, and F541. Use normal .venv/bin/python -m ruff check src tests --fix only; do not enable --unsafe-fixes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 UP006, UP007, UP015, UP024, UP037, SIM910, and F541 standard fixes are applied where Ruff offers them
- [ ] #2 No --unsafe-fixes are used
- [ ] #3 Any fix that appears behavior-sensitive is left for TASK-27.14 instead
- [ ] #4 Test suite passes after the cleanup
<!-- AC:END -->
