# Bug #002: Font Scaling settings don't apply

**Date Reported:** 2025-06-03
**Reporter:** kiney
**Severity:** Medium
**Status:** Fixed

## Summary
Setting display.dpi_scale in the config file has no visible effect.

## Expected Behavior
Fonts get bigger or smaller with display.dpi_scale setting

## Actual Behavior
Fonts always stay the same size

## Steps to Reproduce
1. Set display.dpi_scale in the config file
2. Open application
3. Observe font size

## Environment
- OS: Linux
- Python version: 3.13.3
- GTK version: 3.24.49
- Terminal: Various

## Additional Notes
It used to work in previous versions. Broken by CSS reworks for transparency - the `_load_system_css()` method was disabled.

## Root Cause
1. Configuration key mismatch: Users were trying `display.dpi` but the actual key is `display.dpi_scale`
2. The `CSSLoader._load_system_css()` method was disabled, preventing DPI scaling from being applied to CSS
3. Configuration file DPI settings were not being read by the CSS loader
4. Auto-detection algorithm was too conservative, prioritizing GTK XFT DPI over actual monitor DPI

## Fix Applied
- Re-implemented `_load_system_css()` to generate CSS with proper font scaling
- Added configuration integration to read `display.dpi_scale` from config file
- Maintained priority system: CLI args > Environment variables > Config file > Auto-detection
- Added proper error handling and fallbacks
- **Completely fixed auto-detection algorithm with calibrated scaling:**
  - Fixed monitor DPI detection to use reliable methods instead of deprecated APIs
  - **Calibrated to provide optimal 2.0x scaling for ~250 DPI displays (MacBook-style retina)**
  - Prioritizes monitor DPI over conservative GTK XFT DPI for high-DPI displays
  - Ensures minimum 1.8x scaling for other 4K+ displays (≥180 DPI)
  - Ensures minimum 1.25x scaling for 1440p displays (≥120 DPI)
  - Standard 1.0x scaling for 96 DPI displays
  - Auto-detection now provides properly readable fonts instead of tiny ones

## Testing
Verify the fix works by:
1. Setting `display.dpi_scale: 1.5` in config file
2. Launching application
3. Confirming fonts are 150% larger than default

**Auto-detection completely fixed:**
- **Before**: Auto-detection provided ~1.5x scaling on retina displays (fonts too small)
- **After**: Auto-detection provides calibrated 2.0x scaling on retina displays (optimal readability)
- Test with: `python -m tree_style_terminal --test-fonts`
- Priority system working perfectly: CLI > ENV > Config > Auto-detection
- `display.dpi_scale: "auto"` now works correctly in config files
- Manual overrides still work: `--dpi 144`, `TST_DPI=180`, `dpi_scale: 1.5`
