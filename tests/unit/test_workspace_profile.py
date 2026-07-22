"""Workspace profile YAML loading and validation tests."""

import pytest

from tree_style_terminal.config.workspace_profile import (
    WorkspaceProfileError,
    load_workspace_profile,
)


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
