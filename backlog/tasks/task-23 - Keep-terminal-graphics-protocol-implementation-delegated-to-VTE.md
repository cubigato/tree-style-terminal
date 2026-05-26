---
id: TASK-23
title: Keep terminal graphics protocol implementation delegated to VTE
status: To Do
assignee: []
created_date: '2026-05-26 22:11'
labels:
  - research
  - not-now
  - 'effort:large'
  - 'area:terminal'
dependencies: []
references:
  - 'https://gnome.pages.gitlab.gnome.org/vte/gtk3/class.Terminal.html'
priority: low
ordinal: 310
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Record that Kitty graphics, Sixel, and similar renderer-level protocols should not be hand-implemented in Tree Style Terminal. If VTE supports them, expose configuration only where needed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document the delegation boundary for graphics protocols
- [ ] #2 Note current VTE support expectations at the time this is reviewed
- [ ] #3 Avoid adding custom parser or renderer code for graphics protocols
<!-- AC:END -->
