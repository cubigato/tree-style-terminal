---
id: TASK-27.6
title: Evaluate realistic Ruff lint rules and cleanup path
status: next
assignee: []
created_date: '2026-05-27 22:19'
updated_date: '2026-05-28 12:13'
labels: []
dependencies: []
references:
  - TASK-27
  - pyproject.toml
  - src
  - tests
parent_task_id: TASK-27
priority: medium
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. Ruff currently reports many findings, but the project should first decide which lint rules are realistic and useful for this codebase instead of blindly accepting every configured rule. Review the current Ruff configuration, decide which rule groups should be kept, relaxed, or deferred, then define a mechanical cleanup path that keeps review noise separate from behavior changes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Current Ruff findings are summarized by rule category and impact.
- [ ] #2 The task recommends which Ruff rules/config sections should be kept, adjusted, or deferred for this project.
- [ ] #3 pyproject.toml Ruff configuration is updated only if the review concludes changes are warranted.
- [ ] #4 Any mechanical fixes are separated from behavior changes and limited to the accepted rule set.
- [ ] #5 A follow-up cleanup task is created if the lint cleanup is too large for this ticket.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 The project has an explicit, documented Ruff/lint policy suitable for the current codebase.
- [ ] #2 If config or mechanical fixes are changed, relevant tests still pass.
<!-- DOD:END -->
