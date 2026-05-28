---
id: TASK-28
title: Handle text drag and drop
status: Done
assignee: []
created_date: '2026-05-28 06:37'
updated_date: '2026-05-28 07:07'
labels:
  - feature
  - 'area:terminal'
  - 'effort:small'
dependencies: []
modified_files:
  - src/tree_style_terminal/widgets/terminal.py
  - tests/test_terminal_widget.py
priority: high
ordinal: 500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Support dropping plain text from other applications onto the active VTE terminal. A user should be able to select text in another app, drag it into Tree Style Terminal, and have that text delivered to the shell/application as terminal input.

Reference behavior: xfce4-terminal. Known source examples are browser address bars and text editors.

Problem to verify:
- Dropping selected text into TST currently does not deliver the text to the running terminal application.
- A cbreak-mode script that completes input via bracketed paste markers or a short burst timeout works in xfce4-terminal, but not in TST when text is dropped.

Expected behavior:
- Dropped text is inserted into the active terminal session, equivalent to a paste/drop in xfce4-terminal.
- If bracketed paste mode is active in the terminal application, dropped text should be delivered in a way that preserves VTE's bracketed-paste behavior.
- Focus should end up on the terminal after a successful drop.
- Non-text drops should be ignored without crashing or changing sessions.

Implementation notes:
- Prefer using VTE/GTK drag-and-drop APIs on the existing `VteTerminal` wrapper instead of app-level clipboard workarounds.
- Keep the change scoped to terminal text input handling; do not add file/URI dropping, sidebar drag handling, or new UI.
- Add focused tests around the terminal wrapper where feasible. Manual verification is expected because full cross-app drag-and-drop is difficult to cover in unit tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Dragging selected plain text from a browser address bar into the active terminal inserts that exact text into the running shell/application.
- [x] #2 Dragging selected plain text from a text editor into the active terminal inserts that exact text, including spaces and Unicode characters.
- [x] #3 Dropped text is delivered as paste-like terminal input so bracketed paste aware programs can complete input consistently with xfce4-terminal.
- [x] #4 After a successful text drop, keyboard focus is on the terminal that received the drop.
- [x] #5 Dropping unsupported data such as files or non-text payloads is ignored without a traceback, crash, or session switch.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented a scoped GTK text drag-and-drop target on VteTerminal. Dropped text is inserted with Vte.Terminal.paste_text() so VTE keeps paste-like terminal semantics, then focus returns to the receiving terminal. Non-text payloads are ignored. Manual cross-app verification against xfce4-terminal is still pending.

Follow-up for focus: after a handled drop, TST now finishes the GTK drop context first, then schedules an idle callback that calls present_with_time(drop_time) on the toplevel window and focuses the VTE widget. This is the portable GTK best-effort path for Xorg and Wayland; Wayland compositors may still reject focus activation by policy.

Manual review completed on Xorg: browser/text-editor text drops insert correctly, bracketed-paste style input works, unsupported drops are ignored, and focus returns to TST after the follow-up focus fix.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Focused terminal-widget tests or documented manual-only coverage exist for the drag/drop handler.
- [x] #2 Manual comparison with xfce4-terminal is documented in implementation notes before review.
- [x] #3 Existing terminal paste, copy, context menu, and session focus behavior still pass their tests.
- [x] #4 No unrelated terminal rendering, sidebar, or clipboard refactor is included.
<!-- DOD:END -->
