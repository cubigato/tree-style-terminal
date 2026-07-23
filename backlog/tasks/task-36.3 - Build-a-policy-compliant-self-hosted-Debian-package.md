---
id: TASK-36.3
title: Build a policy-compliant self-hosted Debian package
status: next
assignee: []
created_date: '2026-07-23 13:16'
labels:
  - packaging
  - debian
  - release
  - 'blocker:1.0'
dependencies:
  - TASK-36.1
  - TASK-36.2
references:
  - 'https://www.debian.org/doc/debian-policy/'
  - 'https://www.debian.org/doc/packaging-manuals/python-policy/'
  - 'https://manpages.debian.org/bookworm/dh-python/pybuild.1.en.html'
modified_files:
  - debian/control
  - debian/rules
  - debian/changelog
  - debian/copyright
  - debian/source/format
  - debian/watch
  - README.md
parent_task_id: TASK-36
priority: high
ordinal: 2300
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provide a native Debian package that regular users can install without a Python development environment and that can later be taken through Debian's official sponsorship process without replacing the packaging approach. Use Debian's Python and GTK/VTE packages rather than vendoring native runtime components, and keep user configuration outside package ownership.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A non-native Debian source package and Architecture: all binary package build from a clean checkout using current Debian Python packaging helpers.
- [ ] #2 The binary package declares Python, PyGObject, PyYAML, GTK3, and VTE runtime dependencies using Debian package names and does not download dependencies during the build.
- [ ] #3 Installing with apt provides the documented command, application menu entry, icon, MetaInfo, license, and all runtime resources; uninstall and upgrade behavior preserves user configuration.
- [ ] #4 The package passes a clean build, Lintian, install/uninstall checks, and an application launch smoke test on the declared Debian support baseline.
- [ ] #5 Debian build, verification, local installation, versioning, and self-publication instructions are documented, including why the package does not yet provide x-terminal-emulator.
<!-- AC:END -->
