---
id: TASK-27.8
title: Reassess whether ARCHITECTURE.md reflects working code
status: next
assignee: []
created_date: '2026-05-27 22:19'
updated_date: '2026-05-31 15:03'
labels: []
dependencies: []
references:
  - TASK-27
  - ARCHITECTURE.md
  - src/tree_style_terminal
parent_task_id: TASK-27
priority: medium
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. ARCHITECTURE.md was written before implementation started and may describe planned architecture rather than the working application. Treat this as an open review, not an instruction to force the code toward the document. Working code wins over architecture astronomy: assess what the document still explains accurately, what is obsolete, and whether it should be updated, shortened, split into historical notes, or replaced with a concise current architecture overview.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ARCHITECTURE.md is reviewed against the current implementation, especially SessionManager callbacks, SidebarController synchronization, ShortcutController actions, and actual module layout.
- [ ] #2 Obsolete aspirational sections are identified separately from still-useful design context.
- [ ] #3 The outcome recommends whether to update, shrink, replace, or archive the document.
- [ ] #4 No code is changed as part of this architecture-document review unless a separate implementation task is created and accepted.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Review-Ergebnis: ARCHITECTURE.md war ein Vor-Implementierungs-Plan. Entscheidung: aktualisiert und gestrafft statt verworfen/archiviert. Korrekturen: signalbasiertes Modell -> reales callbackbasiertes Modell (SessionManager-Callbacks, von MainWindow an SidebarController verdrahtet); ShortcutController als Gio.SimpleAction + Gtk.AccelGroup (nicht Gtk.ShortcutController); Tech-Stack bereinigt (kein pytest-gtk, VTE 2.91, PyYAML, statische Version statt setuptools_scm); Verzeichnislayout an tatsaechlichen Code angepasst (config/, css_loader.py, __main__.py, Unterstrich-Paketname). Aspirational/noch-nicht-umgesetzt (CI/CD, .deb/Flatpak, Plugins, Session-Persistenz, Splits) in einen Roadmap-Abschnitt verschoben. CI bleibt bewusst als langfristiger Roadmap-Punkt. Kein Code geaendert.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A clear documentation decision exists in the task notes or in an updated ARCHITECTURE.md.
- [ ] #2 If ARCHITECTURE.md is changed, it describes the working code rather than forcing unimplemented architecture.
<!-- DOD:END -->
