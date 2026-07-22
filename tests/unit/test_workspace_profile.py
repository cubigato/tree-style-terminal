"""Workspace profile YAML loading and validation tests."""

from unittest.mock import patch

import pytest
import yaml

from tree_style_terminal.config.workspace_profile import (
    WorkspaceProfileError,
    export_workspace_profile,
    load_workspace_profile,
)
from tree_style_terminal.models.session import TerminalSession


def test_load_workspace_profile_resolves_inherited_workdirs(tmp_path):
    project = tmp_path / "project"
    logs = project / "build" / "logs"
    logs.mkdir(parents=True)
    profile_path = tmp_path / "my-java-project.yml"
    profile_path.write_text(
        """
version: 1
name: "My Java Project"
workdir: "project"
root:
  title: "project"
  children:
    - title: "server"
      command: "./gradlew bootRun"
    - title: "logs"
      workdir: "build/logs"
""",
        encoding="utf-8",
    )

    profile = load_workspace_profile(profile_path, base_dir=tmp_path)

    assert profile.version == 1
    assert profile.name == "My Java Project"
    assert profile.roots == [profile.root]
    assert profile.root.title == "project"
    assert profile.root.workdir == str(project)
    assert profile.root.children[0].command == "./gradlew bootRun"
    assert profile.root.children[0].workdir == str(project)
    assert profile.root.children[1].workdir == str(logs)


def test_load_workspace_profile_defaults_to_base_dir_without_workdir(tmp_path):
    profile_path = tmp_path / "workspace.yml"
    profile_path.write_text(
        """
version: 1
root:
  title: "shell"
""",
        encoding="utf-8",
    )

    profile = load_workspace_profile(profile_path, base_dir=tmp_path)

    assert profile.root.workdir == str(tmp_path)
    assert profile.root.command is None
    assert profile.root.children == []


def test_load_workspace_profile_supports_multiple_roots(tmp_path):
    project = tmp_path / "project"
    logs = project / "logs"
    scratch = tmp_path / "scratch"
    logs.mkdir(parents=True)
    scratch.mkdir()
    profile_path = tmp_path / "workspace.yml"
    profile_path.write_text(
        """
version: 1
workdir: "project"
roots:
  - title: "project"
    children:
      - title: "logs"
        workdir: "logs"
  - title: "scratch"
    workdir: "../scratch"
""",
        encoding="utf-8",
    )

    profile = load_workspace_profile(profile_path, base_dir=tmp_path)

    assert [root.title for root in profile.roots] == ["project", "scratch"]
    assert profile.roots[0].workdir == str(project)
    assert profile.roots[0].children[0].workdir == str(logs)
    assert profile.roots[1].workdir == str(scratch)


def test_load_workspace_profile_supports_one_selected_node(tmp_path):
    profile_path = tmp_path / "workspace.yml"
    profile_path.write_text(
        """
version: 1
root:
  title: "root"
  children:
    - title: "selected"
      selected: true
    - title: "normal"
""",
        encoding="utf-8",
    )

    profile = load_workspace_profile(profile_path, base_dir=tmp_path)

    assert profile.root.selected is False
    assert profile.root.children[0].selected is True
    assert profile.root.children[1].selected is False


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("version: 2\nroot: {}\n", "version must be 1"),
        ("version: 1\n", "profile must define exactly one of root or roots"),
        (
            "version: 1\nroot: {}\nroots: []\n",
            "profile must define exactly one of root or roots",
        ),
        ("version: 1\nroot: []\n", "root must be a mapping"),
        ("version: 1\nroots: nope\n", "roots must be a list"),
        ("version: 1\nroots: []\n", "roots must contain at least one root"),
        ("version: 1\nroots:\n  - nope\n", r"roots\[0\] must be a mapping"),
        (
            "version: 1\nroots:\n  - children: nope\n",
            r"roots\[0\].children must be a list",
        ),
        (
            'version: 1\nroot:\n  selected: "yes"\n',
            "root.selected must be a boolean",
        ),
        (
            "version: 1\nroots:\n  - selected: true\n  - selected: true\n",
            r"roots\[1\].selected cannot be true because roots\[0\].selected is already true",
        ),
        ("version: 1\nroot:\n  command: 123\n", "root.command must be a string"),
        ("version: 1\nroot:\n  children: nope\n", "root.children must be a list"),
        (
            "version: 1\nroot:\n  children:\n    - children: nope\n",
            r"root.children\[0\].children must be a list",
        ),
    ],
)
def test_load_workspace_profile_reports_yaml_path_errors(tmp_path, content, message):
    profile_path = tmp_path / "workspace.yml"
    profile_path.write_text(content, encoding="utf-8")

    with pytest.raises(WorkspaceProfileError, match=message):
        load_workspace_profile(profile_path, base_dir=tmp_path)


def test_load_workspace_profile_rejects_missing_workdir(tmp_path):
    profile_path = tmp_path / "workspace.yml"
    profile_path.write_text(
        """
version: 1
root:
  workdir: "missing"
""",
        encoding="utf-8",
    )

    with pytest.raises(WorkspaceProfileError, match="root.workdir points to a missing directory"):
        load_workspace_profile(profile_path, base_dir=tmp_path)


def test_export_workspace_profile_writes_loadable_selected_subtree(tmp_path):
    child_dir = tmp_path / "child"
    child_dir.mkdir()
    root = TerminalSession(pid=1, pty_fd=1, cwd=str(tmp_path), title="root")
    child = TerminalSession(pid=2, pty_fd=2, cwd=str(child_dir), title="child")
    root.children.append(child)
    profile_path = tmp_path / "workspace.yml"

    export_workspace_profile(profile_path, [root], selected_session=child)

    assert yaml.safe_load(profile_path.read_text(encoding="utf-8")) == {
        "version": 1,
        "root": {
            "title": "root",
            "workdir": str(tmp_path),
            "children": [
                {
                    "title": "child",
                    "workdir": str(child_dir),
                    "selected": True,
                }
            ],
        },
    }
    loaded = load_workspace_profile(profile_path)
    assert loaded.root.children[0].selected is True
    assert loaded.root.children[0].command is None


def test_export_workspace_profile_writes_all_roots(tmp_path):
    first = TerminalSession(pid=1, pty_fd=1, cwd=str(tmp_path), title="first")
    second = TerminalSession(pid=2, pty_fd=2, cwd=str(tmp_path), title="second")
    profile_path = tmp_path / "workspace.yml"

    export_workspace_profile(profile_path, [first, second], selected_session=second)

    exported = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    assert "root" not in exported
    assert exported["roots"] == [
        {"title": "first", "workdir": str(tmp_path)},
        {"title": "second", "workdir": str(tmp_path), "selected": True},
    ]
    assert len(load_workspace_profile(profile_path).roots) == 2


def test_export_workspace_profile_preserves_destination_on_replace_failure(tmp_path):
    profile_path = tmp_path / "workspace.yml"
    profile_path.write_text("existing content\n", encoding="utf-8")
    root = TerminalSession(pid=1, pty_fd=1, cwd=str(tmp_path), title="root")

    with (
        patch(
            "tree_style_terminal.config.workspace_profile.os.replace",
            side_effect=OSError("replace failed"),
        ),
        pytest.raises(WorkspaceProfileError, match="replace failed"),
    ):
        export_workspace_profile(profile_path, [root])

    assert profile_path.read_text(encoding="utf-8") == "existing content\n"
    assert list(tmp_path.glob(".workspace.yml.*.tmp")) == []
