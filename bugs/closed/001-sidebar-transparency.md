# Bug #001: Sidebar transparency not working with terminal transparency

**Date Reported:** 2025-06-03
**Date Fixed:** 2026-05-22
**Reporter:** kiney
**Severity:** Medium
**Status:** Fixed

## Summary
Sidebar remained opaque when terminal transparency was configured, despite transparency settings in the config file.

## Expected Behavior
Sidebar should be transparent when transparency is configured in the config file, matching terminal transparency behavior.

## Actual Behavior
Terminal transparency worked correctly, but the sidebar and TreeView stayed opaque with solid theme backgrounds.

## Steps to Reproduce
1. Configure `terminal.transparency` below `1.0`
2. Launch application
3. Observe that terminal area is transparent
4. Observe that sidebar remains opaque

## Environment
- OS: Linux
- Python version: 3.13.3
- GTK version: 3.24.49
- Terminal: Various

## Root Cause
The base CSS transparency rules were loaded before the active theme CSS. The theme files then restored opaque backgrounds on `.sidebar`, `box`, `stack`, `treeview`, and related GTK containers.

The sidebar also contains multiple GTK layers (`GtkRevealer`, `GtkBox`, `GtkScrolledWindow`, viewport, `GtkTreeView`), so making only the TreeView transparent was not enough.

## Fix Applied
- Added runtime sidebar transparency CSS generated from `terminal.transparency`
- Loaded that runtime CSS after theme CSS via the existing system CSS provider
- Applied transparent backgrounds to the complete sidebar widget chain
- Added explicit CSS hooks for outer sidebar containers
- Kept theme-specific selection, hover, and border colors intact
- Exposed the sidebar `GtkScrolledWindow` for clearer styling and tests

## Testing
Verified with the project virtual environment:

```bash
.venv/bin/python -m pytest -q
```

Result:

```text
183 passed in 2.69s
```
