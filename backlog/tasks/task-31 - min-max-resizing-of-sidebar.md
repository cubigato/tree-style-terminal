---
id: TASK-31
title: min/max resizing of sidebar
status: Done
assignee: []
created_date: '2026-05-29 23:00'
updated_date: '2026-06-01 12:55'
labels:
  - feature
  - 'area:sidebar'
  - 'effort:small'
dependencies: []
priority: high
ordinal: 35500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make sidebar resizing behave well across normal laptop displays and very large monitors. The current sidebar minimum, maximum, and default widths appear to be fixed pixel values, which makes the default and maximum feel too narrow on large 4K windows.

Problem:
The session tree sidebar needs hard bounds so it cannot become unusably tiny or consume the whole window, but fixed pixel-only limits do not scale with available window width. On large displays, users should be able to make the sidebar wider enough for nested session titles and paths without changing code or configuration.

Expected behavior:
- The sidebar still has a sensible minimum width so the tree remains usable.
- The sidebar has a larger maximum width on wide windows than it does today.
- The default width scales better on large windows while staying reasonable on small and medium windows.
- Resizing should be based on the current window width where that is practical, with pixel clamps for lower and upper safety limits.
- User-driven resizing remains simple: dragging the sidebar divider should feel the same, only with better bounds.

Implementation guidance:
Keep the implementation local to the existing sidebar/paned layout code. Prefer a small helper that derives min/default/max sidebar widths from the current window or paned allocation, for example percentage-based values clamped to sensible pixel limits. Avoid adding preferences, presets, or new UI for this task unless implementation discovers an existing setting that already owns sidebar width.

The exact numbers can be tuned during implementation, but the behavior should be easy to reason about: small windows should not lose too much terminal space, and large 4K windows should allow a substantially wider sidebar than the current fixed maximum.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Sidebar minimum width prevents the session tree from becoming unusably narrow.
- [ ] #2 Sidebar maximum width scales up on wide windows and allows a noticeably wider sidebar on 4K-sized windows than the current fixed limit.
- [ ] #3 Default sidebar width is reasonable on small/medium windows and wider on large windows.
- [ ] #4 Dragging the sidebar divider respects the computed min/max bounds after window resize.
- [ ] #5 The change does not add new settings or visible UI controls.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Focused tests or a small layout helper test cover the computed min/default/max width behavior for small, medium, and large window widths where practical.
- [ ] #2 Manual verification covers resizing the sidebar on a normal-sized window and a 4K-sized or emulated large window.
- [ ] #3 Implementation stays scoped to the existing sidebar/paned layout code and does not introduce unrelated sidebar behavior changes.
<!-- DOD:END -->
