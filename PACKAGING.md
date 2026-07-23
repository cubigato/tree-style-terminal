# Packaging and release metadata

Tree Style Terminal keeps package-independent Linux desktop metadata in the
upstream repository. Debian, AppImage, and other package formats should install
these shared files instead of maintaining format-specific copies.

## Shared identity

- Application ID: `de.cubigato.treestyleterminal`
- Desktop entry: `data/de.cubigato.treestyleterminal.desktop`
- AppStream metadata: `data/de.cubigato.treestyleterminal.metainfo.xml`
- Icon master:
  `data/icons/hicolor/scalable/apps/de.cubigato.treestyleterminal.svg`
- Screenshot: `assets/screenshots/tree-style-terminal.png`
- Screenshot wallpaper: `assets/screenshots/wallpaper-nebula-tree.png`

Both `tree-style-terminal` and `tst` are public command-line entry points.
Packages should install both commands on `PATH`. The desktop entry launches the
long, descriptive command name and does not claim D-Bus activation.

## Preparing a release

1. Update the single authoritative version in
   `src/tree_style_terminal/_version.py`.
2. Add the matching release and date to `CHANGELOG.md`.
3. Add the same version, date, and concise release notes as the first
   `<release>` in the AppStream metadata.
4. Replace the screenshot at its stable path when the interface changes. Keep
   its declared width and height in the AppStream metadata accurate.
5. Edit the SVG when the application icon changes, then regenerate the PNG:

   ```sh
   inkscape \
     data/icons/hicolor/scalable/apps/de.cubigato.treestyleterminal.svg \
     --export-type=png \
     --export-width=512 \
     --export-filename=data/icons/hicolor/512x512/apps/de.cubigato.treestyleterminal.png
   ```

6. Validate the shared metadata:

   ```sh
   desktop-file-validate data/de.cubigato.treestyleterminal.desktop
   appstreamcli validate --no-net \
     data/de.cubigato.treestyleterminal.metainfo.xml
   xmllint --noout data/de.cubigato.treestyleterminal.metainfo.xml
   xmllint --noout \
     data/icons/hicolor/scalable/apps/de.cubigato.treestyleterminal.svg
   ```

7. Run the test suite and Ruff before publishing.

Package-specific installation paths and build mechanics belong to their
respective Debian, AppImage, PyPI, or Flatpak tasks.

## Debian package

The Debian package targets Debian 13 (trixie) and uses the distribution's
Python, GTK 3, PyGObject, PyYAML, and VTE packages. It does not vendor Python or
native libraries and does not download dependencies during the package build.

### One-command Podman build

The normal build only requires GNU Make and rootless Podman on the host:

```sh
make deb
```

This builds or reuses a Debian 13 builder image, runs `dpkg-buildpackage` and
Lintian in a disposable container, and writes the finished package to:

```text
build/debian/tree-style-terminal_0.8.1-1_all.deb
```

Remove all local build artifacts before rebuilding with:

```sh
make clean
make deb
```

`make clean` removes only the ignored `build/` directory. It keeps the Podman
builder image so that subsequent clean builds can reuse the dependency layers.

APT needs network access while Podman initially creates the builder image. The
actual package build runs in a separate container with networking disabled.
The source checkout is mounted read-only; build intermediates remain inside
the disposable container.

For the release-level package check, use:

```sh
make deb-check
```

In addition to the normal build and Lintian run, this installs the package,
executes the installed-package GTK smoke test under Xvfb, reinstalls and
removes it, and verifies that user configuration survives both operations.

The image name and Podman executable can be overridden when necessary:

```sh
DEB_IMAGE=localhost/custom-tst-builder PODMAN=podman make deb
```

### Versioning

Debian versions append a packaging revision to the upstream version. Upstream
release `0.8.1` therefore starts as Debian version `0.8.1-1`. Increment the
suffix for packaging-only revisions and update `debian/changelog` with `dch`;
change the upstream version only when preparing a new upstream release.

### Manual host build: install tools

The Podman workflow above is the normal path. To build directly on a Debian 13
host instead, install the package's declared build dependencies and additional
verification tools:

```sh
sudo apt update
sudo apt build-dep .
sudo apt install devscripts lintian appstream desktop-file-utils xvfb xauth
```

### Manual host build: binary and source packages

A local unsigned binary build can be made directly from a clean checkout:

```sh
dpkg-buildpackage --build=binary --unsigned-changes
```

For a non-native source package, place the matching upstream archive beside the
checkout. For a release tag maintained in this repository:

```sh
git archive \
  --format=tar.gz \
  --prefix=tree-style-terminal-0.8.1/ \
  --output=../tree-style-terminal_0.8.1.orig.tar.gz \
  v0.8.1 -- . ':(exclude)debian'
dpkg-buildpackage --build=source --unsigned-source --unsigned-changes
```

Build both source and binary artifacts with:

```sh
dpkg-buildpackage --build=full --unsigned-source --unsigned-changes
```

The build runs the upstream Pytest suite through Pybuild. Network access is
needed only when APT installs the declared build dependencies, never during
`dpkg-buildpackage`.

### Verify and install

Run Lintian against the generated changes files and inspect the binary package:

```sh
lintian ../tree-style-terminal_0.8.1-1_*.changes
dpkg-deb --info ../tree-style-terminal_0.8.1-1_all.deb
dpkg-deb --contents ../tree-style-terminal_0.8.1-1_all.deb
```

Install through APT so dependencies are resolved normally:

```sh
sudo apt install ../tree-style-terminal_0.8.1-1_all.deb
tree-style-terminal --help
tst --help
xvfb-run -a tree-style-terminal --test-fonts
```

To rerun the installed-package smoke test, install `autopkgtest` and use the
generated binary:

```sh
autopkgtest \
  ../tree-style-terminal_0.8.1-1.dsc \
  -- null
```

Normal upgrades, reinstalls, and removal do not touch
`${XDG_CONFIG_HOME:-~/.config}/tree-style-terminal/config.yaml` because the
file is created and owned by the user, not by the Debian package:

```sh
sudo apt install --reinstall ../tree-style-terminal_0.8.1-1_all.deb
sudo apt remove tree-style-terminal
```

### Manual self-publication

A complete source publication consists of the `.dsc`, `.orig.tar.gz`,
`.debian.tar.xz`, source `.changes`, and `.buildinfo` files. The installable
artifact is the `_all.deb`; publish its checksum alongside direct downloads.
Sign release changes files with `debsign` before feeding them into an APT
repository tool:

```sh
debsign ../tree-style-terminal_0.8.1-1_*.changes
```

Attaching the `.deb` to a release provides manual installation but no update
channel. A signed APT repository additionally needs repository metadata and
publication tooling; the internal GitLab CI implementation is tracked in
TASK-36.6.

### Preparing an upload to Debian

Before the first upload to Debian, file an Intent To Package (ITP) bug. Add its
number to the first `debian/changelog` entry as `Closes: #NNNNNN` and remove
`debian/tree-style-terminal.lintian-overrides`. That override exists only so
the independently published package can have a clean Lintian result before an
ITP bug exists.

Debian 13's Lintian only knows Debian Policy 4.7.2. The source override for
`newer-standards-version` suppresses that stale warning while the package
targets Policy 4.7.4.1; remove the override once the build environment's
Lintian recognizes that version.

### Why the package does not provide `x-terminal-emulator`

Debian's `x-terminal-emulator` virtual package is a command-line compatibility
contract, not merely a category. Providers must support at least `-e command`
with arguments passed directly to the command and `-T title`, then register an
`update-alternatives` entry and matching manual-page alternative.

Tree Style Terminal does not currently implement `-e` or `-T`. It therefore
installs its desktop entry and the `tree-style-terminal` and `tst` commands
without claiming or registering the virtual package. Generic callers of
`x-terminal-emulator` continue to use another installed terminal emulator.
