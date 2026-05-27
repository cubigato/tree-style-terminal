---
id: TASK-19
title: Explore remote SSH session helpers
status: To Do
assignee: []
created_date: '2026-05-26 22:10'
updated_date: '2026-05-27 22:25'
labels:
  - feature
  - 'effort:large'
  - 'area:remote'
  - research
dependencies: []
references:
  - 'https://wezterm.org/'
  - 'https://iterm2.com/documentation-shell-integration.html'
priority: low
ordinal: 240
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Explore lightweight SSH helpers such as profiles for remote hosts and creating child sessions in a known SSH context. Avoid building a multiplexer; this should remain a convenience layer over normal terminal sessions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document possible SSH profile configuration
- [ ] #2 Identify what can be inferred without shell integration
- [ ] #3 Recommend whether this belongs before or after shell integration
<!-- AC:END -->
