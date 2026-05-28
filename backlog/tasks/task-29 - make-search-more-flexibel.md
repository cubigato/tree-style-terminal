---
id: TASK-29
title: Make terminal search more flexible
status: next
assignee: []
created_date: '2026-05-28 11:41'
updated_date: '2026-05-28 11:48'
labels:
  - feature
  - 'area:terminal'
  - 'effort:small'
dependencies: []
priority: medium
ordinal: 9500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Improve the active-terminal search so the default mode is forgiving enough for common terminal text differences while still staying predictable. The existing exact search behavior should remain available through a fuzzy/exact toggle in the search UI.

Problem:
The current terminal search only finds exact, case-sensitive matches. This makes command lookup brittle when users do not remember exact capitalization, spacing, or separator spelling from scrollback.

Expected behavior:
- Search defaults to fuzzy mode when the search UI opens.
- Fuzzy mode is case-insensitive.
- Fuzzy mode tolerates small separator differences that are common in command text, such as `my-command` matching `mycommand`, and `command --flag` matching `command -flag`.
- Fuzzy mode should not become broad approximate matching: typos, reordered words, and unrelated substrings should not match just because they are similar.
- Users can turn fuzzy mode off to use exact matching.
- The fuzzy/exact setting is obvious in the existing search UI and does not add a separate advanced-search workflow.

Implementation guidance:
Keep search VTE-native. Build a conservative PCRE2 search pattern from the user's query and pass it through `Vte.Regex.new_for_search()` and `Vte.Terminal.search_set_regex()`, then continue using `search_find_next()` and `search_find_previous()` for navigation. For fuzzy mode, prefer query-to-regex expansion: case-insensitive matching plus a small documented separator class for command text, for example spaces, hyphens, and underscores. Do not extract/index the scrollback or implement edit-distance matching unless VTE regex search proves insufficient during implementation.

API notes checked before implementation:
- VTE exposes native regex search through `search_set_regex()` and native navigation through `search_find_next()` / `search_find_previous()`.
- `Vte.Regex.new_for_search()` accepts PCRE2-style search patterns; local introspection confirmed it compiles case-insensitive separator-tolerant patterns such as `(?i)my[-_[:space:]]*command` and `(?i)command[-_[:space:]]*flag`.
- `get_text_range_format()` exists, but using it for this feature would be a fallback path and is not the preferred design.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Opening terminal search defaults to fuzzy mode.
- [ ] #2 Fuzzy search is case-insensitive.
- [ ] #3 In fuzzy mode, searching for `my-command` matches scrollback text containing `mycommand`, and searching for `command --flag` matches `command -flag`.
- [ ] #4 Fuzzy search does not match clearly different terms such as reordered words or unrelated typo-only matches.
- [ ] #5 The user can switch fuzzy mode off and get the existing exact matching behavior.
- [ ] #6 Next/previous search navigation continues to work in both fuzzy and exact modes.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Focused tests cover fuzzy normalization and exact-mode fallback behavior.
- [ ] #2 Manual verification covers case-insensitive search, separator-tolerant search, exact mode, and next/previous navigation in a running terminal.
- [ ] #3 Search remains implemented through VTE regex search/navigation; no custom scrollback extraction, indexing, regex UI, or broad approximate matching is added.
<!-- DOD:END -->
