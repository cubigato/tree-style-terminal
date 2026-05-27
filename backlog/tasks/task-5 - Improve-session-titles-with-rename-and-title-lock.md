---
id: TASK-5
title: Improve session titles with rename and title lock
status: In Progress
assignee: []
created_date: '2026-05-26 22:08'
updated_date: '2026-05-27 22:29'
labels:
  - feature
  - 'effort:small'
  - 'area:sidebar'
dependencies: []
references:
  - 'https://iterm2.com/documentation-preferences-profiles-general.html'
modified_files:
  - src/tree_style_terminal/models/session.py
  - src/tree_style_terminal/controllers/session_manager.py
  - src/tree_style_terminal/widgets/sidebar.py
  - src/tree_style_terminal/main.py
  - tests/unit/test_session.py
  - tests/unit/test_session_actions.py
  - tests/unit/test_session_sidebar.py
priority: high
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Let users rename a session from the sidebar and optionally keep that custom title from being overwritten by automatic cwd/shell-title updates. This strengthens the tree navigation without adding a full profile system.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A session can be renamed from the UI
- [x] #2 A custom title remains stable across automatic title updates
- [x] #3 Clearing the custom title restores automatic naming
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented sidebar session rename via context menu, custom title locking against automatic VTE/CWD title updates, and clearing custom titles to restore automatic naming. Added focused unit coverage and verified the full test suite.
<!-- SECTION:FINAL_SUMMARY:END -->
