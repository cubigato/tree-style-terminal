---
id: TASK-27.2
title: Extract CSSLoader from main.py
status: Done
assignee: []
created_date: '2026-05-27 22:18'
updated_date: '2026-05-28 11:33'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/main.py
  - tests/unit/test_css_loader.py
  - tests/unit/test_dpi_scaling.py
  - tests/integration/test_theme_integration.py
  - tests/integration/test_font_scaling_integration.py
modified_files:
  - src/tree_style_terminal/css_loader.py
  - src/tree_style_terminal/main.py
  - tests/unit/test_css_loader.py
  - tests/unit/test_dpi_scaling.py
  - tests/integration/test_theme_integration.py
  - tests/integration/test_font_scaling_integration.py
parent_task_id: TASK-27
priority: high
ordinal: 7500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. CSSLoader currently lives in main.py and owns CSS provider loading, theme detection, DPI scaling, runtime sidebar transparency CSS, and related diagnostics. Move it behind a dedicated module while preserving behavior and keeping the first change as a pure extraction.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CSSLoader lives outside main.py in a dedicated module with a clear import path.
- [x] #2 TreeStyleTerminalApp uses the extracted CSSLoader without behavior changes.
- [x] #3 Existing CSS/theme/DPI tests are updated to import the new module path, or a temporary compatibility import is explicitly documented.
- [x] #4 No logging, DPI algorithm, theme behavior, or CSS semantics are changed in this task.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented behavior-preserving CSSLoader extraction to tree_style_terminal.css_loader. Kept the original logger name for this pure extraction and updated CSS/theme/DPI tests to patch/import the new module path. Verification: .venv/bin/python -m pytest (226 passed).
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 CSSLoader, DPI, and theme integration tests pass.
- [x] #2 main.py is smaller and still exposes only any compatibility imports intentionally kept.
<!-- DOD:END -->
