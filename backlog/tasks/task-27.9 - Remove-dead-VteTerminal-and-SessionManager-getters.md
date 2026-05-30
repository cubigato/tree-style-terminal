---
id: TASK-27.9
title: Remove dead VteTerminal and SessionManager getters
status: Done
assignee: []
created_date: '2026-05-30 09:41'
updated_date: '2026-05-30 10:18'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/widgets/terminal.py
  - src/tree_style_terminal/controllers/session_manager.py
parent_task_id: TASK-27
priority: high
ordinal: 14500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. Several public getters have no callers in src or tests: VteTerminal.get_transparency(), VteTerminal.get_current_theme(), VteTerminal.force_update_directory_tracking() (widgets/terminal.py), and SessionManager.get_current_theme() (controllers/session_manager.py). Their backing state is set/used internally, but the getters themselves are never read. Prove they are unreachable, then remove them and any test that only asserts their existence.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Call-site review confirms each getter (VteTerminal.get_transparency/get_current_theme/force_update_directory_tracking, SessionManager.get_current_theme) has no production or test callers.
- [x] #2 The dead getters are removed; backing attributes (_transparency, _current_theme, CWD tracking) and their setters/active paths remain unchanged.
- [x] #3 Any test that only asserted existence of a removed getter is updated or removed.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Goal: delete unread public getters. Less code, no behavior change.

Step 0 - Confirm reachability (AC #1)
- grep '.get_transparency(', '.get_current_theme(', 'force_update_directory_tracking' across src + tests. Confirmed: only definitions, no callers.
- Note: VteTerminal.set_transparency, apply_theme, and _on_title_changed CWD tracking remain in use; only the getters are dead.

Step 1 - Remove (AC #2)
- widgets/terminal.py: delete get_transparency, get_current_theme, force_update_directory_tracking. Keep _transparency/_current_theme attributes and set_transparency/apply_theme.
- controllers/session_manager.py: delete get_current_theme. Keep _current_theme and set_theme.

Step 2 - Tests (AC #3)
- Remove/adjust any hasattr-style assertions referencing the removed getters (check tests/test_terminal_widget.py method-exists list).

Step 3 - Validate (DoD)
- .venv/bin/python -m pytest tests/test_terminal_widget.py tests/unit/test_session_actions.py tests/integration/test_theme_integration.py -q

Risks / what could go wrong
- A getter is reached via getattr/string dispatch: mitigated by grep (zero hits outside defs).
- Removing a backing attribute by mistake breaks set_transparency/apply_theme: only remove the getter methods, not the attributes.
- Scope creep into theme/transparency refactor: keep strictly to getter deletion.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented on 2026-05-30: call-site review found no production callers for the four removed methods. It found one test-only caller in tests/test_main_window.py asserting SessionManager.get_current_theme(); that assertion only exercised the deleted getter and was removed. Post-removal search for get_transparency(, get_current_theme(, and force_update_directory_tracking across src and tests returns no matches. Removed VteTerminal.get_transparency, VteTerminal.get_current_theme, VteTerminal.force_update_directory_tracking, and SessionManager.get_current_theme while keeping _transparency, _current_theme, set_transparency/apply_theme, set_theme, and existing CWD tracking paths unchanged. Validation: .venv/bin/python -m pytest tests/test_terminal_widget.py tests/unit/test_session_actions.py tests/integration/test_theme_integration.py tests/test_main_window.py -q => 80 passed.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Focused terminal-widget and session-manager tests pass.
- [x] #2 No behavior change beyond removing the unused getters.
<!-- DOD:END -->
