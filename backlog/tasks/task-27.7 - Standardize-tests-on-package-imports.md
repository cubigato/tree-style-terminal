---
id: TASK-27.7
title: Standardize tests on package imports
status: next
assignee: []
created_date: '2026-05-27 22:19'
updated_date: '2026-05-28 08:25'
labels: []
dependencies: []
references:
  - TASK-27
  - tests/test_main_window.py
  - tests/test_terminal_widget.py
  - tests/test_imports.py
  - tests/conftest.py
parent_task_id: TASK-27
priority: high
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up from TASK-27. Tests currently mix imports from src.tree_style_terminal and the package namespace tree_style_terminal. Standardize on the installed package namespace so tests exercise the same import path users get from the package and avoid hiding packaging/import drift.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Tests no longer import application modules through src.tree_style_terminal unless there is a documented exception.
- [ ] #2 test_main_window.py, test_terminal_widget.py, and test_imports.py use tree_style_terminal imports.
- [ ] #3 conftest/import-path setup still allows local test execution from the repository checkout.
- [ ] #4 No runtime application code is changed unless required to fix a real package import issue exposed by the test cleanup.
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Full test suite passes with .venv/bin/python -m pytest.
- [ ] #2 Import behavior is consistent between tests and installed package entry points.
<!-- DOD:END -->
