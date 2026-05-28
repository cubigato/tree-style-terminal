---
id: TASK-27.3
title: Normalize runtime diagnostics to logging
status: Done
assignee: []
created_date: '2026-05-27 22:18'
updated_date: '2026-05-28 07:49'
labels: []
dependencies: []
references:
  - TASK-27
  - src/tree_style_terminal/main.py
modified_files:
  - src/tree_style_terminal/main.py
  - src/tree_style_terminal/config/defaults.py
  - tests/unit/test_css_loader.py
  - tests/unit/test_config.py
  - tests/unit/test_logging_config.py
  - README.md
  - CONFIG.md
  - config-example.yaml
parent_task_id: TASK-27
priority: high
ordinal: 250
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. Runtime app paths currently mix print() and logging. Keep print() for explicit CLI output such as --show-info and --test-fonts, but use logging for normal application startup, CSS/theme loading, sidebar/focus state changes, and recoverable runtime warnings.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Runtime UI/application paths in main.py use logging instead of print for non-CLI diagnostics.
- [x] #2 Explicit CLI diagnostic output for --show-info and --test-fonts remains printed to stdout/stderr as appropriate.
- [x] #3 Error handling for transparency/config startup remains user-visible enough to diagnose startup failure.
- [x] #4 No unrelated behavior, CSS, or session-management changes are included.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented in main.py: normal runtime diagnostics now use logging for CSS/theme loading, startup, sidebar/focus state changes, recoverable warnings, and transparency/config startup errors. Intentional print output remains in _print_system_info() for --show-info and print_font_test_info() for --test-fonts, including their direct CLI error messages.

Follow-up: added configurable log level through app.log_level (default warning) and --log-level CLI override. Updated help text, first-start config template, config example, README, and CONFIG.md.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Relevant main/app tests pass.
- [x] #2 A short note in the task clarifies which outputs intentionally remain print-based.
<!-- DOD:END -->
