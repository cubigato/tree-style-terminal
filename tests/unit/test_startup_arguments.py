"""Startup argument parsing and activation tests."""

from unittest.mock import Mock, call, patch

import pytest

from tree_style_terminal.config.workspace_profile import WorkspaceNode, WorkspaceProfile
from tree_style_terminal.main import TreeStyleTerminalApp, parse_arguments


def test_parse_arguments_without_directory_requests_no_initial_cwd():
    args = parse_arguments([])

    assert args.initial_cwd is None


def test_parse_arguments_accepts_positional_directory(tmp_path):
    args = parse_arguments([str(tmp_path)])

    assert args.initial_cwd == str(tmp_path.resolve())


@pytest.mark.parametrize(
    "argv",
    [
        ["--working-directory", "{path}"],
        ["--working-directory={path}"],
        ["--workdir", "{path}"],
    ],
)
def test_parse_arguments_accepts_working_directory_options(tmp_path, argv):
    rendered_argv = [
        item.format(path=tmp_path)
        for item in argv
    ]

    args = parse_arguments(rendered_argv)

    assert args.initial_cwd == str(tmp_path.resolve())


def test_parse_arguments_resolves_relative_directory(tmp_path, monkeypatch):
    workdir = tmp_path / "project"
    workdir.mkdir()
    monkeypatch.chdir(tmp_path)

    args = parse_arguments(["project"])

    assert args.initial_cwd == str(workdir.resolve())


@pytest.mark.parametrize("path_factory", [lambda path: path / "missing", lambda path: path / "file.txt"])
def test_parse_arguments_rejects_invalid_directories(tmp_path, path_factory):
    path = path_factory(tmp_path)
    if path.suffix:
        path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        parse_arguments([str(path)])

    assert exc_info.value.code == 2


def test_parse_arguments_rejects_empty_working_directory():
    with pytest.raises(SystemExit) as exc_info:
        parse_arguments(["--working-directory="])

    assert exc_info.value.code == 2


def test_parse_arguments_rejects_positional_and_option_directory(tmp_path):
    other = tmp_path / "other"
    other.mkdir()

    with pytest.raises(SystemExit) as exc_info:
        parse_arguments([str(tmp_path), "--working-directory", str(other)])

    assert exc_info.value.code == 2


@pytest.mark.parametrize("argv", [["--profile", "{path}"], ["-p", "{path}"]])
def test_parse_arguments_accepts_profile_path(tmp_path, argv):
    profile_path = tmp_path / "workspace.yml"
    profile_path.write_text("version: 1\nroot: {}\n", encoding="utf-8")
    rendered_argv = [
        item.format(path=profile_path)
        for item in argv
    ]

    args = parse_arguments(rendered_argv)

    assert args.profile_path == str(profile_path.resolve())
    assert args.initial_cwd is None


def test_parse_arguments_rejects_missing_profile_path(tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        parse_arguments(["--profile", str(tmp_path / "missing.yml")])

    assert exc_info.value.code == 2


def test_parse_arguments_rejects_profile_and_startup_directory(tmp_path):
    profile_path = tmp_path / "workspace.yml"
    profile_path.write_text("version: 1\nroot: {}\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        parse_arguments(["--profile", str(profile_path), str(tmp_path)])

    assert exc_info.value.code == 2


def test_activation_without_initial_cwd_does_not_create_session():
    app = TreeStyleTerminalApp({"initial_cwd": None})
    window = Mock()

    with patch("tree_style_terminal.main.MainWindow", return_value=window):
        app._on_activate(app)

    window.session_manager.new_session.assert_not_called()
    window.show_all.assert_called_once_with()
    window.present.assert_called_once_with()


def test_activation_with_initial_cwd_creates_one_root_session(tmp_path):
    app = TreeStyleTerminalApp({"initial_cwd": str(tmp_path)})
    window = Mock()

    with patch("tree_style_terminal.main.MainWindow", return_value=window):
        app._on_activate(app)
        app._on_activate(app)

    window.session_manager.new_session.assert_called_once_with(cwd=str(tmp_path))


def test_activation_with_workspace_profile_creates_workspace_tree(tmp_path):
    root = WorkspaceNode(title="project", workdir=str(tmp_path))
    profile = WorkspaceProfile(
        path=tmp_path / "workspace.yml",
        version=1,
        name="Project",
        roots=[root],
    )
    app = TreeStyleTerminalApp({"initial_cwd": None, "workspace_profile": profile})
    window = Mock()

    with patch("tree_style_terminal.main.MainWindow", return_value=window):
        app._on_activate(app)
        app._on_activate(app)

    window.session_manager.create_workspace_tree.assert_called_once_with(root)
    window.session_manager.new_session.assert_not_called()


def test_activation_with_workspace_profile_creates_all_root_trees(tmp_path):
    roots = [
        WorkspaceNode(title="project", workdir=str(tmp_path)),
        WorkspaceNode(title="scratch", workdir=str(tmp_path)),
    ]
    profile = WorkspaceProfile(
        path=tmp_path / "workspace.yml",
        version=1,
        name="Project",
        roots=roots,
    )
    app = TreeStyleTerminalApp({"initial_cwd": None, "workspace_profile": profile})
    window = Mock()

    with patch("tree_style_terminal.main.MainWindow", return_value=window):
        app._on_activate(app)
        app._on_activate(app)

    assert window.session_manager.create_workspace_tree.call_args_list == [
        call(roots[0]),
        call(roots[1]),
    ]
    window.session_manager.new_session.assert_not_called()
