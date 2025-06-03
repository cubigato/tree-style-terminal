# Bug #001: Sidebar transparency not working with terminal transparency

**Date Reported:** 2025-06-03
**Reporter:** User
**Severity:** Medium
**Status:** Open

## Summary
Sidebar remains opaque when terminal transparency is configured, despite transparency settings in config file.

## Expected Behavior
Sidebar should be transparent when transparency is configured in the config file, matching terminal transparency behavior.

## Actual Behavior
Terminal transparency works correctly, but sidebar TreeView remains opaque with solid background.

## Steps to Reproduce
1. Configure transparency in config file
2. Launch application
3. Observe that terminal area is transparent
4. Observe that sidebar remains opaque

## Environment
- OS: Linux
- Python version: 3.13.3
- GTK version: 3.24.49
- Terminal: Various

## Additional Notes
Multiple debugging attempts were made including:
- CSS specificity fixes with `!important`
- Removing `.view` class programmatically
- Static CSS rules in `resources/css/style.css`
- Addressing Adwaita theme conflicts

The issue may be related to:
- Desktop compositor support
- Parent window transparency settings
- Complex GTK widget hierarchy (GtkBox → GtkScrolledWindow → GtkViewport → GtkTreeView)

Further investigation needed for terminal transparency configuration interaction.