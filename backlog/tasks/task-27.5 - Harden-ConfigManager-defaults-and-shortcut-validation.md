---
id: TASK-27.5
title: Harden ConfigManager defaults and shortcut validation
status: Done
assignee: []
created_date: '2026-05-27 22:18'
updated_date: '2026-07-22 21:39'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/config/manager.py
  - src/tree_style_terminal/config/defaults.py
  - src/tree_style_terminal/controllers/shortcuts.py
  - tests/unit/test_config.py
modified_files:
  - src/tree_style_terminal/config/manager.py
  - src/tree_style_terminal/controllers/shortcuts.py
  - tests/unit/test_config.py
  - tests/unit/test_shortcuts.py
parent_task_id: TASK-27
priority: low
ordinal: 310
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. ConfigManager currently uses shallow copies of DEFAULT_CONFIG in parts of the load/merge path, and shortcut validation only checks that terminal_search is a string while accelerator parsing happens later at runtime. Make default handling safer and decide whether invalid shortcut accelerators should be rejected at config validation or only warned about during shortcut registration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Default config loading and merging do not share mutable nested dictionaries with DEFAULT_CONFIG.
- [x] #2 A focused test proves mutations to loaded config cannot mutate DEFAULT_CONFIG.
- [x] #3 Shortcut accelerator validation behavior is explicit and covered by tests: either config validation rejects invalid accelerators, or runtime registration warning behavior is deliberately documented/tested.
- [x] #4 No unrelated config schema changes are included.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Decision: keep accelerator syntax validation at GTK shortcut registration time. Invalid configured accelerators emit a warning and are skipped, preserving a GTK-independent ConfigManager; this behavior is now covered by a focused test.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Deep-copied default configuration on creation and merge, added mutation regression coverage, and documented/tested warning-and-skip behavior for invalid GTK accelerators. Config tests and the full 291-test suite pass; Ruff is clean. Awaiting human review before Done.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Config unit tests pass.
- [x] #2 Existing generated default config behavior remains compatible.
<!-- DOD:END -->
