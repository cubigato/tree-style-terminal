---
id: TASK-12
title: Add simple startup profile session nodes
status: Done
assignee: []
created_date: '2026-05-26 22:09'
updated_date: '2026-06-08 08:53'
labels:
  - feature
  - 'effort:medium'
  - 'area:config'
dependencies: []
references:
  - 'https://learn.microsoft.com/en-us/windows/terminal/'
  - 'https://help.gnome.org/gnome-terminal/'
modified_files:
  - README.md
  - CHANGELOG.md
  - pyproject.toml
  - src/tree_style_terminal/__init__.py
  - examples/workspace-profiles/simple.yml
  - examples/workspace-profiles/linux-overview.yml
  - src/tree_style_terminal/controllers/session_manager.py
  - src/tree_style_terminal/main.py
  - tests/unit/test_session_actions.py
  - tests/unit/test_startup_arguments.py
  - tests/test_basic.py
priority: medium
ordinal: 750
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add the first-pass runtime support for creating terminal sessions from the self-contained YAML workspace profile format defined in TASK-14. This task is not a profile manager and does not add profile definitions to the normal `config.yaml`; it focuses on turning validated profile nodes into real sessions.

Each profile node may provide `title`, resolved `workdir`, optional `command`, and children. When `command` is omitted, create the session exactly like the current new-session path: spawn the user's normal interactive shell in the resolved workdir. When `command` is provided, start it through the user's normal shell in that workdir so shell semantics, Ctrl+C, and follow-up interactive use behave predictably. Keep the implementation small and aligned with the current VTE session creation flow.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A validated profile node can create a terminal session with the configured title and resolved workdir.
- [x] #2 A profile node without `command` starts the same normal interactive shell used by existing new-session behavior.
- [x] #3 A profile node with `command` starts that command through the user's normal shell in the resolved workdir, preserving familiar Ctrl+C and shell behavior.
- [x] #4 Invalid runtime profile data is reported with a clear error instead of silently creating a fallback session in the wrong directory.
- [x] #5 The implementation remains a simple startup/profile-node path and does not add a full profile manager or profile entries to `config.yaml`.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Extended SessionManager with workspace tree creation from validated profile nodes. Nodes without command use the existing spawn_shell(cwd=...) path. Nodes with command spawn the user's SHELL with -c and exec back into the shell after the command. Startup activation now creates a workspace tree when a parsed profile is supplied.

Added README usage docs and harmless example profile files that demonstrate shell-only and command sessions.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented startup profile node session creation from validated workspace YAML data. Nodes without command use the existing interactive shell path; nodes with command run through the user's shell and return to an interactive shell afterward. Bumped version metadata to 0.5.0 and added changelog coverage.
<!-- SECTION:FINAL_SUMMARY:END -->
