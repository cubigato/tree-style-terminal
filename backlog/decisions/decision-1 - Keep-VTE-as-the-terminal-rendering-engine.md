---
id: decision-1
title: Keep VTE as the terminal rendering engine
date: '2026-05-28 08:27'
status: accepted
---
## Context

Tree Style Terminal is a Python/GTK terminal emulator built around the standard VTE terminal component.

Replacing VTE with a custom GPU or canvas-based terminal renderer would turn the project into a terminal rendering engine project. That would add a large maintenance burden around terminal emulation correctness, scrollback, selection, input method handling, accessibility, font shaping, hyperlink detection, escape sequence behavior, and terminal graphics protocols.

The current product goal is the tree-style session model and GTK application experience around a reliable terminal widget, not reimplementing terminal rendering.

This decision supersedes TASK-22, which tracked the same boundary as an open backlog task.


## Decision

Tree Style Terminal will keep VTE as the terminal rendering engine.

Renderer-level behavior remains delegated to VTE, including terminal emulation, glyph rendering, text selection, scrollback rendering, hyperlink support exposed by VTE, cursor rendering, input method integration, accessibility behavior, and supported terminal graphics or escape-sequence handling.

Future work may integrate VTE features or GTK UI around VTE, but replacing VTE with a custom renderer is out of scope unless a future architecture decision explicitly supersedes this one.


## Consequences

The project can focus on session-tree behavior, persistence, configuration, actions, and GTK application polish.

Features that require renderer internals must be implemented only when VTE exposes suitable APIs, or recorded as unsupported/deferred. The project avoids owning terminal-emulation compatibility and renderer maintenance.
