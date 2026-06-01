---
id: TASK-27.14
title: Resolve behavioral Ruff findings (manual review)
status: Done
assignee: []
created_date: '2026-05-31 12:56'
updated_date: '2026-06-01 12:55'
labels:
  - cleanup
dependencies: []
parent_task_id: TASK-27
ordinal: 29500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27.6. These ~41 findings require human judgement rather than autofix because they may hide bugs or change behavior: UP035 (8), F841 (7), B904 (6), E722 (5), SIM102 (5), F811 (4), UP038 (2), E711 (1), B007 (1), SIM105 (1), SIM108 (1). Do AFTER the mechanical autofix task to avoid diff noise.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 E722 bare-except occurrences reviewed and replaced with specific exceptions or justified
- [ ] #2 B904 raise-without-from-inside-except fixed (raise ... from err/None)
- [ ] #3 F841 unused-variable and F811 redefined-while-unused reviewed for latent bugs
- [ ] #4 UP035/UP038, E711, B007, SIM102/105/108 addressed or explicitly waived
- [ ] #5 Test suite passes after changes
<!-- AC:END -->
