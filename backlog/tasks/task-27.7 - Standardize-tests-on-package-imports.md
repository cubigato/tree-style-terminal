---
id: TASK-27.7
title: Standardize tests on package imports
status: Done
assignee: []
created_date: '2026-05-27 22:19'
updated_date: '2026-05-30 00:16'
labels: []
dependencies: []
references:
  - TASK-27
  - tests/test_main_window.py
  - tests/test_terminal_widget.py
  - tests/test_imports.py
  - tests/conftest.py
modified_files:
  - tests/conftest.py
  - tests/test_imports.py
  - tests/test_main_window.py
  - tests/test_terminal_widget.py
parent_task_id: TASK-27
priority: high
ordinal: 9500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. Tests currently mix imports from src.tree_style_terminal and the package namespace tree_style_terminal. Standardize on the installed package namespace so tests exercise the same import path users get from the package and avoid hiding packaging/import drift.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Tests no longer import application modules through src.tree_style_terminal unless there is a documented exception.
- [x] #2 test_main_window.py, test_terminal_widget.py, and test_imports.py use tree_style_terminal imports.
- [x] #3 conftest/import-path setup still allows local test execution from the repository checkout.
- [x] #4 No runtime application code is changed unless required to fix a real package import issue exposed by the test cleanup.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Standardized test imports from src.tree_style_terminal to tree_style_terminal in the targeted tests; kept conftest src-layout path setup for local checkout execution. Verified with .venv/bin/python -m pytest (226 passed).
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Full test suite passes with .venv/bin/python -m pytest.
- [x] #2 Import behavior is consistent between tests and installed package entry points.
<!-- DOD:END -->
