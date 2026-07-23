---
id: TASK-36
title: Ship end-user Linux packages for 1.0
status: next
assignee: []
created_date: '2026-07-22 21:21'
updated_date: '2026-07-23 13:40'
labels:
  - packaging
  - release
  - 'blocker:1.0'
dependencies: []
priority: high
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make Tree Style Terminal installable by regular Linux users without cloning the repository or setting up a Python development environment. Establish release-ready Debian and AppImage packaging for 1.0, including the native GTK3 and VTE runtime dependencies, desktop integration, reproducible build instructions, and installable release artifacts. Flatpak remains an optional post-1.0 distribution experiment and does not block this task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Debian package and AppImage definitions build installable or directly runnable artifacts from a clean checkout with all required application resources included.
- [ ] #2 A user can install or download and launch the application through the documented desktop and command-line paths without cloning the repository or installing development tooling.
- [ ] #3 The Debian package declares and the AppImage bundles the required Python, GTK3, PyGObject, and VTE runtime dependencies appropriately for each format.
- [ ] #4 Version, application ID, icon, desktop entry, license, and AppStream metadata are consistent and release-ready across the 1.0 artifacts.
- [ ] #5 Installing, upgrading, replacing, or removing either 1.0 format does not overwrite user configuration, and upgrades preserve existing configuration.
- [ ] #6 The release workflow produces versioned Debian and AppImage artifacts for protected version tags and documents how they are published and verified.
- [ ] #7 Supported clean Linux environments have smoke coverage that installs or runs each 1.0 artifact, starts Tree Style Terminal, opens a real host shell session, and exits successfully.
<!-- AC:END -->



## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Packaging metadata, build instructions, installation instructions, and release steps are documented.
- [ ] #2 Package builds and clean-environment launch smoke tests pass for every supported format.
<!-- DOD:END -->
