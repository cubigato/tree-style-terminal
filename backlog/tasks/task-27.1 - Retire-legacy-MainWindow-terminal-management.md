---
id: TASK-27.1
title: Retire legacy MainWindow terminal management
status: Done
assignee: []
created_date: '2026-05-27 22:18'
updated_date: '2026-05-30 09:52'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/main.py
  - tests/test_main_window.py
modified_files:
  - src/tree_style_terminal/main.py
  - tests/test_main_window.py
parent_task_id: TASK-27
priority: medium
ordinal: 12500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. MainWindow still contains an older terminal-management path based on self.terminals, terminal_counter, active_terminal_id, and _create_new_terminal/_switch_to_terminal/_close_terminal, while current runtime actions use SessionManager through ShortcutController. Prove whether any production path still needs the legacy API, update tests away from legacy expectations, then remove or explicitly retain the legacy path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Call-site review documents whether the legacy terminal path is reachable outside tests.
- [x] #2 Tests assert the current SessionManager-driven behavior instead of requiring legacy terminal attributes/methods.
- [x] #3 Unused legacy state and methods are removed, or the remaining compatibility surface is explicitly justified in code/tests.
- [x] #4 Theme update behavior still applies to all active SessionManager terminals.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Goal: remove the dead legacy terminal path so MainWindow has a single, SessionManager-driven model. Less code, no behavior change.

Step 0 - Confirm reachability (AC #1)
- Legacy methods _create_new_terminal/_switch_to_terminal/_close_terminal only call each other and are invoked exclusively from tests/test_main_window.py.
- All UI buttons (_on_new_terminal_clicked, _on_new_child_clicked, _on_close_session_clicked, _on_search_clicked) route through ShortcutController -> SessionManager. The Glade welcome_new_terminal_button maps to _on_new_terminal_clicked, i.e. also the SessionManager path.
- self.terminals is populated ONLY by _create_new_terminal, so in production it is always empty; terminal_counter/active_terminal_id are only mutated there too.
- Conclusion: the legacy path is unreachable in production -> safe to delete. Record this in the task notes for AC #1.

Step 1 - Update tests away from legacy expectations (AC #2)
- tests/test_main_window.py:
  - Remove test_terminal_management_dict entirely (asserts terminals dict, terminal_counter, active_terminal_id).
  - In test_main_window_creation, drop the three hasattr(legacy) assertions; keep window construction smoke check.
  - In test_main_window_methods_exist, replace the three legacy method names with current public surface (e.g. _on_new_terminal_clicked, _on_close_session_clicked, _on_new_child_clicked, _on_sidebar_toggle_clicked). Optionally add a session-driven assertion.
- Add/keep a theme test: build window, register a fake terminal in session_manager._session_terminals, call _update_terminal_themes('dark'), assert apply_theme was invoked on it (covers AC #4 after the legacy loop is gone).

Step 2 - Remove legacy state and methods (AC #3)
- main.py __init__: delete the 'Legacy terminal management' block (self.terminals, terminal_counter, active_terminal_id).
- Delete methods _create_new_terminal, _switch_to_terminal, _close_terminal.
- Also delete _ensure_revealer_state (L540) - confirmed to have no callers; note it in the PR/notes. If wanting to stay minimal, this can be a separate line item but it is dead too.
- _update_terminal_themes: remove the 'for terminal_widget in self.terminals' loop; keep the session_manager.set_theme(theme_name) call (already covers every live terminal via _session_terminals). Drop the defensive hasattr(self.session_manager, 'set_theme').
- Clean now-unused imports: Dict (if no other use), and VteTerminal/Optional only if they become unused in main.py - verify with grep before removing.

Step 3 - Validate (DoD)
- .venv/bin/python -m pytest tests/test_main_window.py -q
- Run broader session/theme tests: tests touching SessionManager and shortcut controller.
- Manual smoke (optional): launch app, create sibling/child sessions, toggle theme, confirm all open terminals recolor.

Out of scope: no refactor of SessionManager, sidebar, or naming changes beyond deleting the legacy path.

Risks / what could go wrong
- Hidden reflection access: something might call legacy attrs via getattr/string names. Mitigation: grep for 'terminals', 'active_terminal_id', 'terminal_counter', '_switch_to_terminal' across src + tests before deleting (done for main paths; re-check before commit).
- Theme regression (AC #4): if removal accidentally drops the session_manager.set_theme call, open terminals stop recoloring. Mitigation: keep that call, cover with the new theme test.
- Import breakage: removing Dict/Optional/VteTerminal imports that are still used elsewhere in main.py causes NameError at import time. Mitigation: verify each import is unused via grep; run pytest which imports the module.
- Test coupling elsewhere: other test files may rely on the legacy API indirectly. Mitigation: run the full suite, not just test_main_window.py.
- Scope creep: _ensure_revealer_state and import cleanup tempt a wider tidy-up. Keep changes limited to the legacy terminal path to satisfy DoD #2; treat anything larger as a separate task.
- welcome stack name assumption: _close_terminal referenced a 'welcome' stack child; ensure no other code now depends on _close_terminal to set that page (the SessionManager close path already handles the welcome fallback in _on_session_closed).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Call-site review (AC #1): legacy path (_create_new_terminal/_switch_to_terminal/_close_terminal, self.terminals, terminal_counter, active_terminal_id) is unreachable in production. Only callers are tests and the legacy methods themselves; all buttons route via ShortcutController->SessionManager. self.terminals is only filled by _create_new_terminal so it is always empty at runtime, making the theme loop over it a no-op (SessionManager.set_theme already themes every live terminal via _session_terminals). _ensure_revealer_state also has no remaining callers.

Implemented: removed MainWindow legacy terminal state/methods, updated main-window tests to assert SessionManager-driven behavior, and kept theme updates delegated through SessionManager.set_theme. Verified no remaining legacy references in src/tests.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Focused main-window/session tests pass.
- [x] #2 No unrelated MainWindow refactor is included.
<!-- DOD:END -->
