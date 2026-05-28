---
id: TASK-27
title: code review and cleanup
status: Done
assignee: []
created_date: '2026-05-27 21:54'
updated_date: '2026-05-28 07:49'
labels: []
dependencies: []
references:
  - src/tree_style_terminal/main.py
  - src/tree_style_terminal/widgets/terminal.py
  - src/tree_style_terminal/controllers/session_manager.py
  - src/tree_style_terminal/controllers/sidebar.py
  - src/tree_style_terminal/controllers/shortcuts.py
  - src/tree_style_terminal/config/manager.py
  - ARCHITECTURE.md
priority: high
ordinal: 2500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The codebase has grown organically and some implementation details have drifted from the intended architecture. TASK-27 is a review and triage task, not an implementation cleanup task.

The expected result of completing TASK-27 is a set of smaller, concrete, human-reviewable backlog tasks. Each follow-up task must be narrow enough to implement and review independently, and must reference TASK-27 so its origin is clear.

Initial areas to inspect:
- MainWindow in src/tree_style_terminal/main.py is very large and mixes application wiring, CSS/DPI logic, headerbar callbacks, legacy terminal management, session callbacks, sidebar behavior, debug output, and CLI diagnostics.
- MainWindow still contains a legacy terminal dictionary path (_create_new_terminal/_switch_to_terminal/_close_terminal/active_terminal_id) alongside the newer SessionManager-driven session path. Review whether that path is dead, test-only compatibility, or still reachable.
- CSSLoader in main.py owns theme detection, runtime CSS generation, DPI scaling, sidebar transparency CSS, and console output. Review whether this should stay there or move behind a smaller helper without changing behavior.
- Logging and diagnostics are inconsistent: app code uses both print() and logging, including normal runtime messages in UI/session paths.
- SidebarController contains manual TreeStore synchronization and unused-looking helper paths such as move/remove variants and bind_session_tree_events(). Review actual call sites before proposing removal.
- ShortcutController has action registration, accelerator parsing, window wiring, and action-state updates in one place. Review for simple deduplication and config validation gaps only.
- Config handling uses shallow copies for nested defaults and repeated load_config() calls through the global config manager. Review for real risks before proposing changes.
- Architecture docs mention planned signals and structure that do not fully match the current callback/manual-sync implementation. Create documentation follow-up tasks only after the intended direction is clear.

Keep the review conservative: identify concrete problems, turn accepted findings into small backlog tasks, and do not touch implementation code as part of TASK-27.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A written review note exists in TASK-27 notes or linked documentation with concrete cleanup candidates, rationale, affected files, and expected risk.
- [x] #2 Each proposed cleanup item states whether it is proven dead code, duplication, documentation drift, missing test coverage, or a maintainability refactor.
- [x] #3 The human-reviewed findings are converted into smaller backlog tasks instead of being implemented directly in TASK-27.
- [x] #4 Every follow-up task created from this review references TASK-27 and has focused scope, acceptance criteria, and relevant file references.
- [x] #5 No implementation code is changed as part of TASK-27.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inventory: map the main runtime paths for startup, session creation/selection/closing, shortcuts, config loading, theme/CSS loading, and sidebar synchronization.
2. Call-site review: for each suspected dead or redundant path, prove whether it is reachable via code search and tests before proposing a follow-up task.
3. Group findings into small candidate tasks by area and risk: dead code removal, helper extraction, logging cleanup, config safety, documentation drift, and missing tests.
4. Stop for human review of the candidate task list before creating or changing backlog items beyond TASK-27.
5. After review, create the accepted follow-up tasks in Backlog.md. Each follow-up must reference TASK-27 and include concrete scope, acceptance criteria, and relevant file references.
6. Mark TASK-27 ready for completion only after the accepted follow-up tasks exist and are linked back to TASK-27.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Review note 2026-05-28: candidate follow-up tasks for human review

Scope reviewed:
- Startup and app/window wiring in src/tree_style_terminal/main.py.
- Session creation, selection, close, and title/cwd update paths in src/tree_style_terminal/controllers/session_manager.py and MainWindow callbacks.
- Headerbar and shortcut routing in src/tree_style_terminal/main.py and src/tree_style_terminal/controllers/shortcuts.py.
- Sidebar TreeStore synchronization in src/tree_style_terminal/controllers/sidebar.py and src/tree_style_terminal/widgets/sidebar.py.
- Config loading, validation, and default merging in src/tree_style_terminal/config/manager.py and defaults.py.
- Related tests and tool output.

Verification commands run:
- rg call-site searches for legacy terminal methods, CSSLoader usage, sidebar controller helpers, shortcut config usage, and mixed import styles.
- .venv/bin/python -m pytest tests/unit/test_config.py tests/unit/test_shortcuts.py tests/unit/test_sidebar_controller.py tests/test_main_window.py -> 75 passed.
- .venv/bin/python -m ruff check src tests --statistics -> failed with 1348 findings; 1164 fixable. Dominant categories: 1048 W293 blank-line-with-whitespace, 70 E402, 46 I001, 39 UP007, 38 F401, 20 W292.

Candidate follow-up tasks:

1. Remove or retire legacy MainWindow terminal management
Type: proven dead-code candidate plus test drift.
Evidence: src/tree_style_terminal/main.py keeps self.terminals, terminal_counter, active_terminal_id at lines 450-453 and legacy methods _create_new_terminal/_switch_to_terminal/_close_terminal at lines 781-882. Runtime buttons now route through ShortcutController and SessionManager. rg found productive references only inside the legacy methods and theme update, while tests/test_main_window.py still asserts these attributes and methods exist. The UI file only contains welcome_new_terminal_button, which activates _on_new_terminal_clicked and therefore the SessionManager path.
Risk: medium. Tests currently encode the old API, and _update_terminal_themes still iterates self.terminals. Follow-up should first update tests to assert the current SessionManager behavior, then remove legacy state/methods if no runtime path remains.
Suggested scope: main.py, tests/test_main_window.py, maybe tests around theme update.

2. Extract CSS/theme/DPI loading out of main.py without behavior changes
Type: maintainability refactor.
Evidence: CSSLoader spans src/tree_style_terminal/main.py lines 33-360 and owns theme detection, CSS provider loading, DPI scale detection, runtime sidebar transparency CSS, and console output. Tests import CSSLoader directly from tree_style_terminal.main, so extraction needs compatibility or coordinated test updates.
Risk: medium. This code touches startup, theme switching, transparency, and DPI behavior. Keep the first task as a pure move to a dedicated module such as src/tree_style_terminal/ui/css_loader.py or src/tree_style_terminal/config/css_loader.py, with import compatibility if needed.
Suggested scope: move class, update imports/tests, keep public behavior and test expectations unchanged.

3. Normalize runtime diagnostics: use logging in app paths, keep print for explicit CLI output
Type: maintainability refactor.
Evidence: main.py uses print throughout CSS loading, transparency checks, legacy/session UI paths, focus/sidebar toggles, theme updates, startup, and CLI diagnostics. There is already module logging in main.py and other controllers. print remains appropriate for --show-info and --test-fonts output, but normal UI/runtime messages should be logging.
Risk: low to medium. User-visible CLI output must be preserved for explicit diagnostic flags. Runtime logs may affect tests only if they assert stdout.
Suggested scope: main.py only at first. Do not mix with CSS extraction or legacy removal.

4. Review and simplify SidebarController helper API
Type: dead-code candidate plus documentation drift.
Evidence: productive call-site search found remove_session_with_adoption used by MainWindow, but move_session, _cleanup_session_mapping, _extract_children_data, and bind_session_tree_events are not used by runtime code. bind_session_tree_events is a no-op placeholder kept alive by tests. Comments at lines 55-58 and docstring at 350-360 talk about event binding/manual refresh, while actual MainWindow integration performs direct add/update/remove calls.
Risk: medium. TreeStore iter invalidation and adoption behavior are easy to break. Follow-up should either remove unused helpers and adjust tests, or document them as intentionally reserved only if there is a near-term feature requiring them.
Suggested scope: src/tree_style_terminal/controllers/sidebar.py, tests/unit/test_sidebar_controller.py, tests/unit/test_session_tree_events.py.

5. Harden ConfigManager default copying and shortcut validation
Type: small correctness/maintainability task.
Evidence: ConfigManager assigns DEFAULT_CONFIG.copy() when creating a missing config and uses shallow copies in _merge_with_defaults. Nested dictionaries are currently mutable shared structures unless overwritten by deep_merge recursion. Validation only checks shortcuts.terminal_search is a string; ShortcutController later relies on Gtk.accelerator_parse and logs invalid accelerators at runtime.
Risk: low. Use copy.deepcopy for defaults/merge results and add a focused validation test. Shortcut validation can either reject invalid GTK accelerators at config load or remain runtime-only, but the decision should be explicit.
Suggested scope: src/tree_style_terminal/config/manager.py, src/tree_style_terminal/config/defaults.py, tests/unit/test_config.py.

6. Create a mechanical lint cleanup task instead of mixing style with architecture cleanup
Type: tooling/style debt.
Evidence: ruff currently reports 1348 findings across src and tests, with 1164 auto-fixable. pyproject.toml also uses deprecated top-level Ruff lint keys. Many findings are whitespace/import modernization and should be handled mechanically in a separate task to keep architecture diffs reviewable.
Risk: low if split as mechanical only. High review noise if bundled with behavior changes.
Suggested scope: pyproject.toml plus one mechanical ruff-format/ruff-fix pass, then tests. Consider limiting first pass to safe fixes only.

7. Standardize test imports to the installed package namespace
Type: test cleanup and maintenance.
Evidence: tests mix imports from src.tree_style_terminal and tree_style_terminal. Examples: tests/test_main_window.py and tests/test_terminal_widget.py use src.tree_style_terminal, while most unit/integration tests use tree_style_terminal. This can hide packaging/import differences.
Risk: low. Should be separate from runtime changes so failures are easy to interpret.
Suggested scope: tests/test_main_window.py, tests/test_terminal_widget.py, tests/test_imports.py, possibly conftest/import path setup.

8. Align ARCHITECTURE.md with current implementation after cleanup direction is decided
Type: documentation drift.
Evidence: ARCHITECTURE.md describes signals such as node-added/node-removed and ShortcutController as Gtk.ShortcutController based. Current code uses SessionManager callbacks, manual SidebarController updates, and Gtk.AccelGroup/Gio.SimpleAction. This should not be fixed before deciding whether to preserve current architecture or move toward the documented one.
Risk: low. Timing matters: document after the implementation direction is accepted.
Suggested scope: ARCHITECTURE.md only unless implementation changes are approved first.

Recommendation for review:
- Approve creating follow-up tasks for 1, 4, 5, 6, 7 immediately. They are concrete and bounded.
- Approve 2 only if moving CSSLoader out of main.py is worth the churn now.
- Approve 3 after deciding whether logging behavior should become consistent before or after CSSLoader extraction.
- Defer 8 until the accepted cleanup tasks clarify the intended architecture.

No implementation code was changed during this review.

Follow-up tasks created after human review:
- TASK-27.1 Retire legacy MainWindow terminal management (medium)
- TASK-27.2 Extract CSSLoader from main.py (high)
- TASK-27.3 Normalize runtime diagnostics to logging (high)
- TASK-27.4 Simplify SidebarController helper API (medium)
- TASK-27.5 Harden ConfigManager defaults and shortcut validation (low)
- TASK-27.6 Evaluate realistic Ruff lint rules and cleanup path (medium)
- TASK-27.7 Standardize tests on package imports (high)
- TASK-27.8 Reassess whether ARCHITECTURE.md reflects working code (medium)

All follow-up tasks are children of TASK-27 and include TASK-27 as a reference.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Human review has accepted the candidate cleanup task list.
- [x] #2 Accepted follow-up tasks have been created in Backlog.md and each references TASK-27.
- [x] #3 Each follow-up task is small enough to implement independently and includes clear acceptance criteria.
- [x] #4 TASK-27 contains or links the review notes that explain why the follow-up tasks were created.
<!-- DOD:END -->
