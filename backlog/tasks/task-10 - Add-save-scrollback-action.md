---
id: TASK-10
title: Add save scrollback action
status: To Do
assignee: []
created_date: '2026-05-26 22:09'
labels:
  - feature
  - 'effort:small'
  - 'area:terminal'
dependencies: []
references:
  - 'https://help.gnome.org/gnome-terminal/'
priority: medium
ordinal: 80
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow saving the visible terminal scrollback/content of the active session to a text file. This should use VTE text extraction and a simple GTK file chooser.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 User can save active terminal contents to a chosen file
- [ ] #2 Saved output preserves line breaks
- [ ] #3 Save failures are surfaced without crashing the app
<!-- AC:END -->
