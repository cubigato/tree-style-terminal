---
id: TASK-27.1
title: Retire legacy MainWindow terminal management
status: next
assignee: []
created_date: '2026-05-27 22:18'
updated_date: '2026-05-28 12:12'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/main.py
  - tests/test_main_window.py
parent_task_id: TASK-27
priority: medium
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. MainWindow still contains an older terminal-management path based on self.terminals, terminal_counter, active_terminal_id, and _create_new_terminal/_switch_to_terminal/_close_terminal, while current runtime actions use SessionManager through ShortcutController. Prove whether any production path still needs the legacy API, update tests away from legacy expectations, then remove or explicitly retain the legacy path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Call-site review documents whether the legacy terminal path is reachable outside tests.
- [ ] #2 Tests assert the current SessionManager-driven behavior instead of requiring legacy terminal attributes/methods.
- [ ] #3 Unused legacy state and methods are removed, or the remaining compatibility surface is explicitly justified in code/tests.
- [ ] #4 Theme update behavior still applies to all active SessionManager terminals.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Focused main-window/session tests pass.
- [ ] #2 No unrelated MainWindow refactor is included.
<!-- DOD:END -->
