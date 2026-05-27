---
id: TASK-4
title: 'Handle hyperlinks, URLs, and file paths in terminal output'
status: next
assignee: []
created_date: '2026-05-26 22:08'
updated_date: '2026-05-27 21:46'
labels:
  - feature
  - 'effort:small'
  - 'area:terminal'
dependencies: []
references:
  - 'https://gnome.pages.gitlab.gnome.org/vte/gtk3/class.Terminal.html'
priority: high
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enable VTE-supported hyperlinks and add minimal context actions for opening/copying links or detected file paths. Prefer VTE APIs and conservative matching over custom parsing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 OSC 8 hyperlinks are enabled where supported by VTE
- [ ] #2 Right-clicking a link exposes open and copy actions
- [ ] #3 Plain URL or file-path detection does not interfere with normal terminal selection
<!-- AC:END -->
