This is a python/GTK terminal emulator app.
It's still in beta / active development.
When asked to add a feature make clean and simple implementation - no extra bells and whistles
Always use the project virtual environment for Python commands: `.venv/bin/python`.

Backlog.md is used for project task tracking.
- Use the `backlog` CLI for task operations instead of creating ad-hoc markdown files.
- Tasks live under `backlog/tasks/`; keep them in Backlog.md's generated format.
- Before adding a new task or bug, search/list existing backlog items to avoid duplicates.
- Use simple statuses from `backlog/config.yml`: `To Do`, `next`, `In Progress`, `Done`.
- Do not move tasks to `Done` until a human has reviewed and accepted the change.
- Record bugs as backlog tasks with the `bug` label and close them by moving the task to `Done`.
