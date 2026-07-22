---
id: TASK-36
title: Ship end-user Linux packages for 1.0
status: next
assignee: []
created_date: '2026-07-22 21:21'
updated_date: '2026-07-22 21:23'
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
Make Tree Style Terminal installable by regular Linux users without cloning the repository or setting up a Python development environment. Establish release-ready packaging for the existing documented targets, Debian packages and Flatpak, including the native GTK3 and VTE runtime dependencies, desktop integration, reproducible build instructions, and installable release artifacts. This task blocks the 1.0 release.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Debian package and Flatpak definitions build installable artifacts from a clean checkout with all required application resources included.
- [ ] #2 A user can install and launch the application from both the desktop application menu and the documented command line without cloning the repository or installing development tooling.
- [ ] #3 The packages declare or bundle the required Python, GTK3, PyGObject, and VTE runtime dependencies appropriately for their format.
- [ ] #4 Version, application ID, icon, desktop entry, license, and AppStream or equivalent store metadata are consistent and release-ready.
- [ ] #5 Installing and uninstalling either format does not overwrite user configuration, and upgrading preserves existing configuration.
- [ ] #6 The release workflow produces versioned artifacts for tagged releases and documents how they are published and verified.
- [ ] #7 Supported clean Linux environments have smoke coverage that installs the artifact, starts Tree Style Terminal, opens a shell session, and exits successfully.
<!-- AC:END -->













## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Packaging metadata, build instructions, installation instructions, and release steps are documented.
- [ ] #2 Package builds and clean-environment launch smoke tests pass for every supported format.
<!-- DOD:END -->
