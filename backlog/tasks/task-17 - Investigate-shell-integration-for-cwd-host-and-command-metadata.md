---
id: TASK-17
title: Investigate shell integration for cwd host and command metadata
status: To Do
assignee: []
created_date: '2026-05-26 22:10'
updated_date: '2026-05-27 22:25'
labels:
  - feature
  - 'effort:large'
  - 'area:integration'
  - research
dependencies: []
references:
  - 'https://iterm2.com/documentation-shell-integration.html'
priority: low
ordinal: 220
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Research a minimal shell integration for bash, zsh, and fish that can report cwd, host, command start/end, and exit status to Tree Style Terminal. Keep implementation opt-in and avoid requiring it for basic terminal use.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document the escape sequences or protocol TST would consume
- [ ] #2 Identify minimal shell snippets for bash, zsh, and fish
- [ ] #3 List fallback behavior when shell integration is unavailable
<!-- AC:END -->
