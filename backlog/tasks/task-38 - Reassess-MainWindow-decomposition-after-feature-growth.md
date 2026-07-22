---
id: TASK-38
title: Reassess MainWindow decomposition after feature growth
status: To Do
assignee: []
created_date: '2026-07-22 23:03'
labels:
  - cleanup
  - 'area:architecture'
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/main.py
priority: medium
ordinal: 37500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
main.py has accumulated additional header-bar actions, dialogs, workspace-profile flows, session callbacks, and feature orchestration after the earlier TASK-27 cleanup. Review the remaining MainWindow responsibilities and turn worthwhile extractions into small behavior-preserving follow-up tasks. This task is planning/triage only; it must not bundle a broad refactor.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 MainWindow methods are inventoried by cohesive responsibility, with current call sites and test coverage noted.
- [ ] #2 Only extractions that reduce coupling or isolate a clear responsibility are proposed; moves that merely add indirection are rejected.
- [ ] #3 Accepted cleanup candidates are split into independently reviewable follow-up tasks with explicit scope and behavior-preserving criteria.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 No production code is changed as part of this review task.
<!-- DOD:END -->
