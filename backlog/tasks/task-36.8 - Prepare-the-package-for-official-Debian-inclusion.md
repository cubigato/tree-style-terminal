---
id: TASK-36.8
title: Prepare the package for official Debian inclusion
status: next
assignee: []
created_date: '2026-07-23 13:17'
labels:
  - packaging
  - debian
  - distribution
dependencies:
  - TASK-36.3
references:
  - 'https://www.debian.org/devel/wnpp/'
  - 'https://mentors.debian.net/intro-maintainers/'
  - 'https://www.debian.org/doc/manuals/developers-reference/ch05.en.html'
parent_task_id: TASK-36
priority: medium
ordinal: 2800
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Take the proven self-hosted Debian packaging to submission quality so cubigato can pursue inclusion in Debian without redesigning the package. Keep this as a downstream distribution follow-up rather than a prerequisite for publishing the 1.0 self-hosted artifact, since Debian review and sponsorship are externally scheduled.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Debian package, WNPP, and namespace searches are repeated immediately before submission and no conflicting package or active packaging effort is found.
- [ ] #2 The source package is maintained in a public Debian-oriented repository with complete policy metadata, clean source and binary builds, and no unexplained Lintian or reproducibility issues.
- [ ] #3 An Intent To Package report and package-maintainer identity are prepared with the correct upstream URL, license, description, and package scope; external submission occurs only with explicit human approval.
- [ ] #4 A mentors.debian.net upload and Request For Sponsorship are prepared from the exact reviewed source package, with a documented process for responding to sponsor review.
- [ ] #5 The handoff explains unstable/testing migration, future stable or backports availability, ongoing Debian maintenance obligations, and which self-hosted release channel remains available meanwhile.
<!-- AC:END -->
