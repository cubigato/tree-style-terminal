---
id: TASK-36.6
title: Automate tagged package releases in internal GitLab CI
status: next
assignee: []
created_date: '2026-07-23 13:17'
updated_date: '2026-07-23 13:40'
labels:
  - ci
  - packaging
  - release
  - gitlab
  - 'blocker:1.0'
dependencies:
  - TASK-36.3
  - TASK-36.11
references:
  - 'https://docs.gitlab.com/ci/'
  - 'https://docs.gitlab.com/runner/executors/docker/'
modified_files:
  - .gitlab-ci.yml
  - README.md
parent_task_id: TASK-36
priority: high
ordinal: 2600
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend the existing skeleton pipeline into a reproducible release workflow on cubigato's self-hosted GitLab Docker runner. Build and verify Debian and AppImage artifacts from protected version tags while keeping publishing controlled until the pipeline is deliberately enabled for production.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The GitLab pipeline uses pinned build environments on the Docker runner to lint, test, build, and validate the Debian and AppImage artifacts from a clean checkout.
- [ ] #2 Protected version tags are the only automatic release trigger, and produced filenames, embedded versions, release notes, and checksums agree with the tag.
- [ ] #3 Debian install/launch smoke coverage runs in a disposable environment; AppImage smoke coverage runs in extract-and-run mode in Docker and the documented supported-system matrix includes an actual FUSE, desktop, host-shell, X11, and Wayland launch check where required.
- [ ] #4 Successful release jobs retain versioned source, Debian, AppImage, checksum, verification, and bundled-component/license artifacts and can attach them to a GitLab release without rebuilding unverified source.
- [ ] #5 Secrets and publishing credentials are protected, publishing remains manual or disabled until explicitly activated, failures cannot create a partial public release, and runner/bootstrap/recovery procedures are documented.
<!-- AC:END -->
