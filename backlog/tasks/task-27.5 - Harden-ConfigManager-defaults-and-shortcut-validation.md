---
id: TASK-27.5
title: Harden ConfigManager defaults and shortcut validation
status: To Do
assignee: []
created_date: '2026-05-27 22:18'
updated_date: '2026-05-27 22:25'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/config/manager.py
  - src/tree_style_terminal/config/defaults.py
  - src/tree_style_terminal/controllers/shortcuts.py
  - tests/unit/test_config.py
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
- [ ] #1 Default config loading and merging do not share mutable nested dictionaries with DEFAULT_CONFIG.
- [ ] #2 A focused test proves mutations to loaded config cannot mutate DEFAULT_CONFIG.
- [ ] #3 Shortcut accelerator validation behavior is explicit and covered by tests: either config validation rejects invalid accelerators, or runtime registration warning behavior is deliberately documented/tested.
- [ ] #4 No unrelated config schema changes are included.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Config unit tests pass.
- [ ] #2 Existing generated default config behavior remains compatible.
<!-- DOD:END -->
