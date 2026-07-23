---
id: TASK-36.5
title: Build and self-publish the Flatpak artifact
status: next
assignee: []
created_date: '2026-07-23 13:16'
updated_date: '2026-07-23 13:40'
labels:
  - packaging
  - flatpak
  - release
dependencies:
  - TASK-36.1
  - TASK-36.2
  - TASK-36.4
references:
  - 'https://docs.flatpak.org/en/latest/building.html'
  - 'https://docs.flatpak.org/en/latest/python.html'
  - 'https://docs.flatpak.org/en/latest/sandbox-permissions.html'
modified_files:
  - packaging/flatpak/de.cubigato.TreeStyleTerminal.yml
  - packaging/flatpak/python3-requirements.json
  - README.md
parent_task_id: TASK-36
priority: low
ordinal: 3100
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Optionally provide a self-hosted Flatpak after the 1.0 Debian and AppImage release path is complete. The artifact would remain under cubigato's control and would document the broad host access required by a terminal emulator. This work is explicitly non-blocking for 1.0 and does not imply a Flathub submission.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A pinned Flatpak manifest builds the application and all non-runtime dependencies from source without network access during the build.
- [ ] #2 The artifact uses de.cubigato.TreeStyleTerminal consistently, includes shared desktop assets and license files, and launches from the desktop menu and documented flatpak run command.
- [ ] #3 The manifest requests only permissions required for the supported terminal, profile, display, and optional network behavior; host-shell access and its security implications are documented.
- [ ] #4 Installation, upgrade, normal uninstall, and explicit data deletion behave predictably and preserve configuration according to Flatpak conventions.
- [ ] #5 A clean build passes Flatpak and AppStream validation, installs into a clean user environment, starts a verified host shell session, and can be exported as a versioned bundle or signed self-hosted repository artifact.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-07-23: Flatpak remains as an optional self-hosted follow-up with low priority. It is no longer a 1.0 artifact or a dependency of the release pipeline.
<!-- SECTION:NOTES:END -->
