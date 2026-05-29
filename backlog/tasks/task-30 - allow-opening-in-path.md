---
id: TASK-30
title: Allow opening in a requested path
status: next
assignee: []
created_date: '2026-05-29 12:39'
updated_date: '2026-05-29 13:32'
labels:
  - feature
  - 'area:startup'
  - 'effort:small'
dependencies: []
references:
  - 'https://www.debian.org/doc/debian-policy/ch-customized-programs.html#packages-providing-a-terminal-emulator'
  - 'https://manpages.debian.org/trixie/gnome-terminal/x-terminal-emulator.1.en.html'
  - 'https://www.mankier.com/1/gnome-terminal'
  - 'https://man.archlinux.org/man/xfce4-terminal.1.en'
  - 'https://docs.kde.org/trunk_kf6/de/konsole/konsole/command-line-options.html'
priority: high
ordinal: 500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow Tree Style Terminal to be used as the terminal opened by file managers and desktop integrations for a specific directory. A common integration is a file manager action such as "Open Terminal Here"; for example, pcmanfm appears to call `x-terminal-emulator %s`, where `%s` is the current directory path.

Problem:
Tree Style Terminal currently starts without a running terminal session. The user has to create the first session manually, and that first root session uses `$HOME` when no `cwd` is passed to `SessionManager.new_session()`. TST also does not expose a command-line option or positional directory argument for "open terminal here" use cases. That makes it awkward to call directly from a file manager action or to register behind `/usr/bin/x-terminal-emulator` for integrations that pass the selected/current directory.

Current behavior to preserve:
- Starting `tree-style-terminal` without a path opens the normal application window without creating an initial terminal session.
- Creating the first session manually without an explicit `cwd` continues to start in `$HOME`.
- Child and sibling sessions continue to use the existing session cwd inheritance behavior.

Expected behavior:
- `tree-style-terminal /some/path` opens the application and creates the first root terminal session in `/some/path` when the argument is an existing directory.
- `tree-style-terminal --working-directory /some/path` does the same explicitly. Also accept `--working-directory=/some/path`.
- `tree-style-terminal --workdir /some/path` is accepted as a small compatibility alias because Konsole and several newer terminal tools use this spelling.
- A relative path is resolved from the caller's current working directory.
- Invalid or non-directory paths fail clearly without opening a misleading terminal in an unrelated directory.
- Existing no-argument startup behavior is unchanged: no automatic session is created.

Compatibility notes:
- The Debian terminal alternative chain may look like:
```
/usr/bin/x-terminal-emulator -> /etc/alternatives/x-terminal-emulator -> /usr/bin/xfce4-terminal.wrapper
```
- Debian Policy for `x-terminal-emulator` standardizes `-e command` and `-T title`; it does not standardize an "open in directory" option.
- Common terminal emulators still provide explicit working-directory options: GNOME Terminal uses `--working-directory`, xfce4-terminal uses `--working-directory` and `--default-working-directory`, and Konsole uses `--workdir`.
- Keep the implementation focused on the path-opening use case needed by file managers. This task is not about full xterm/xfce4-terminal CLI compatibility, command execution, tabs/windows CLI grammar, or becoming a complete Debian `x-terminal-emulator` provider.
- Positional directory support is included specifically for file-manager commands like `x-terminal-emulator %s`.

Implementation guidance:
- Parse startup arguments in one place near the application entry point.
- Pass the resolved working directory into the initial session creation path rather than changing the process cwd globally.
- Store the requested initial cwd on the app/window and create exactly one root session from it during activation. Do not create an initial session when no cwd was requested.
- Add focused tests for argument parsing/path validation where feasible.
- Add focused tests for activation/session creation behavior where feasible: no path still creates no session; requested path creates one root session in that path.
- Do not add workspace templates, saved sessions, file-manager integration UI, tabs/windows command-line grammar, or command execution support in this task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Running `tree-style-terminal` without a path still opens TST without an automatic terminal session.
- [ ] #2 Creating the first session manually after a no-path startup still starts that session in `$HOME`.
- [ ] #3 Running `tree-style-terminal /tmp` opens TST and creates exactly one root terminal session with `/tmp` as its working directory.
- [ ] #4 Running `tree-style-terminal --working-directory /tmp` and `tree-style-terminal --working-directory=/tmp` opens exactly one root terminal session with `/tmp` as its working directory.
- [ ] #5 Running `tree-style-terminal --workdir /tmp` opens exactly one root terminal session with `/tmp` as its working directory.
- [ ] #6 Relative directory arguments are resolved relative to the caller's current working directory.
- [ ] #7 Invalid paths and regular files are reported clearly and do not silently fall back to `$HOME` or another unrelated working directory.
- [ ] #8 The path-opening behavior works when invoked through a desktop/file-manager command equivalent to `x-terminal-emulator %s`.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Argument parsing and path validation have focused automated tests where practical.
- [ ] #2 Manual verification covers direct CLI invocation and at least one file-manager or `x-terminal-emulator` style invocation.
- [ ] #3 Automated or documented manual coverage verifies that no-argument startup still creates no initial session.
- [ ] #4 The implementation does not change cwd globally for the whole application.
- [ ] #5 No unrelated terminal profile, workspace, session persistence, tabs/windows CLI grammar, or command-execution feature is added.
<!-- DOD:END -->
