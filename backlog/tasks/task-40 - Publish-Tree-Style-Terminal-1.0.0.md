---
id: TASK-40
title: Publish Tree Style Terminal 1.0.0
status: next
assignee: []
created_date: '2026-07-24 00:57'
updated_date: '2026-07-24 00:57'
labels:
  - release
  - 'blocker:1.0'
dependencies:
  - TASK-36
documentation:
  - PACKAGING.md
  - CHANGELOG.md
modified_files:
  - src/tree_style_terminal/_version.py
  - CHANGELOG.md
  - data/de.cubigato.treestyleterminal.metainfo.xml
  - PACKAGING.md
  - README.md
priority: high
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the actual 1.0.0 release as an agent-guided checklist. Prepare and freeze the release commit, build and thoroughly verify every public artifact from that exact source state, publish the tag and artifacts as a GitHub Release, and coordinate announcement copy and manual posting. Codex should drive the sequence, perform safe local checks and CLI operations, stop for explicit approval before external publication, and prompt the maintainer only for authentication, subjective release decisions, and channel-specific manual actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The release commit consistently declares version 1.0.0 in the authoritative version source, changelog, AppStream release metadata, and all user-facing release notes, with the intended release date and no unresolved blocker:1.0 tasks.
- [ ] #2 From a clean checkout of the exact release commit, the complete Python test suite, Ruff, metadata checks, `make deb-check`, and `make appimage-check` pass; final Debian and AppImage artifacts are also exercised on a real workstation, including launch, host shell, configuration preservation, and both normal and fallback AppImage execution where applicable.
- [ ] #3 The final release directory contains the Debian package, versioned AppImage, SHA-256 verification data for every downloadable binary, the AppImage bundled-component/license inventory, and reviewed release notes; every artifact is traceable to the same tested commit.
- [ ] #4 An annotated or signed `v1.0.0` tag and the corresponding release commit are pushed to GitHub only after maintainer approval, and a non-draft GitHub Release is created through an auditable CLI command rather than manual browser uploads.
- [ ] #5 Fresh downloads from the published GitHub Release pass checksum verification and basic launch/install checks, and the release page contains accurate installation, compatibility, security, and known-limitation information.
- [ ] #6 An announcement kit is drafted and approved with a concise canonical announcement, channel-specific variants, screenshots and release links; the maintainer is guided through publishing on the selected channels such as X and Hacker News, and published URLs are recorded on the task.
- [ ] #7 Post-release checks confirm that repository links and documentation point users to the published release, urgent issues are recorded as backlog bugs, and the release checklist is closed with the final tag, commit, artifact checksums, release URL, and announcement URLs documented.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Establish the release gate with the maintainer: confirm TASK-36 acceptance, freeze the intended 1.0 scope, choose the release date, decide annotated versus signed tag, select announcement channels, and confirm a clean working tree and GitHub repository target.
2. Prepare the release commit: set version 1.0.0 in the authoritative source, update CHANGELOG and AppStream metadata with reviewed notes/date, audit README and packaging instructions, and generate a concise GitHub release-notes draft plus a known-limitations section.
3. Run pre-release validation locally. Codex executes the full Python suite, Ruff, metadata validators, shell checks, `make clean`, `make deb-check`, and `make appimage-check`, then records exact commands and results. Any failure stops publication and is fixed or recorded as a blocker.
4. Freeze the exact source state. After maintainer review, create the release commit; verify its commit ID and clean tree. Build all final artifacts from that exact commit, assemble them in one release directory, generate/check SHA-256 data for every downloadable binary, and retain the AppImage license inventory.
5. Guide the maintainer through real-system acceptance as an explicit checklist: install/upgrade the Debian package, start both commands and the desktop launcher, open a host shell, verify configuration preservation; run the AppImage normally and with extract-and-run fallback; inspect version/help, icon, screenshot, and basic terminal behavior. Record pass/fail before tagging.
6. Prepare CLI publication. The GitHub remote already targets `cubigato/tree-style-terminal`; GitHub CLI is currently absent, so install it or use an approved standalone binary, then have the maintainer authenticate with `gh auth login`. Codex verifies identity/repository without exposing credentials and prints the exact proposed tag, push, and release commands before requesting approval.
7. Publish with explicit maintainer gates: create the annotated/signed `v1.0.0` tag, push the release commit and tag to GitHub, create a draft GitHub Release with `gh release create --draft`, upload the reviewed artifacts through the CLI, inspect the rendered release and asset list, then publish it with `gh release edit --draft=false` only after final approval.
8. Independently verify publication: download every asset from the GitHub Release into a fresh temporary directory with `gh release download`, verify checksums, repeat basic package/AppImage launch checks, and record the GitHub release URL, tag, commit, artifact names, sizes, and hashes.
9. Prepare announcements while technical verification runs: draft one canonical announcement and tailored variants for the selected channels (at minimum X and a Show HN submission), choose screenshot/link/alt text, and present each final post for approval. The maintainer performs channel logins and any anti-bot/manual submission; Codex guides one item at a time and records each published URL. Additional channels such as Mastodon, relevant Linux communities, or the company site remain an explicit maintainer choice rather than automatic cross-posting.
10. Perform post-release checks, record bugs instead of silently changing published artifacts, update task notes with all permanent URLs and checksums, and close TASK-40 only after the maintainer confirms the release and announcements are complete.
<!-- SECTION:PLAN:END -->
