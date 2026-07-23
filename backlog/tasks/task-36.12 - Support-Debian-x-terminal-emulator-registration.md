---
id: TASK-36.12
title: Support Debian x-terminal-emulator registration
status: To Do
assignee: []
created_date: '2026-07-23 23:13'
labels:
  - packaging
  - debian
  - cli
dependencies:
  - TASK-36.3
references:
  - >-
    https://www.debian.org/doc/debian-policy/ch-customized-programs.html#packages-providing-a-terminal-emulator
documentation:
  - PACKAGING.md
  - debian/tree-style-terminal.1
parent_task_id: TASK-36
priority: medium
ordinal: 3200
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make Tree Style Terminal compatible with Debian's generic terminal-emulator contract so users and applications can select it through the x-terminal-emulator alternative. TASK-36.3 intentionally omitted the registration because the application did not support the required command-execution and title options. Add the missing command-line behavior, then update the Debian package, Podman verification workflow, manual page, and packaging documentation so installation and removal manage the alternative safely.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Both public commands accept `-e command [arguments...]`, start the requested program in the initial terminal session, and preserve the supplied argument vector without shell reinterpretation, including arguments beginning with `-`.
- [ ] #2 Both public commands accept `-T title` and apply the requested initial window title.
- [ ] #3 The Debian package declares the terminal-emulator capability and registers Tree Style Terminal as an `x-terminal-emulator` alternative, including the matching manual-page alternative and the Debian-prescribed priority.
- [ ] #4 Installing, upgrading, reinstalling, and removing the package updates the alternatives database safely without overriding an explicit user choice or breaking another installed terminal emulator.
- [ ] #5 Automated CLI and Debian package tests cover the required option semantics and invocation through `/usr/bin/x-terminal-emulator` in a clean environment.
- [ ] #6 The manual page and Debian build, installation, verification, and removal instructions document the supported options and alternative registration.
<!-- AC:END -->
