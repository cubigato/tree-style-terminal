---
id: TASK-27.4
title: Simplify SidebarController helper API
status: next
assignee: []
created_date: '2026-05-27 22:18'
updated_date: '2026-05-28 12:13'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/controllers/sidebar.py
  - src/tree_style_terminal/widgets/sidebar.py
  - tests/unit/test_sidebar_controller.py
  - tests/unit/test_session_tree_events.py
parent_task_id: TASK-27
priority: medium
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. SidebarController has runtime-used direct TreeStore update methods plus unused or placeholder helper paths such as move_session, _cleanup_session_mapping, _extract_children_data, and bind_session_tree_events. Review each helper, remove dead API where safe, and update tests so they describe the current callback/manual-sync design instead of preserving placeholders.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each SidebarController helper is classified as runtime-used, test-only, dead, or intentionally reserved.
- [ ] #2 Dead/test-only helpers are removed or explicitly justified.
- [ ] #3 Tests no longer assert placeholder APIs merely exist unless the API is intentionally kept.
- [ ] #4 Session close/adoption behavior in the sidebar remains covered by tests.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Sidebar controller and session tree related tests pass.
- [ ] #2 No behavior change is made to active session add/select/close flows except removal of unused API.
<!-- DOD:END -->
