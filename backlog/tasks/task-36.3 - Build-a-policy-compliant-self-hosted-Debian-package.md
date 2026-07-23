---
id: TASK-36.3
title: Build a policy-compliant self-hosted Debian package
status: Done
assignee:
  - Codex
created_date: '2026-07-23 13:16'
updated_date: '2026-07-23 23:14'
labels:
  - packaging
  - debian
  - release
  - 'blocker:1.0'
dependencies:
  - TASK-36.1
  - TASK-36.2
references:
  - 'https://www.debian.org/doc/debian-policy/'
  - 'https://www.debian.org/doc/packaging-manuals/python-policy/'
  - 'https://manpages.debian.org/trixie/dh-python/pybuild.1.en.html'
  - 'https://packages.debian.org/trixie/python3-gi'
  - 'https://packages.debian.org/trixie/gir1.2-gtk-3.0'
  - 'https://packages.debian.org/trixie/gir1.2-vte-2.91'
  - 'https://packages.debian.org/trixie/python3-yaml'
modified_files:
  - .containerignore
  - Makefile
  - debian/changelog
  - debian/control
  - debian/copyright
  - debian/pybuild.testfiles
  - debian/rules
  - debian/source/format
  - debian/source/lintian-overrides
  - debian/tests/control
  - debian/tests/smoke
  - debian/tree-style-terminal.1
  - debian/tree-style-terminal.docs
  - debian/tree-style-terminal.examples
  - debian/tree-style-terminal.install
  - debian/tree-style-terminal.links
  - debian/tree-style-terminal.lintian-overrides
  - debian/tree-style-terminal.manpages
  - debian/watch
  - packaging/debian/Containerfile
  - packaging/debian/build.sh
  - packaging/debian/container-build.sh
  - PACKAGING.md
  - README.md
  - pyproject.toml
  - tests/unit/test_dpi_scaling.py
parent_task_id: TASK-36
priority: high
ordinal: 2300
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provide a native Debian package that regular users can install without a Python development environment and that can later be taken through Debian's official sponsorship process without replacing the packaging approach. Use Debian's Python and GTK/VTE packages rather than vendoring native runtime components, and keep user configuration outside package ownership.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A non-native Debian source package and Architecture: all binary package build from a clean checkout using current Debian Python packaging helpers.
- [x] #2 The binary package declares Python, PyGObject, PyYAML, GTK3, and VTE runtime dependencies using Debian package names and does not download dependencies during the build.
- [x] #3 Installing with apt provides the documented command, application menu entry, icon, MetaInfo, license, and all runtime resources; uninstall and upgrade behavior preserves user configuration.
- [x] #4 The package passes a clean build, Lintian, install/uninstall checks, and an application launch smoke test on the declared Debian support baseline.
- [x] #5 Debian build, verification, local installation, versioning, and self-publication instructions are documented, including why the package does not yet provide x-terminal-emulator.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Target Debian 13 (trixie), package version 0.8.1-1, source format 3.0 (quilt), Architecture: all, Rules-Requires-Root: no, Standards-Version 4.7.4.1, and Maintainer Jannik Winkel <jannik.winkel@cubigato.de>.
2. Build with debhelper compat 13, dh-sequence-python3, pybuild-plugin-pyproject, python3-all, python3-setuptools, and python3-pytest. Run the full upstream suite through pybuild under Xvfb and include its source/metadata fixtures.
3. Declare dependencies proven from imports and a minimal Debian installation: ${python3:Depends}, ${misc:Depends}, python3-gi, python3-yaml, GTK 3 and VTE 2.91 GIR packages, and librsvg2-common for bundled SVG icons. Recommend ca-certificates for optional HTTPS AI requests; remove the stale PyCairo documentation.
4. Install both entry points, Python UI/CSS/icon resources, desktop entry, MetaInfo, scalable and 512px icons, documentation, and workspace profile examples. Keep user configuration outside package ownership.
5. Add tree-style-terminal(1) and a tst(1) alias. Do not provide x-terminal-emulator because the required -e command and -T title interface is absent.
6. Add machine-readable Apache-2.0/CC0-1.0 copyright coverage, a GitHub-tag watch file, non-native changelog, and narrowly documented Lintian overrides for the private first build and Trixie's stale Policy knowledge.
7. Add an installed-package smoke test covering both CLI names, metadata validation, packaged resources, and controlled real GTK startup under Xvfb.
8. Document clean builds, verification, APT installation, versioning, manual self-publication, configuration preservation, Debian submission preparation, and the x-terminal-emulator decision. CI automation remains TASK-36.6.
9. Verify full source/binary packaging in fresh Debian 13 with networking disabled during dpkg-buildpackage: tests, Lintian, install/reinstall/remove, contents, dependency resolution, metadata, GTK launch, and configuration preservation.
10. Add a small Makefile frontend and Podman helper. make deb builds/reuses a Debian 13 image, performs a network-isolated binary build plus Lintian, and places the .deb in build/debian. make deb-check additionally installs, smoke-tests, reinstalls, removes, and checks configuration preservation. Derive builder dependencies from debian/control.
11. Modernize pyproject.toml license metadata to an SPDX string and remove the deprecated redundant license classifier. Run local pytest, Ruff, shell syntax, and diff checks before handoff; leave the task In Progress for human review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented a Debian 13 (trixie) non-native 3.0 (quilt) source package and Architecture: all binary package for 0.8.1-1. Runtime imports were audited from code. Direct runtime dependencies are python3-gi, python3-yaml, GTK 3 and VTE 2.91 GIR packages, plus librsvg2-common for bundled SVG icons; ca-certificates is recommended for optional HTTPS AI requests. PyCairo is unused and its stale README claim was removed. Build-time GUI tests run under Xvfb, and a workstation-dependent DPI test now mocks the Gdk screen it actually exercises. Packaging installs both commands, desktop/AppStream metadata, icons, Python resources, docs/examples, and a manpage with tst alias. It deliberately does not claim x-terminal-emulator because -e and -T are unsupported. Private-build and stale-Trixie-Lintian warnings have narrowly documented overrides for later Debian submission. A conventional Makefile fronts a Podman workflow: make deb creates the .deb under build/debian, while make deb-check adds installed-package and configuration-preservation checks. The builder derives dependencies from debian/control through mk-build-deps, mounts the checkout read-only, and disables networking for the actual build container. pyproject.toml now uses the non-deprecated SPDX license string.

Podman workflow verification on 2026-07-24: `make deb` succeeded and produced build/debian/tree-style-terminal_0.8.1-1_all.deb owned by the invoking user. `make deb-check` reused the cached builder, passed all 345 pybuild tests and Lintian, installed the package, passed metadata/resource/real-GTK smoke checks, and preserved a user config checksum across reinstall and removal. The package-build container used `--network none`; only initial builder-image dependency installation used network. Local pytest (345 passed), Ruff, shell syntax checks, and git diff --check also passed. Setuptools emitted no license deprecation warnings after the pyproject update.

Added and documented a conventional `make clean` target. It removes only the ignored project `build/` directory and intentionally preserves the cached Podman builder image. Verified the complete fresh path: `make clean` removed all .deb artifacts, then `make deb` rebuilt 0.8.1-1 successfully with 345 passing tests and restored build/debian/tree-style-terminal_0.8.1-1_all.deb.

Human acceptance on 2026-07-24: Jannik installed the generated .deb on the real target system, confirmed that Tree Style Terminal launches and runs correctly, and approved completing the task.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented and verified a policy-oriented Debian 13 package for Tree Style Terminal 0.8.1-1. The package uses Debian's Python, PyGObject, GTK 3, VTE, PyYAML, and SVG loader packages; installs both CLI names, desktop/AppStream metadata, icons, resources, examples, and manual pages; preserves user configuration; and deliberately leaves x-terminal-emulator registration to TASK-36.12 until the required CLI contract exists.

Added a rootless Podman build workflow with `make deb`, producing the finished artifact in `build/debian/`, plus `make deb-check` for Lintian, installation, real GTK startup, reinstall/removal, and configuration-preservation checks. `make clean` removes only local build artifacts while retaining the cached builder image. Builder dependencies are generated from `debian/control`, the checkout is mounted read-only, and the actual package build runs without network access. Modernized the pyproject SPDX license metadata and removed stale PyCairo documentation.

Verification: 345 project and pybuild tests pass; Ruff, shell syntax, metadata validation, git diff checks, and Lintian pass; clean Podman source/binary package builds and APT lifecycle tests pass. The generated .deb was additionally installed and run successfully on the maintainer's real system.
<!-- SECTION:FINAL_SUMMARY:END -->
