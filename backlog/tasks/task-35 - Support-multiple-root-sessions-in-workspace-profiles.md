---
id: TASK-35
title: Support multiple root sessions in workspace profiles
status: In Progress
assignee: []
created_date: '2026-07-22 12:33'
updated_date: '2026-07-22 12:37'
labels:
  - feature
  - 'effort:medium'
  - 'area:workspace'
  - 'area:config'
  - 'area:session'
dependencies:
  - TASK-14
references:
  - CONFIG.md
modified_files:
  - CONFIG.md
  - README.md
  - src/tree_style_terminal/config/workspace_profile.py
  - src/tree_style_terminal/main.py
  - tests/unit/test_workspace_profile.py
  - tests/unit/test_startup_arguments.py
priority: medium
ordinal: 490
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend the version 1 workspace profile format and loader from TASK-14 so one profile can describe multiple independent root session trees.

Keep existing single-root profiles valid. A profile may contain either the existing `root` mapping or a new top-level `roots` list of node mappings, but not both. `roots` must contain at least one node. All existing node fields, recursive children, workdir inheritance, validation, and command semantics apply independently to every root.

Startup through `--profile` / `-p` creates every declared root tree. This enables TASK-6 to export all live root sessions into one reusable profile without synthetic wrapper sessions or runtime session IDs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Existing version 1 profiles with one top-level `root` continue to load and start unchanged.
- [x] #2 A profile may use a non-empty top-level `roots` list whose entries use the existing recursive workspace node schema.
- [x] #3 Exactly one of `root` or `roots` must be present; missing both, specifying both, an empty list, or non-mapping list entries produce useful YAML-path validation errors.
- [x] #4 Top-level workdir inheritance and all existing title, workdir, command, and children semantics apply to every root.
- [x] #5 Startup through `--profile` / `-p` creates every root tree without adding a synthetic parent session.
- [x] #6 Focused tests cover legacy single-root compatibility, multiple roots, inherited workdirs, startup creation, and invalid root combinations.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extend the validated profile model to represent one or more roots while preserving compatibility with existing `root` profiles.
2. Parse and validate mutually exclusive `root` and `roots` top-level forms with useful YAML-path errors.
3. Update startup creation to create every root tree.
4. Document the multi-root form and add loader and startup tests for single-root compatibility, multiple roots, and invalid combinations.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented backward-compatible multi-root workspace profiles. `WorkspaceProfile.roots` is the canonical root list and `WorkspaceProfile.root` remains as a compatibility accessor for the first root. The loader accepts exactly one of `root` or non-empty `roots`, applies existing recursive parsing and workdir inheritance to each root, and reports YAML-path errors for invalid lists and entries. Startup now creates each root tree once. README and CONFIG.md document the new form. Verification: 277 pytest tests passed; Ruff passed for src and tests.
<!-- SECTION:NOTES:END -->
