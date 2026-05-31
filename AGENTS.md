This is a python/GTK terminal emulator app.
It's still in beta / active development.
When asked to add a feature make clean and simple implementation - no extra bells and whistles
Always use the project virtual environment for Python commands: `.venv/bin/python`.
Keep Ruff checks clean after each task: run `.venv/bin/python -m ruff check src tests`
before handoff and fix any new findings introduced by the task.

Backlog.md is used for project task tracking.
- Use the `backlog` CLI for task operations instead of creating ad-hoc markdown files.
- Tasks live under `backlog/tasks/`; keep them in Backlog.md's generated format.
- Treat the task `ordinal` field as the source of truth for the board order humans see: lower ordinal means higher/up on the board. Do not rely on the default `backlog task list --plain` order for board priority.
- Before adding a new task or bug, search/list existing backlog items to avoid duplicates.
- Use simple statuses from `backlog/config.yml`: `To Do`, `next`, `In Progress`, `Done`.
- Do not move tasks to `Done` until a human has reviewed and accepted the change.
- Record bugs as backlog tasks with the `bug` label and close them by moving the task to `Done`.
