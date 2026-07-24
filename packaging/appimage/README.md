# AppImage packaging

This directory contains the reproducible local AppImage workflow for
Tree Style Terminal.

Run from the repository root:

```sh
make appimage
make appimage-check
```

`make appimage` creates the versioned x86_64 AppImage, its SHA-256 checksum,
and the bundled-component/license inventory in `build/appimage/`.
`make appimage-check` additionally starts the artifact in a minimal Debian 12
container under Xvfb and headless Weston, then verifies the host-shell
environment boundary on both GTK display backends.

The files have deliberately separate responsibilities:

- `Containerfile` pins the Debian snapshot, builder image, AppImage tooling,
  checksums, and build prerequisites.
- `container-build.sh` assembles and validates the AppDir, collects licenses,
  and invokes `appimagetool`.
- `AppRun` prepares only the bundled graphical runtime.
- `build.sh` is the rootless Podman entry point.
- `Containerfile.smoke` and `smoke.sh` provide clean-system X11 and Wayland
  smoke tests.

The checkout is mounted read-only and the actual build and smoke containers
have networking disabled. Only initial builder-image creation needs network
access. The recipe currently supports x86_64 and a glibc 2.36 baseline.

User-facing compatibility, FUSE fallback, security, verification, removal, and
manual publication instructions are maintained in the repository's
`PACKAGING.md`.
