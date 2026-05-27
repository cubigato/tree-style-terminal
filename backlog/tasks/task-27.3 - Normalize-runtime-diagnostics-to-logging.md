---
id: TASK-27.3
title: Normalize runtime diagnostics to logging
status: To Do
assignee: []
created_date: '2026-05-27 22:18'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/main.py
parent_task_id: TASK-27
priority: high
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. Runtime app paths currently mix print() and logging. Keep print() for explicit CLI output such as --show-info and --test-fonts, but use logging for normal application startup, CSS/theme loading, sidebar/focus state changes, and recoverable runtime warnings.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Runtime UI/application paths in main.py use logging instead of print for non-CLI diagnostics.
- [ ] #2 Explicit CLI diagnostic output for --show-info and --test-fonts remains printed to stdout/stderr as appropriate.
- [ ] #3 Error handling for transparency/config startup remains user-visible enough to diagnose startup failure.
- [ ] #4 No unrelated behavior, CSS, or session-management changes are included.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Relevant main/app tests pass.
- [ ] #2 A short note in the task or code clarifies which outputs intentionally remain print-based.
<!-- DOD:END -->
