---
id: TASK-36.4
title: Support real host shell sessions from Flatpak
status: next
assignee: []
created_date: '2026-07-23 13:16'
updated_date: '2026-07-23 13:40'
labels:
  - packaging
  - flatpak
  - terminal
  - release
dependencies:
  - TASK-36.1
  - TASK-36.2
references:
  - >-
    https://docs.flatpak.org/en/latest/flatpak-command-reference.html#flatpak-spawn
  - 'https://github.com/flathub/com.raggesilver.BlackBox'
  - >-
    https://gitlab.gnome.org/raggesilver/blackbox/-/blob/v0.14.0/src/widgets/Terminal.vala
modified_files:
  - src/tree_style_terminal/widgets/terminal.py
  - src/tree_style_terminal/controllers/session_manager.py
  - tests/test_terminal_widget.py
  - tests/unit/test_session_actions.py
parent_task_id: TASK-36
priority: low
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Optionally explore real host shell sessions from a Flatpak build after the 1.0 Debian and AppImage release path is complete. Run the user's real host shell with correct terminal semantics instead of silently opening a shell inside the Flatpak runtime. This work is not a 1.0 prerequisite and native behavior must remain unchanged.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Flatpak sessions run the user's configured host shell and host environment rather than the runtime shell, while native installations retain existing shell behavior.
- [ ] #2 Interactive PTY behavior supports job control, terminal resize, signals, exit-status handling, and cleanup without orphaning host processes.
- [ ] #3 Requested host working directories and workspace-profile commands work correctly, including paths whose sandbox view differs from the host view.
- [ ] #4 Current-directory tracking does not rely on host process visibility through the sandbox's /proc namespace and degrades safely when shell directory reporting is unavailable.
- [ ] #5 Automated unit coverage exercises backend selection and failure paths, and an integration smoke test demonstrates host identity, working directory, shell startup, resize, and clean exit.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-07-23: Flatpak was removed from the 1.0 blocking path. AppImage is the preferred portable 1.0 artifact because it can run host shell sessions directly without a Flatpak host-command bridge.
<!-- SECTION:NOTES:END -->
