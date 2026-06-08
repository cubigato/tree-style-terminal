---
id: TASK-34
title: Evaluate use of padding gap between terminal and sidebar
status: To Do
assignee: []
created_date: '2026-06-01 12:54'
labels:
  - 'area:sidebar'
dependencies: []
priority: low
ordinal: 25500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-32. The current fix adds/keeps padding between the terminal and sidebar so selecting text at the first character of a line is usable, but that area feels like lost space. Re-evaluate later whether the gap can be used better or reduced without bringing back the selection/resizer conflict.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The existing first-character text selection behavior from TASK-32 remains protected.
- [ ] #2 The padding/gap between terminal and sidebar is reviewed with at least one concrete option: keep it, reduce it, make it adaptive, or give it an intentional visual/interaction role.
- [ ] #3 Any implementation stays simple and avoids adding new controls or preferences unless clearly necessary.
<!-- AC:END -->
