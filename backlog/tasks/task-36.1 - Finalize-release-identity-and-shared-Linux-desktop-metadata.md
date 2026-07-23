---
id: TASK-36.1
title: Finalize release identity and shared Linux desktop metadata
status: Done
assignee:
  - Codex
created_date: '2026-07-23 13:15'
updated_date: '2026-07-23 19:20'
labels:
  - packaging
  - release
  - desktop-integration
  - 'blocker:1.0'
dependencies: []
references:
  - 'https://docs.flathub.org/docs/for-app-authors/requirements'
  - 'https://www.freedesktop.org/software/appstream/docs/chap-Metadata.html'
modified_files:
  - CHANGELOG.md
  - MANIFEST.in
  - PACKAGING.md
  - README.md
  - assets/screenshots/tree-style-terminal.png
  - assets/screenshots/wallpaper-nebula-tree.png
  - data/de.cubigato.treestyleterminal.desktop
  - data/de.cubigato.treestyleterminal.metainfo.xml
  - data/icons/hicolor/512x512/apps/de.cubigato.treestyleterminal.png
  - data/icons/hicolor/scalable/apps/de.cubigato.treestyleterminal.svg
  - pyproject.toml
  - screenshot-dark-transparent.png
  - src/tree_style_terminal/__init__.py
  - src/tree_style_terminal/_metadata.py
  - src/tree_style_terminal/_version.py
  - src/tree_style_terminal/main.py
  - tests/test_basic.py
  - tests/test_release_metadata.py
parent_task_id: TASK-36
priority: high
ordinal: 2100
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Establish one stable, package-independent identity and metadata set for the 1.0 Linux release so Debian, AppImage, PyPI metadata, the application runtime, and desktop software centers all describe the same application. cubigato GmbH controls cubigato.de; use the permanent lowercase reverse-DNS application ID de.cubigato.treestyleterminal. Keep the shared desktop, icon, license, and release metadata upstream so packaging formats consume the same source files.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The runtime application ID, desktop file ID, icon name, and MetaInfo component ID all use de.cubigato.treestyleterminal.
- [x] #2 A release-quality application icon, desktop entry, and AppStream MetaInfo file are included as shared upstream assets and pass their standard validators.
- [x] #3 Project version information has one authoritative source and is consistent across runtime and packaging metadata.
- [x] #4 License, project URLs, release notes, categories, launch command, and screenshots referenced by the metadata are complete and consistent.
- [x] #5 Automated tests cover the permanent application ID and version consistency, and the packaging/release documentation describes how shared metadata is updated.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a temporary, review-only design workspace and generate several distinct application-icon concepts based on a shell prompt containing a tree/branch motif. Keep the permanent icon name `de.cubigato.TreeStyleTerminal`; do not integrate an icon until the user selects a concept.
2. Generate several original wallpaper concepts suitable for a clean release screenshot, avoiding third-party characters, logos, personal data, and recognizable copyrighted artwork. The user will create the final application screenshot separately.
3. After visual selection, create the selected application icon as a clean scalable SVG master plus a large PNG rendition suitable for desktop integration, AppImage, and software-center use; license project visual assets under Apache-2.0 and AppStream metadata under CC0-1.0.
4. Introduce the permanent runtime/application identity `de.cubigato.TreeStyleTerminal` while preserving current NON_UNIQUE/multi-instance behavior. Add a normal Exec-based desktop entry (`Exec=tree-style-terminal`, no D-Bus activation) and keep both `tree-style-terminal` and `tst` console commands declared for PATH installation by package formats.
5. Add shared upstream desktop integration assets under `data/`: the desktop entry, application icon(s), and AppStream MetaInfo. Use the public GitHub repository and issue tracker as project/source/bug URLs, cubigato GmbH as developer, Apache-2.0 as project license, current release 0.8.0, and appropriate terminal/system categories.
6. Establish one authoritative Python/package version source and make runtime and package metadata consume or validate against it. Keep AppStream release metadata synchronized through an explicit documented release step.
7. Replace the published screenshot reference with the user's forthcoming neutral screenshot and use a stable public HTTPS URL. Do not publish or reference the existing screenshot with personal host/user data and unclear wallpaper rights.
8. Add automated checks for the permanent ID, both command entry points, and version/metadata consistency. Validate the desktop entry with `desktop-file-validate`, AppStream metadata with `appstreamcli validate`, SVG/XML syntax as applicable, then run relevant tests and `.venv/bin/python -m ruff check src tests`.
9. Document how maintainers update versions, release notes, shared metadata, icon renditions, and screenshots. Keep Debian/AppImage installation mechanics in their dedicated follow-up tasks.

Approved release-version adjustment (2026-07-23): ship these identity and metadata changes as patch release 0.8.1 rather than describing the current metadata as 0.8.0. Update the authoritative version source, changelog, AppStream release entry, and consistency checks together. No new application feature is implied by this version bump.

Approved identity normalization (2026-07-23): replace `de.cubigato.TreeStyleTerminal` everywhere with the fully lowercase permanent ID `de.cubigato.treestyleterminal`. Rename the desktop, MetaInfo, SVG, and PNG files and update runtime constants, metadata references, tests, and documentation. Re-run all validators; the AppStream uppercase-ID pedantic hint must disappear.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Planning audit (2026-07-23): runtime still uses placeholder `org.example.TreeStyleTerminal`; `pyproject.toml` and `src/tree_style_terminal/__init__.py` duplicate version 0.8.0; no application icon, desktop entry, or AppStream MetaInfo exists. The public GitHub mirror is https://github.com/cubigato/tree-style-terminal and the project already has Apache-2.0 licensing/copyright and a `tree-style-terminal` launch command. The existing screenshot is not suitable as the primary release/AppStream screenshot because it contains personal user/host data and a third-party anime wallpaper whose redistribution rights are unclear. A neutral release screenshot and a release-quality application icon are therefore prerequisites/assets for this task. Local `desktop-file-validate`, `appstreamcli`, and Inkscape are available. Keep NON_UNIQUE/multi-instance behavior unless separately agreed; use a normal Exec-based desktop entry rather than claiming D-Bus activation.

Visual review checkpoint (2026-07-23): generated four raster icon concepts and four original wallpaper concepts with the built-in image generator. Drafts and overview sheets are stored under `design-drafts/task-36.1/`. Icon concepts: A terminal window plus hierarchical tree; B prompt chevron growing into a tree; C compact terminal/session-tree glyph; D tree canopy with session nodes and cursor. Wallpaper concepts: A circuit grove; B nebula tree; C geometric forest; D branching coral. These are review drafts only. After user selection, rebuild the chosen icon as deterministic SVG plus PNG; the user will use a selected wallpaper to capture a new clean application screenshot. Both `tree-style-terminal` and `tst` are already declared in `[project.scripts]`; downstream Debian/AppImage tasks must ensure their installed launchers are on PATH.

Visual selection/update (2026-07-23): user selected Icon A (terminal window plus hierarchical tree) as the final concept. Use that concept as the basis for the deterministic SVG/PNG application icon. Generated two brighter variants of Wallpaper B using the original as an edit reference. `wallpaper-b2-bright-nebula-tree.png` is the high-brightness alternative; `wallpaper-b3-balanced-nebula-tree.png` keeps the left side calmer and moderately illuminated for terminal readability. Exported the balanced variant to 3840x2160 as `design-drafts/task-36.1/wallpapers/wallpaper-b3-balanced-nebula-tree-4k.png`.

Selected visual assets integrated (2026-07-23): moved the user-created screenshot to `assets/screenshots/tree-style-terminal.png` and updated README to reference it. Preserved selected Wallpaper B2 Bright as `assets/screenshots/wallpaper-nebula-tree.png` for future screenshot refreshes. Removed the previous screenshot and all temporary/unselected icon and wallpaper drafts. Rebuilt selected Icon A concept as the deterministic, Apache-2.0-licensed SVG `data/icons/hicolor/scalable/apps/de.cubigato.TreeStyleTerminal.svg`. XML validation and Inkscape rendering succeeded; a 32x32 render remains recognizable. The selected screenshot still visibly contains user/host labels (`kiney-duo`, `jump01`), so confirm separately before using the same image in public AppStream metadata.

Visual review follow-up (2026-07-23): user explicitly accepted the visible hostnames in the screenshot for publication. Corrected the SVG icon's right subtree so its lower-right branch and node stay inside the terminal panel. Revalidated XML and inspected fresh 512x512 and 32x32 renders.

User approved implementation of the remaining TASK-36.1 scope and selected version 0.8.1 as the patch release for the packaging/identity changes.

Implementation verification (2026-07-23): all five acceptance criteria are implemented. Permanent ID is shared across runtime, desktop entry, icon basename, and AppStream component. `_version.py` is the authoritative version source and Setuptools built `tree_style_terminal-0.8.1-py3-none-any.whl`. Added normal Exec desktop launch, both PATH entry points, AppStream URLs/licenses/categories/release/screenshot, reproducible SVG-to-PNG instructions, sdist manifest, changelog entry, and metadata consistency tests. Verification: 339 project tests passed; 4 focused release-metadata tests passed after final cleanup; Ruff passed; desktop-file-validate passed; xmllint passed; appstreamcli validate --no-net passed with one pedantic hint (`cid-contains-uppercase-letter`) because the deliberately selected permanent ID `de.cubigato.TreeStyleTerminal` contains uppercase characters. Network URL checks were unavailable before push; initial online-mode validation emitted only DNS/screenshot-not-yet-published warnings. Keep task In Progress pending human review and acceptance.

User does not require Binnenmajuskeln and approved changing the permanent application ID to `de.cubigato.treestyleterminal` to satisfy AppStream's lowercase recommendation.

Lowercase identity verification (2026-07-23): renamed all runtime, desktop, AppStream, SVG, and PNG identity references/files to `de.cubigato.treestyleterminal`. AppStream validation now succeeds even with `--pedantic --explain` and emits no issue. Desktop and XML validators pass, all 339 tests pass, Ruff passes, and `git diff --check` passes. Acceptance criteria rechecked after the approved identity change; task remains In Progress for human acceptance.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Established the permanent lowercase Linux application identity `de.cubigato.treestyleterminal` for the 0.8.1 patch release. Added and validated the shared desktop entry, AppStream metadata, Apache-2.0 application icon in SVG and 512px PNG form, release screenshot, retained screenshot wallpaper, public project URLs, changelog entry, source-distribution manifest, and packaging/release maintenance guide. Runtime, icon, desktop, and AppStream IDs are consistent; both `tree-style-terminal` and `tst` remain declared command entry points, with normal Exec-based desktop launching and existing multi-instance behavior preserved. Consolidated version authority in `_version.py` and configured Setuptools to consume it dynamically; a test wheel built as 0.8.1. Added automated release-metadata consistency coverage. Verification completed with 339 passing tests, clean Ruff and diff checks, successful desktop/XML validation, and clean AppStream validation including pedantic mode. User reviewed and accepted the icon, screenshot/hostname choice, lowercase identity, and completed implementation.
<!-- SECTION:FINAL_SUMMARY:END -->
