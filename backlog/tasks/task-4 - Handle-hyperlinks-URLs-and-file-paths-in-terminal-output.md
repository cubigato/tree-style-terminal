---
id: TASK-4
title: 'Handle hyperlinks, URLs, and file paths in terminal output'
status: Done
assignee: []
created_date: '2026-05-26 22:08'
updated_date: '2026-05-28 08:15'
labels:
  - feature
  - 'effort:small'
  - 'area:terminal'
dependencies: []
references:
  - 'https://gnome.pages.gitlab.gnome.org/vte/gtk3/class.Terminal.html'
modified_files:
  - src/tree_style_terminal/widgets/terminal.py
  - tests/test_terminal_widget.py
priority: high
ordinal: 125
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enable VTE-supported hyperlinks and add minimal context actions for opening/copying links or detected file paths. Prefer VTE APIs and conservative matching over custom parsing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 OSC 8 hyperlinks are enabled where supported by VTE
- [x] #2 Right-clicking a link exposes open and copy actions
- [x] #3 Plain URL or file-path detection does not interfere with normal terminal selection
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Enabled VTE OSC 8 hyperlinks, added conservative URL/file path matches, and extended the terminal context menu with Open/Copy actions that appear only when right-clicking a detected target. Path targets use file/path labels. Hyperlink setup failures are logged as warnings so initialization problems are visible above debug logging.
<!-- SECTION:FINAL_SUMMARY:END -->
