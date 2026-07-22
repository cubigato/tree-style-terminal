---
id: TASK-25
title: Add AI-assisted shell command drafting
status: next
assignee: []
created_date: '2026-05-26 22:11'
updated_date: '2026-07-22 21:23'
labels:
  - feature
  - ai
  - 'area:integration'
dependencies: []
references:
  - 'https://docs.warp.dev/features/windows'
priority: medium
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add an opt-in command-drafting feature backed by a configured OpenAI-compatible API. The user may type a natural-language description on the current prompt and invoke a keyboard shortcut. The application sends a bounded portion of the current shell history plus that editable input in a purpose-built prompt, then replaces the entire current input line with the returned command. It must not submit the command or synthesize Enter, so the user can review and edit it first.
<!-- SECTION:DESCRIPTION:END -->








## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 User-facing configuration and privacy implications are documented in CONFIG.md and README.md.
- [ ] #2 Ruff and the relevant automated tests pass.
<!-- DOD:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The YAML config supports an OpenAI-compatible endpoint, API key, required model identifier, and a configurable non-conflicting shortcut; the feature remains inactive until the required API settings are supplied.
- [ ] #2 Invoking the shortcut captures a bounded recent shell history and the full current editable line, keeping the user intent distinct when constructing a concise prompt that requests a shell command.
- [ ] #3 A successful response replaces the full current editable line with the proposed command and never submits it; the user must explicitly press Enter.
- [ ] #4 The network request does not freeze the GTK UI, and errors or invalid responses leave the existing input unchanged while presenting a useful non-disruptive error.
- [ ] #5 API credentials and transmitted shell content are never written to application logs, and no request is made while the feature is unconfigured.
- [ ] #6 Configuration, prompt construction, response handling, line replacement, no-submit behavior, and failure paths have automated coverage.
<!-- AC:END -->
