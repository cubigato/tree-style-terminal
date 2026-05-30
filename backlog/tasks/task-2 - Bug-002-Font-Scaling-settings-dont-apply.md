---
id: TASK-2
title: 'Bug #002: Font Scaling settings don''t apply'
status: Done
assignee: []
created_date: '2026-05-26 22:04'
updated_date: '2026-05-30 00:16'
labels:
  - bug
  - legacy
dependencies: []
priority: medium
ordinal: 5500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Legacy bug migrated from bugs/closed/002-font-scaling.md. Reported 2025-06-03 by kiney. Setting display.dpi_scale in the config file had no visible effect. Expected fonts to scale with display.dpi_scale; actual behavior was that fonts stayed the same size.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Set display.dpi_scale in the config file
- [x] #2 Launch the application
- [x] #3 Fonts reflect the configured DPI scale
<!-- AC:END -->



## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Root cause: configuration key confusion around display.dpi_scale, disabled CSSLoader._load_system_css(), config DPI settings not read by the CSS loader, and overly conservative auto-detection. Fix applied: reimplemented system CSS generation for font scaling, integrated config file dpi_scale, kept priority order CLI > environment > config > auto-detection, added error handling/fallbacks, and recalibrated auto-detection for high-DPI and retina displays.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Legacy ticket says to verify with display.dpi_scale: 1.5, --test-fonts, CLI/env/config priority checks, display.dpi_scale: auto, --dpi 144, TST_DPI=180, and dpi_scale: 1.5.
<!-- SECTION:FINAL_SUMMARY:END -->
