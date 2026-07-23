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
   appstreamcli validate data/de.cubigato.treestyleterminal.metainfo.xml
   xmllint --noout data/de.cubigato.treestyleterminal.metainfo.xml
   xmllint --noout \
     data/icons/hicolor/scalable/apps/de.cubigato.treestyleterminal.svg
   ```

7. Run the test suite and Ruff before publishing.

Package-specific installation paths and build mechanics belong to their
respective Debian, AppImage, PyPI, or Flatpak tasks.
