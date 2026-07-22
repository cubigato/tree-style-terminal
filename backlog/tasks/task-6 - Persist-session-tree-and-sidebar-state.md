---
id: TASK-6
title: Export session trees as workspace profiles
status: next
assignee: []
created_date: '2026-05-26 22:08'
updated_date: '2026-07-22 12:34'
labels:
  - feature
  - 'effort:medium'
  - 'area:session'
  - 'area:config'
  - 'area:workspace'
dependencies:
  - TASK-14
  - TASK-35
references:
  - CONFIG.md
priority: medium
ordinal: 500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make reusable workspace profiles easier to create by explicitly exporting live sessions to the version 1 YAML profile format defined by TASK-14 and extended with multi-root support by TASK-35. The generated file must be directly loadable with `tst --profile FILE` / `tst -p FILE`.

Add an export button to the existing linked session-action buttons in the headerbar, next to new sibling, new child, and close. Clicking it opens a small menu with two choices: save the selected session and all of its descendants, or save all sessions. After choosing the scope, show a file chooser for the YAML destination.

The selected-subtree choice writes the selected session as the profile root. The all-sessions choice writes every root tree, using the multi-root profile form when necessary. The export is always initiated explicitly by the user. It is not session persistence: do not save under XDG state, do not write automatically after changes, and do not load or restore anything implicitly at startup.

Export nodes recursively using the existing profile fields `title`, `workdir`, optional `command`, and `children`. Runtime sessions generally have no reconstructable startup command, so the exporter must not invent one. Extend profile nodes with optional `selected: true`; omission means false. A profile containing more than one selected node is invalid. When a loaded profile has one selected node, that session becomes active after the whole profile has been created.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The generated document uses the TASK-14 version 1 profile structure and can be loaded by the existing `--profile` / `-p` startup path.
- [ ] #2 The exported root and descendants preserve tree structure, titles, and working directories; the exporter does not invent startup commands that cannot be reconstructed from live sessions.
- [ ] #3 Profile nodes accept optional boolean `selected`; omission is false, exactly zero or one selected node is valid, and more than one `selected: true` produces a useful YAML-path validation error.
- [ ] #4 The exporter writes `selected: true` only on the currently selected session when that session belongs to the exported tree.
- [ ] #5 Loading a profile with one selected node activates that session only after the complete tree has been created; a profile without `selected: true` keeps the existing default selection behavior.
- [ ] #6 Writing failures are reported clearly and do not damage an existing destination file; automated tests cover serialization, round-trip loading, selection validation, and write failure behavior.
- [ ] #7 The headerbar has an export button beside the existing new-sibling, new-child, and close-session controls; it is disabled when there are no sessions.
- [ ] #8 Clicking the export button opens a menu with exactly two scopes: the selected session plus all descendants, or all sessions.
- [ ] #9 After either scope is chosen, a file chooser lets the user select the destination YAML file; cancelling leaves the filesystem unchanged.
- [ ] #10 Selected-subtree export writes that session as `root`; all-sessions export includes every root and uses the TASK-35 multi-root form when more than one root exists.
- [ ] #11 Profile export occurs only after the user explicitly chooses an export scope and destination; no profile or session state is written or loaded automatically.
<!-- AC:END -->





## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extend the shared workspace profile node model and loader with optional `selected` validation across all roots and descendants.
2. Add a serializer for either the selected session subtree or all root trees, emitting the existing version 1 profile structure plus TASK-35 multi-root form where needed.
3. Add an export button beside the existing headerbar session controls. Its menu offers selected session plus children or all sessions, then opens a YAML save dialog.
4. Write the chosen destination atomically and report failures without damaging an existing file.
5. Update profile startup so selection is applied after every root tree has been created.
6. Document the export workflow and `selected` field, and add focused loader, serializer, UI-action, startup, and failure tests.
<!-- SECTION:PLAN:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: Codex
created: 2026-07-22 12:25
---
Rescoped from automatic XDG session persistence to explicit export of reusable TASK-14 workspace profiles. Automatic saving, implicit startup restore, expanded-row persistence, and multi-instance state coordination are intentionally out of scope. Selection is represented inline as `selected: true`, without session IDs.
---

author: Codex
created: 2026-07-22 12:33
---
UI scope clarified: a new export button joins the existing linked headerbar session controls. Its menu offers selected session plus descendants or all sessions, followed by a YAML save dialog. All-session export depends on TASK-35 multi-root profile support.
---
<!-- COMMENTS:END -->
