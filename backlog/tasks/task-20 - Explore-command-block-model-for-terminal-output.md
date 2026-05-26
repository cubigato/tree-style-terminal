---
id: TASK-20
title: Explore command block model for terminal output
status: To Do
assignee: []
created_date: '2026-05-26 22:10'
labels:
  - feature
  - 'effort:large'
  - 'area:terminal'
  - research
dependencies: []
references:
  - 'https://docs.warp.dev/features/windows'
priority: low
ordinal: 240
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate whether Tree Style Terminal should model command/output blocks similar to modern AI-oriented terminals. With VTE this likely requires shell integration or prompt detection, so treat this as research before implementation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document at least two possible approaches: shell integration and prompt heuristics
- [ ] #2 Assess reliability and UX cost for each approach
- [ ] #3 Recommend whether to implement, defer, or reject
<!-- AC:END -->
