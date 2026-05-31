---
id: TASK-27.13
title: Coordinate mechanical Ruff cleanup
status: Done
assignee: []
created_date: '2026-05-31 12:56'
updated_date: '2026-05-31 13:52'
labels:
  - cleanup
dependencies: []
modified_files:
  - AGENTS.md
parent_task_id: TASK-27
priority: medium
ordinal: 23500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27.6. Umbrella task for the accepted Ruff cleanup path. Keep this ticket as coordination only; apply changes in smaller child tasks so review noise stays bounded. Use normal .venv/bin/python -m ruff check src tests --fix only unless a child task explicitly calls out manual review. Do not use --unsafe-fixes as part of the mechanical cleanup.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Unsafe or behavior-sensitive Ruff suggestions remain in TASK-27.14 or another manual-review task
- [x] #2 Child tasks cover the mechanical Ruff cleanup in reviewable chunks
- [x] #3 No code changes are mixed directly into this umbrella task
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Coordination review complete: TASK-27.13 child tasks cover the mechanical Ruff cleanup in bounded chunks, behavior-sensitive findings were handled through TASK-27.14/manual-review scope, and current verification with .venv/bin/python -m ruff check src tests reports all checks passed. No code changes were made directly under the umbrella task; AGENTS.md now records that Ruff must stay clean after each task.
<!-- SECTION:FINAL_SUMMARY:END -->
