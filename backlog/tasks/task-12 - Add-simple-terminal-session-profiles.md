---
id: TASK-12
title: Add simple terminal session profiles
status: To Do
assignee: []
created_date: '2026-05-26 22:09'
updated_date: '2026-05-27 22:25'
labels:
  - feature
  - 'effort:medium'
  - 'area:config'
dependencies: []
references:
  - 'https://learn.microsoft.com/en-us/windows/terminal/'
  - 'https://help.gnome.org/gnome-terminal/'
priority: medium
ordinal: 130
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Introduce a small profile/preset layer for new sessions: display name, shell command, start directory, and optional theme/font overrides if they fit existing config patterns. Avoid a large profile manager in the first pass.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Profiles can be defined in the YAML config
- [ ] #2 User can create a new session from a selected profile
- [ ] #3 Invalid profile config is reported with a clear error
<!-- AC:END -->
