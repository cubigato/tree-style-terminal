---
id: TASK-26
title: 'Bug: Terminal verliert Fokus nach Session-Wechsel per Maus'
status: Done
assignee: []
created_date: '2026-05-27 21:39'
updated_date: '2026-05-30 00:16'
labels:
  - bug
dependencies: []
modified_files:
  - src/tree_style_terminal/main.py
  - src/tree_style_terminal/widgets/sidebar.py
  - src/tree_style_terminal/widgets/terminal.py
  - tests/test_main_window.py
  - tests/unit/test_session_sidebar.py
priority: medium
ordinal: 6500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Beim Wechseln einer Session in der Sidebar oder beim Erstellen einer neuen Session per Plus-Button blieb der Fokus auf Sidebar bzw. Button. Dadurch musste vor dem Tippen erneut ins Terminal geklickt werden.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Nach Mausauswahl einer Session liegt der Fokus wieder im aktiven Terminal.
- [x] #2 Nach Klick auf den Plus-Button fuer eine neue Session liegt der Fokus in der neuen Terminal-Session.
<!-- AC:END -->



## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Behoben durch Pointer-Erkennung bei Sidebar-Auswahl, Fokus-Weiterleitung auf das interne VTE-Widget und Fokus-Rueckgabe nach Session-Erstellung.
<!-- SECTION:FINAL_SUMMARY:END -->
