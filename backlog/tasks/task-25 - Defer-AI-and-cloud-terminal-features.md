---
id: TASK-25
title: Add AI-assisted shell command drafting
status: Done
assignee: []
created_date: '2026-05-26 22:11'
updated_date: '2026-07-22 23:15'
labels:
  - feature
  - ai
  - 'area:integration'
dependencies: []
references:
  - 'https://docs.warp.dev/features/windows'
modified_files:
  - CONFIG.md
  - README.md
  - CHANGELOG.md
  - pyproject.toml
  - src/tree_style_terminal/__init__.py
  - src/tree_style_terminal/ai_command.py
  - src/tree_style_terminal/config/defaults.py
  - src/tree_style_terminal/config/manager.py
  - src/tree_style_terminal/controllers/ai_command.py
  - src/tree_style_terminal/controllers/shortcuts.py
  - src/tree_style_terminal/main.py
  - >-
    src/tree_style_terminal/resources/icons/hicolor/scalable/actions/ai-sparkles-symbolic.svg
  - src/tree_style_terminal/widgets/terminal.py
  - tests/test_ai_command.py
  - tests/test_basic.py
  - tests/test_main_window.py
  - tests/test_terminal_widget.py
  - tests/unit/test_ai_command_controller.py
  - tests/unit/test_config.py
  - tests/unit/test_shortcuts.py
priority: medium
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add an opt-in command-drafting feature backed by a configured OpenAI-compatible API. The user may type a natural-language description on the current prompt and invoke a keyboard shortcut. The application sends a bounded portion of the current shell history plus that editable input in a purpose-built prompt, then replaces the entire current input line with the returned command. It must not submit the command or synthesize Enter, so the user can review and edit it first.
<!-- SECTION:DESCRIPTION:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 User-facing configuration and privacy implications are documented in CONFIG.md and README.md.
- [x] #2 Ruff and the relevant automated tests pass.
- [x] #3 Newly created configuration files are readable and writable only by the current user.
<!-- DOD:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The YAML config supports an OpenAI-compatible endpoint, API key, required model identifier, and a configurable non-conflicting shortcut; the feature remains inactive until the required API settings are supplied.
- [x] #2 Invoking the shortcut captures a bounded recent shell history and the full current editable line, keeping the user intent distinct when constructing a concise prompt that requests a shell command.
- [x] #3 A successful response replaces the full current editable line with the proposed command and never submits it; the user must explicitly press Enter.
- [x] #4 The network request does not freeze the GTK UI, and errors or invalid responses leave the existing input unchanged while presenting a useful non-disruptive error.
- [x] #5 API credentials and transmitted shell content are never written to application logs, and no request is made while the feature is unconfigured.
- [x] #6 Configuration, prompt construction, response handling, line replacement, no-submit behavior, and failure paths have automated coverage.
- [x] #7 The AI command-drafting action is available through both the configured keyboard shortcut and a header-bar button with a bundled theme-compatible symbolic sparkle icon; the action requires an active terminal.
- [x] #8 If the required AI API configuration is missing or incomplete, invoking either trigger makes no network request and shows a short help dialog with the config path and required fields, without exposing credential values.
- [x] #9 Right-clicking the AI button offers one-shot requests with 200 lines, 1000 lines, or up to 1000 lines of explicitly selected terminal text, while normal click and shortcut behavior remain at the 40-line default.
- [x] #10 When the user asks for an explanation or diagnosis instead of an executable action, the model is instructed to return one concise shell comment line beginning with '# ' rather than wrapping prose in printf, echo, or another command.
- [x] #11 The AI-specific GTK controls, context menu, request threading, progress state, dialogs, and completion handling live in a cohesive controller instead of continuing to grow MainWindow; MainWindow retains only wiring and shortcut delegation.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented opt-in OpenAI-compatible shell command drafting through a configurable shortcut and bundled symbolic sparkle button. Requests run off the GTK thread, use bounded terminal context, never log credentials or transmitted content, and insert only validated single-line commands without submitting them. Missing configuration shows a help dialog, failures preserve input, fresh config files use mode 0600, and user-facing privacy/configuration documentation and automated coverage were added.

Fixed terminal-input capture on current VTE releases by using get_text_range_format(TEXT) instead of the deprecated attribute-returning API, while retaining an older-VTE fallback and clamping history reads to valid absolute rows.

Added a visible spinner and drafting tooltip on the AI button for the duration of each background request, with automatic restoration of the sparkle icon. Added explicit regression coverage for trailing and embedded newline/carriage-return responses.

Added a one-shot secondary-click context menu to the AI button for 200-row, 1000-row, or explicitly selected-text requests. Selected text is available only when the active terminal has a selection and is bounded to its trailing 1000 lines; normal click and shortcut requests remain at 40 rows.

Updated the prompt contract so explanation, interpretation, and diagnosis requests return one concise non-executable shell comment beginning with '# ' instead of printf/echo prose commands. Verified the behavior with mocked tests and a synthetic live Terra request.

Extracted the newly added AI GTK orchestration from MainWindow into a cohesive AICommandController. MainWindow now only constructs and packs the controller, delegates the shortcut, and forwards terminal availability; dedicated controller tests preserve the behavior. This reduces main.py by 258 lines without refactoring unrelated existing responsibilities.

Released as version 0.8.0 with a changelog entry dated 2026-07-23; the full test suite (335 tests) and Ruff checks pass.
<!-- SECTION:FINAL_SUMMARY:END -->
