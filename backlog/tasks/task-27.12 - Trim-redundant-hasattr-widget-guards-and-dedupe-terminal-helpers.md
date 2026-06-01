---
id: TASK-27.12
title: Trim redundant hasattr widget guards and dedupe terminal helpers
status: next
assignee: []
created_date: '2026-05-30 09:42'
updated_date: '2026-05-31 15:19'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/main.py
  - src/tree_style_terminal/controllers/shortcuts.py
parent_task_id: TASK-27
priority: medium
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. Three small maintainability cleanups in the session/terminal wiring. (E) Defensive hasattr(terminal_widget, '<method>') guards in shortcuts.py and main.py protect calls to grab_focus/copy_clipboard/paste_clipboard/show_search/apply_theme, which always exist on VteTerminal, so the guards are noise. (F) The terminal-stack child name 'session_{pid}' is built inline in three places in main.py (_on_session_created, _on_session_closed, _on_session_selected_by_manager). (G) Terminal-focus logic (get_terminal_widget -> grab_focus) is duplicated between MainWindow.focus_terminal and ShortcutController._on_focus_terminal. Consolidate without changing behavior.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Redundant hasattr(widget, method) guards on always-present VteTerminal methods are removed (keep only the 'widget is not None' check).
- [ ] #2 The 'session_{pid}' terminal-stack name is produced by a single small helper and used by all three main.py call sites.
- [ ] #3 Terminal-focus logic is defined once and reused; no duplicated get_terminal_widget+grab_focus blocks remain.
- [ ] #4 Focus, copy/paste, search, theme, and session-switch behavior is unchanged.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Goal: reduce noise and duplication in session/terminal wiring. Pure maintainability, no behavior change.

E - Drop redundant hasattr guards
- shortcuts.py: _on_focus_terminal (grab_focus), _on_terminal_copy (copy_clipboard), _on_terminal_paste (paste_clipboard), _on_terminal_search (show_search).
- main.py: focus_terminal (grab_focus).
- Keep the 'if terminal_widget' None-check and the surrounding try/except; only drop the hasattr part. Note: SessionManager.set_theme's hasattr(widget,'apply_theme') and _update_terminal_themes can be simplified too once TASK-27.1 lands; coordinate to avoid conflicts.

F - Single source for stack name
- Add a small helper (e.g. module-level _terminal_stack_name(session) -> f'session_{session.pid}' or a MainWindow method) and use it in _on_session_created, _on_session_closed, _on_session_selected_by_manager.

G - Dedupe focus logic
- Have ShortcutController._on_focus_terminal delegate to MainWindow.focus_terminal (main_window is already held) instead of repeating get_terminal_widget+grab_focus, or extract one shared helper. Pick the option that keeps the existing logging/behavior.

Validate (DoD)
- .venv/bin/python -m pytest tests/unit/test_shortcuts.py tests/test_main_window.py tests/integration/test_sidebar_focus.py -q

Risks / what could go wrong
- A test stubs a terminal widget without a given method and relied on the hasattr guard to skip it: check tests use real VteTerminal or Mock (Mock auto-provides attributes, so removal is safe) before deleting guards.
- Coordination with TASK-27.1: that task also touches _update_terminal_themes; sequence to avoid merge conflicts (do this after 27.1 or keep edits disjoint).
- Focus dedupe via delegation could change focus timing if main_window is None in some test context: guard the delegation.
- Scope creep: keep to E/F/G only; do not refactor unrelated handlers.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Lower-priority maintainability bundle. E: hasattr guards on grab_focus/copy_clipboard/paste_clipboard/show_search/apply_theme are redundant (methods always on VteTerminal). F: 'session_{pid}' built inline 3x in main.py. G: focus logic duplicated in main.focus_terminal and shortcuts._on_focus_terminal. Coordinate with TASK-27.1 which also edits _update_terminal_themes.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Focused main-window, shortcut, and focus integration tests pass.
- [ ] #2 No functional change beyond the consolidations above.
<!-- DOD:END -->
