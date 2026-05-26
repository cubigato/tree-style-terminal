---
id: TASK-22
title: Keep custom terminal rendering engine out of scope
status: To Do
assignee: []
created_date: '2026-05-26 22:11'
labels:
  - research
  - not-now
  - 'effort:large'
  - 'area:architecture'
dependencies: []
references:
  - ARCHITECTURE.md
priority: low
ordinal: 300
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Record the decision boundary for not replacing VTE with a custom GPU terminal renderer. Tree Style Terminal should continue to rely on the standard terminal component unless a future architecture decision explicitly changes that.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document why VTE remains the terminal engine
- [ ] #2 List what renderer-level features are delegated to VTE
- [ ] #3 Close this task once the out-of-scope decision is captured in project docs
<!-- AC:END -->
