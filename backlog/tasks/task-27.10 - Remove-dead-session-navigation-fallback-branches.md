---
id: TASK-27.10
title: Remove dead session-navigation fallback branches
status: Done
assignee: []
created_date: '2026-05-30 09:41'
updated_date: '2026-06-01 12:55'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/controllers/shortcuts.py
parent_task_id: TASK-27
priority: high
ordinal: 26500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. ShortcutController._on_next_session and _on_prev_session guard the call with 'if hasattr(self.session_manager, "select_next_session")' and provide an else fallback that re-implements the index-based navigation. SessionManager always defines select_next_session/select_previous_session, so the else branches are unreachable and duplicate logic that already lives in the manager. Remove the dead branches and keep the direct calls.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Call-site review confirms SessionManager always provides select_next_session/select_previous_session, making the else fallback branches unreachable.
- [ ] #2 The hasattr guard and the duplicated fallback navigation logic are removed from _on_next_session and _on_prev_session; the handlers call the manager methods directly inside their existing try/except.
- [ ] #3 Next/previous session navigation remains covered by tests.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Goal: drop unreachable fallback branches; single source of navigation logic in SessionManager.

Step 0 - Confirm reachability (AC #1)
- select_next_session (session_manager.py L352) and select_previous_session (L371) always exist. hasattr is always True -> else branch is dead.

Step 1 - Simplify (AC #2)
- shortcuts.py _on_next_session: replace the hasattr/else block with a direct self.session_manager.select_next_session() inside the existing try/except.
- shortcuts.py _on_prev_session: same with select_previous_session().

Step 2 - Tests (AC #3)
- Check tests/unit/test_shortcuts.py and tests/ui/test_session_ui_integration.py for coverage of next/prev navigation; ensure they exercise the manager call. Add a minimal test if navigation is currently only exercised through the dead fallback.

Step 3 - Validate (DoD)
- .venv/bin/python -m pytest tests/unit/test_shortcuts.py tests/ui/test_session_ui_integration.py -q

Risks / what could go wrong
- A test patches/relies on the fallback branch: search tests for select_session-based navigation assertions before removing.
- Index/wrap-around behavior differs between fallback and manager: verify SessionManager.select_next/previous_session already implement wrap-around (they do) so behavior is unchanged.
- Scope creep into refactoring SessionManager navigation: keep changes inside shortcuts.py handlers only.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Call-site review (AC #1): SessionManager.select_next_session/select_previous_session are always defined (session_manager.py ~L352/L371). The hasattr checks in shortcuts.py _on_next_session/_on_prev_session are therefore always True and the else fallbacks are dead, duplicating the manager's index/wrap-around logic.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Focused shortcut/navigation tests pass.
- [ ] #2 No behavior change to next/previous navigation beyond removing the dead branches.
<!-- DOD:END -->
