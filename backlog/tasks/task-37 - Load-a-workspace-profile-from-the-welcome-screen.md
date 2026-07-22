---
id: TASK-37
title: Load a workspace profile from the welcome screen
status: next
assignee: []
created_date: '2026-07-22 21:27'
updated_date: '2026-07-22 21:29'
labels:
  - feature
  - 'area:workspace'
  - 'area:ui'
  - 'area:config'
dependencies: []
priority: medium
ordinal: 500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When Tree Style Terminal starts without --profile and has no open session, add a Load profile button directly below the existing New Terminal button. The button opens a YAML file chooser and loads the selected workspace through the existing profile validation and session-creation path. The chooser starts in the user home directory by default, or in an optional profile directory configured in config.yaml. Keep this as a direct file-loading action rather than adding a profile manager.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The empty welcome screen shows a Load profile button directly below New Terminal, without changing the existing New Terminal behavior.
- [ ] #2 The file chooser is limited to YAML profile files while still allowing the user to navigate to another directory.
- [ ] #3 The optional config key workspace_profiles.default_directory accepts a user path with tilde expansion; when it is unset, empty, missing, or not a usable directory, the chooser starts in the user home directory.
- [ ] #4 Confirming a valid file uses the same parser, validation, multi-root creation, and selected-session behavior as the existing --profile startup path.
- [ ] #5 Cancelling the chooser leaves the application on the unchanged welcome screen with no session created.
- [ ] #6 Unreadable or invalid profiles show a clear error and leave the welcome screen usable without partially created profile sessions.
- [ ] #7 Automated coverage verifies button placement and activation, configured and fallback start directories, successful loading, cancellation, and error handling.
<!-- AC:END -->













## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 The new configuration key and welcome-screen loading flow are documented in CONFIG.md and README.md.
- [ ] #2 Ruff and the relevant unit and GTK integration tests pass.
<!-- DOD:END -->
