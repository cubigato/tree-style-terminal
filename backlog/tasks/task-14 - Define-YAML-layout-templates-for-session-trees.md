---
id: TASK-14
title: Define YAML layout templates for session trees
status: Done
assignee: []
created_date: '2026-05-26 22:10'
updated_date: '2026-06-08 08:53'
labels:
  - feature
  - 'effort:medium'
  - 'area:workspace'
  - 'area:config'
dependencies: []
references:
  - 'https://zellij.dev/features/'
modified_files:
  - CONFIG.md
  - README.md
  - CHANGELOG.md
  - pyproject.toml
  - src/tree_style_terminal/__init__.py
  - examples/workspace-profiles/simple.yml
  - examples/workspace-profiles/linux-overview.yml
  - src/tree_style_terminal/config/workspace_profile.py
  - src/tree_style_terminal/main.py
  - tests/unit/test_workspace_profile.py
  - tests/unit/test_startup_arguments.py
  - tests/test_basic.py
priority: medium
ordinal: 500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Define a documented self-contained YAML file format for reusable Tree Style Terminal workspace profiles. A profile file such as `my-java-project.yml` is loaded explicitly at startup, for example with `tst --profile my-java-project.yml` / `tst -p my-java-project.yml`, and describes one session tree.

Use format version `1`. The preferred structure is:

```yaml
version: 1
name: "My Java Project"
workdir: "~/dev/my-java-project"

root:
  title: "project"
  children:
    - title: "server"
      command: "./gradlew bootRun"
    - title: "tests"
      command: "./gradlew test"
    - title: "logs"
      workdir: "build/logs"
```

Top-level `workdir` is optional and acts as the inherited base directory. Each node may define `title`, `workdir`, optional `command`, and optional nested `children`. Relative node `workdir` values resolve against the inherited workdir; `~` is expanded. If no workdir is specified anywhere, startup should use the current process directory. If `command` is omitted, the node starts a normal interactive shell exactly like current new-session behavior. If `command` is present, it must be started through the user's normal shell rather than exec-style argv replacement, so Ctrl+C and shell behavior remain familiar.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 YAML profile schema is documented in CONFIG.md or a linked project doc, including `version`, optional top-level `name`, optional inherited `workdir`, required `root`, node `title`, node `workdir`, optional node `command`, and recursive `children`.
- [x] #2 Layout/profile files support nested children and inherited workdir resolution, including `~`, absolute paths, and relative paths against the nearest inherited workdir.
- [x] #3 `command` is explicitly optional; nodes without `command` create the same normal interactive shell used by current new-session behavior.
- [x] #4 Documented command semantics require commands to run through the user's normal shell so Ctrl+C and shell behavior remain familiar.
- [x] #5 Layout validation reports useful YAML-path errors for malformed entries, unknown versions, invalid field types, invalid `children`, and unusable workdirs.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented a self-contained workspace profile YAML loader for version 1 files with required root node, optional top-level name/workdir, inherited workdir resolution, recursive children, and YAML-path validation errors. Added CLI profile path parsing via --profile/-p and documented the schema in CONFIG.md. Profile files remain separate from config.yaml.

Added README usage docs and example workspace profile YAML files under examples/workspace-profiles/.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added version 1 self-contained workspace profile YAML support, documented usage in CONFIG.md and README.md, included harmless example profile files, wired CLI parsing for --profile/-p, bumped the release version to 0.5.0, and recorded the change in CHANGELOG.md.
<!-- SECTION:FINAL_SUMMARY:END -->
