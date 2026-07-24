---
id: TASK-36
title: Ship end-user Linux packages for 1.0
status: next
assignee: []
created_date: '2026-07-22 21:21'
updated_date: '2026-07-23 23:47'
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
Make Tree Style Terminal installable by regular Linux users without cloning the repository or setting up a Python development environment. The 1.0 release scope is a release-ready Debian package and AppImage, including native GTK3/VTE handling, shared desktop integration, reproducible build instructions, clean host-shell behavior, and a documented manual publication path under cubigato's control. CI automation, PyPI, official Debian inclusion, and Flatpak remain independent post-1.0 follow-ups and do not block completion of this task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Debian package and AppImage definitions build installable or directly runnable artifacts from a clean checkout with all required application resources included.
- [ ] #2 A user can install or download and launch the application through the documented desktop and command-line paths without cloning the repository or installing development tooling.
- [ ] #3 The Debian package declares and the AppImage bundles the required Python, GTK3, PyGObject, and VTE runtime dependencies appropriately for each format.
- [ ] #4 Version, application ID, icon, desktop entry, license, and AppStream metadata are consistent and release-ready across the 1.0 artifacts.
- [ ] #5 Installing, upgrading, replacing, or removing either 1.0 format does not overwrite user configuration, and upgrades preserve existing configuration.
- [ ] #6 A documented manual release workflow produces versioned Debian and AppImage artifacts plus the checksums and license information needed for direct publication without requiring GitLab CI or an application catalog.
- [ ] #7 Supported clean Linux environments have smoke coverage that installs or runs each 1.0 artifact, starts Tree Style Terminal, opens a real host shell session, and exits successfully.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Complete shared release identity/configuration and the self-hosted Debian package (TASK-36.1 through TASK-36.3; done).
2. Build and validate the production-ready AppImage, including clean host-shell behavior and manual publication artifacts (TASK-36.11; current).
3. After Debian and AppImage are accepted, close the 1.0 packaging parent. Debian integration, GitLab CI/PyPI automation, and Flatpak remain ordered non-blocking follow-ups.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-07-24 scope clarification: TASK-36.1, TASK-36.2, TASK-36.3, and TASK-36.11 form the complete 1.0 packaging path. The remaining subtasks are useful follow-ups but do not block the parent task or the 1.0 release.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Packaging metadata, build instructions, installation instructions, and release steps are documented.
- [ ] #2 Package builds and clean-environment launch smoke tests pass for every supported format.
<!-- DOD:END -->
