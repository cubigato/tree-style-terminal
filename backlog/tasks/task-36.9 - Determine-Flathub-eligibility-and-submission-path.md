---
id: TASK-36.9
title: Determine Flathub eligibility and submission path
status: Done
assignee: []
created_date: '2026-07-23 13:18'
updated_date: '2026-07-23 13:40'
labels:
  - flatpak
  - flathub
  - distribution
  - policy
dependencies:
  - TASK-36.5
references:
  - 'https://docs.flathub.org/docs/for-app-authors/requirements'
  - 'https://docs.flathub.org/docs/for-app-authors/submission'
  - 'https://github.com/flathub/com.raggesilver.BlackBox'
parent_task_id: TASK-36
priority: low
ordinal: 2900
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Document the Flathub eligibility decision based on the rules current on 2026-07-23 and the project's actual code provenance. Tree Style Terminal is not planned for Flathub while the published generative-AI policy excludes applications containing AI-generated or AI-assisted code, documentation, or other content.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The Flathub generative-AI requirements and submission guidance current on 2026-07-23 are reviewed and linked.
- [x] #2 The project records that its product direction and ticket steering are human-led but its application code is almost entirely AI-generated or AI-assisted.
- [x] #3 A human-approved no-go decision records that no Flathub submission or exception request is planned under the current rules.
- [x] #4 Self-hosted Flatpak work remains an optional low-priority task and is explicitly not part of the 1.0 blocking release path.
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
created: 2026-07-23 13:40
---
Decision recorded 2026-07-23: Flathub's published policy disallows applications containing AI-generated or AI-assisted code, documentation, or other content. Human ideas, ticket steering, review, and acceptance do not change the provenance of code that is almost entirely AI-written. Although the policy mentions possible exceptions for mature, well-maintained projects, Tree Style Terminal is a beta project approaching 1.0, so an exception is not a dependable or appropriate release plan. No Flathub submission will be prepared. This does not prohibit building or self-hosting Flatpak itself.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Reviewed the current Flathub requirements against the project's disclosed provenance and recorded a human-approved no-go decision. The application is almost entirely AI-generated or AI-assisted, so it does not satisfy Flathub's current generative-AI policy. No submission or exception request is planned; optional self-hosted Flatpak work remains separate, low priority, and non-blocking for 1.0.
<!-- SECTION:FINAL_SUMMARY:END -->
