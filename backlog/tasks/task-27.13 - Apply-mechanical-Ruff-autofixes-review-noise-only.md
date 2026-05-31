---
id: TASK-27.13
title: Coordinate mechanical Ruff cleanup
status: next
assignee: []
created_date: '2026-05-31 12:56'
updated_date: '2026-05-31 13:12'
labels:
  - cleanup
dependencies: []
parent_task_id: TASK-27
priority: medium
ordinal: 990
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27.6. Umbrella task for the accepted Ruff cleanup path. Keep this ticket as coordination only; apply changes in smaller child tasks so review noise stays bounded. Use normal .venv/bin/python -m ruff check src tests --fix only unless a child task explicitly calls out manual review. Do not use --unsafe-fixes as part of the mechanical cleanup.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Unsafe or behavior-sensitive Ruff suggestions remain in TASK-27.14 or another manual-review task
- [ ] #2 Child tasks cover the mechanical Ruff cleanup in reviewable chunks
- [ ] #3 No code changes are mixed directly into this umbrella task
<!-- AC:END -->
