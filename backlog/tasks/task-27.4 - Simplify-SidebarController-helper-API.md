---
id: TASK-27.4
title: Simplify SidebarController helper API
status: Done
assignee: []
created_date: '2026-05-27 22:18'
updated_date: '2026-05-30 10:01'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/controllers/sidebar.py
  - src/tree_style_terminal/widgets/sidebar.py
  - tests/unit/test_sidebar_controller.py
  - tests/unit/test_session_tree_events.py
modified_files:
  - src/tree_style_terminal/controllers/sidebar.py
  - tests/unit/test_sidebar_controller.py
  - tests/unit/test_session_tree_events.py
parent_task_id: TASK-27
priority: medium
ordinal: 13500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. SidebarController has runtime-used direct TreeStore update methods plus unused or placeholder helper paths such as move_session, _cleanup_session_mapping, _extract_children_data, and bind_session_tree_events. Review each helper, remove dead API where safe, and update tests so they describe the current callback/manual-sync design instead of preserving placeholders.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Each SidebarController helper is classified as runtime-used, test-only, dead, or intentionally reserved.
- [x] #2 Dead/test-only helpers are removed or explicitly justified.
- [x] #3 Tests no longer assert placeholder APIs merely exist unless the API is intentionally kept.
- [x] #4 Session close/adoption behavior in the sidebar remains covered by tests.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Goal: shrink SidebarController to the helpers the runtime actually uses. Less code, no behavior change to add/select/close flows.

Step 0 - Classify every helper (AC #1) -- recorded in notes
Runtime-used (keep): add_session, remove_session_with_adoption, _restore_children_data (internal), update_session, get_tree_store, get_session_from_iter, find_iter_for_session, sync_with_session_tree, _populate_from_session_tree, _add_session_recursive.
Dead (no callers anywhere): move_session, _cleanup_session_mapping, _extract_children_data.
Test-only / placeholder: bind_session_tree_events (no-op placeholder), remove_session (prod uses remove_session_with_adoption, which handles leaf nodes with adopted_children=[]), update_session_title (prod uses update_session; SessionManager mutates the title and calls update_session).
NOTE vs task text: find_iter_for_session and sync_with_session_tree are NOT dead -- they are used by widgets/sidebar.py (select_session / refresh). Do not remove them.

Step 1 - Remove dead helpers (AC #2)
- Delete move_session, _cleanup_session_mapping, _extract_children_data from controllers/sidebar.py. No call sites exist (verified via grep across src + tests).

Step 2 - Resolve placeholder + test-only API (AC #2, #3)
- bind_session_tree_events: remove the no-op method and the stale 'Event binding' comment block in __init__. Sync happens via SessionManager callbacks + SessionSidebar.refresh()/sync_with_session_tree().
- remove_session: remove; it is redundant with remove_session_with_adoption (leaf = empty adoption list).
- update_session_title: remove; redundant with update_session (production title updates flow through SessionManager then update_session).
- If a reviewer prefers retaining remove_session/update_session_title as public convenience API, the fallback is to keep them and add a one-line code comment justifying the kept surface (AC #2 allows explicit justification). Default recommendation: remove for 'less is more'.

Step 3 - Update tests to describe current design (AC #3, #4)
- tests/unit/test_session_tree_events.py: drop test_bind_session_tree_events_method_exists and the bind calls in test_multiple_controllers_can_bind_to_same_tree (keep the sync_with_session_tree assertions). 
- tests/unit/test_sidebar_controller.py: 
  - Remove test_bind_session_tree_events_placeholder.
  - Replace test_remove_session to exercise remove_session_with_adoption(session, [], None) for the leaf case.
  - Replace test_update_session_title with a test that sets session.title then calls update_session and asserts the TreeStore COL_TITLE.
  - Keep test_find_iter_for_session and test_sync_with_session_tree (still runtime API).
- Ensure session close/adoption coverage remains (AC #4): keep/strengthen a test that builds parent+children, calls remove_session_with_adoption with adopted_children and a new_parent, and asserts children re-appear under the new parent and mappings are updated.

Step 4 - Validate (DoD)
- .venv/bin/python -m pytest tests/unit/test_sidebar_controller.py tests/unit/test_session_tree_events.py -q
- Run the broader sidebar/session suite to catch indirect coupling.
- Optional manual smoke: create child sessions, close a parent, confirm children are adopted in the sidebar and titles update.

Out of scope: no changes to add/select/close behavior beyond deleting unused API; no refactor of widgets/sidebar.py or SessionManager.

Risks / what could go wrong
- Misclassification: a helper assumed dead is reached via getattr/string dispatch. Mitigation: grep each name across src + tests before deleting (done for move_session/_cleanup_session_mapping/_extract_children_data -- zero hits outside their own defs).
- Removing find_iter_for_session/sync_with_session_tree by following the outdated task text would break select_session and refresh. Mitigation: explicitly keep them (called from widgets/sidebar.py).
- Adoption regression (AC #4): remove_session_with_adoption only re-appends direct adopted_children via _restore_children_data; deeper subtree mapping is an existing behavior and must not change here. Mitigation: keep adoption tests; do not touch _restore_children_data logic.
- Test coupling elsewhere: other suites may import the removed methods. Mitigation: run the full test suite, not just the two files.
- API-removal pushback: remove_session/update_session_title are tidy public names; reviewer may want them kept. Mitigation: fallback is to retain with a justifying comment (AC #2) rather than re-adding later.
- Scope creep: tempting to also normalize logging or rename helpers. Keep strictly to dead-code removal to satisfy DoD #2.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Helper classification (AC #1): KEEP (runtime): add_session, remove_session_with_adoption, _restore_children_data, update_session, get_tree_store, get_session_from_iter, find_iter_for_session (widget select_session), sync_with_session_tree (widget refresh), _populate_from_session_tree, _add_session_recursive. DEAD (no callers): move_session, _cleanup_session_mapping, _extract_children_data. TEST-ONLY/PLACEHOLDER: bind_session_tree_events (no-op), remove_session (superseded by remove_session_with_adoption), update_session_title (superseded by update_session). Correction to task description: find_iter_for_session and sync_with_session_tree are runtime-used via widgets/sidebar.py, NOT dead -- keep them.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed dead/test-only SidebarController helpers (remove_session, move_session, _cleanup_session_mapping, _extract_children_data, update_session_title, bind_session_tree_events) and updated tests to cover the runtime manual-sync/adoption API. Validation: .venv/bin/python -m pytest -q -> 251 passed.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Sidebar controller and session tree related tests pass.
- [x] #2 No behavior change is made to active session add/select/close flows except removal of unused API.
<!-- DOD:END -->
