---
id: TASK-27.6
title: Evaluate realistic Ruff lint rules and cleanup path
status: Done
assignee: []
created_date: '2026-05-27 22:19'
updated_date: '2026-05-31 13:07'
labels: []
dependencies: []
references:
  - TASK-27
  - pyproject.toml
  - src
  - tests
parent_task_id: TASK-27
priority: medium
ordinal: 17500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. Ruff currently reports many findings, but the project should first decide which lint rules are realistic and useful for this codebase instead of blindly accepting every configured rule. Review the current Ruff configuration, decide which rule groups should be kept, relaxed, or deferred, then define a mechanical cleanup path that keeps review noise separate from behavior changes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Current Ruff findings are summarized by rule category and impact.
- [x] #2 The task recommends which Ruff rules/config sections should be kept, adjusted, or deferred for this project.
- [x] #3 pyproject.toml Ruff configuration is updated only if the review concludes changes are warranted.
- [x] #4 Any mechanical fixes are separated from behavior changes and limited to the accepted rule set.
- [x] #5 A follow-up cleanup task is created if the lint cleanup is too large for this ticket.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Ruff findings summary (baseline 1248 errors, src+tests):

Mechanical / autofixable (review-noise only, ~1125):
  W293 blank-line-with-whitespace 942, I001 unsorted-imports 56,
  UP007 union-annotation 48, F401 unused-import 31, UP006 pep585 14,
  W292 missing-newline 13, W291 trailing-whitespace 9, UP015/UP024/UP037 3 each,
  SIM910 2, F541 1.

Behavioral / manual review (~41):
  UP035 deprecated-import 8, F841 unused-variable 7, B904 raise-without-from 6,
  E722 bare-except 5, SIM102 collapsible-if 5, F811 redefined 4, UP038 2,
  E711 1, B007 1, SIM105 1, SIM108 1.

False positives for this codebase (now ignored, 82 cleared):
  E402 import-not-at-top 71  -> caused by required GTK gi.require_version() before
       'from gi.repository import ...'. Disabled project-wide.
  N806 non-lowercase-var 11  -> mostly 'MockVteTerminal' patch context names in
       tests (unittest.mock convention). Disabled for tests/** only; kept for src.

Policy decisions:
- Keep the rule set E,W,F,I,N,B,UP,C4,SIM (all reasonable for a py311 GTK app).
- Keep E501 delegated to the formatter (already ignored).
- Add E402 to lint.ignore (justified GTK pattern).
- Add tests/** -> N806 per-file-ignore.
- Migrated deprecated top-level [tool.ruff] select/ignore/per-file-ignores into
  [tool.ruff.lint] / [tool.ruff.lint.per-file-ignores] (removes ruff deprecation warning).

Config change applied to pyproject.toml; 253 tests pass; no behavior change.

Cleanup path: lint cleanup is too large for this ticket, split into follow-ups:
- TASK-27.13: apply mechanical ruff --fix autofixes (single noise-only commit).
- TASK-27.14: resolve behavioral findings (manual review).
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 The project has an explicit, documented Ruff/lint policy suitable for the current codebase.
- [ ] #2 If config or mechanical fixes are changed, relevant tests still pass.
<!-- DOD:END -->
