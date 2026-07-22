"""
Workspace profile loading and validation.

Workspace profiles are self-contained YAML files used to create a startup
session tree. They are separate from the normal application config file.
"""

from __future__ import annotations

import os
import tempfile
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ..models.session import TerminalSession


class WorkspaceProfileError(Exception):
    """Raised when a workspace profile file is invalid."""


@dataclass(frozen=True)
class WorkspaceNode:
    """A validated session node from a workspace profile."""

    title: str | None
    workdir: str
    command: str | None = None
    children: list[WorkspaceNode] = field(default_factory=list)
    selected: bool = False


@dataclass(frozen=True)
class WorkspaceProfile:
    """A validated workspace profile."""

    path: Path
    version: int
    name: str | None
    roots: list[WorkspaceNode]

    @property
    def root(self) -> WorkspaceNode:
        """Return the first root for compatibility with single-root callers."""
        return self.roots[0]


def load_workspace_profile(path: str | Path, base_dir: Path | None = None) -> WorkspaceProfile:
    """Load and validate a workspace profile YAML file."""
    profile_path = Path(path).expanduser()
    if not profile_path.is_absolute():
        profile_path = (base_dir or Path.cwd()) / profile_path

    profile_path = profile_path.resolve(strict=False)
    if not profile_path.is_file():
        raise WorkspaceProfileError(f"profile file does not exist: {profile_path}")

    try:
        with open(profile_path, encoding="utf-8") as profile_file:
            raw_profile = yaml.safe_load(profile_file) or {}
    except yaml.YAMLError as exc:
        raise WorkspaceProfileError(f"invalid YAML in profile file {profile_path}: {exc}") from exc
    except OSError as exc:
        raise WorkspaceProfileError(f"cannot read profile file {profile_path}: {exc}") from exc

    if not isinstance(raw_profile, dict):
        raise WorkspaceProfileError("profile must be a YAML mapping")

    version = _required_int(raw_profile, "version")
    if version != 1:
        raise WorkspaceProfileError(f"version must be 1, got {version}")

    name = _optional_string(raw_profile, "name")
    inherited_workdir = _resolve_workdir(
        _optional_string(raw_profile, "workdir"),
        Path.cwd() if base_dir is None else base_dir,
        "workdir",
    )

    roots = _parse_roots(raw_profile, inherited_workdir)

    return WorkspaceProfile(
        path=profile_path,
        version=version,
        name=name,
        roots=roots,
    )


def _parse_roots(
    raw_profile: dict[str, Any],
    inherited_workdir: Path,
) -> list[WorkspaceNode]:
    selected_paths: list[str] = []
    has_root = "root" in raw_profile
    has_roots = "roots" in raw_profile
    if has_root == has_roots:
        raise WorkspaceProfileError("profile must define exactly one of root or roots")

    if has_root:
        raw_root = raw_profile["root"]
        if not isinstance(raw_root, dict):
            raise WorkspaceProfileError("root must be a mapping")
        roots = [_parse_node(raw_root, "root", inherited_workdir, selected_paths)]
        _validate_selected_paths(selected_paths)
        return roots

    raw_roots = raw_profile["roots"]
    if not isinstance(raw_roots, list):
        raise WorkspaceProfileError("roots must be a list")
    if not raw_roots:
        raise WorkspaceProfileError("roots must contain at least one root")

    roots = []
    for index, raw_root in enumerate(raw_roots):
        root_path = f"roots[{index}]"
        if not isinstance(raw_root, dict):
            raise WorkspaceProfileError(f"{root_path} must be a mapping")
        roots.append(_parse_node(raw_root, root_path, inherited_workdir, selected_paths))
    _validate_selected_paths(selected_paths)
    return roots


def _parse_node(
    raw_node: dict[str, Any],
    path: str,
    inherited_workdir: Path,
    selected_paths: list[str],
) -> WorkspaceNode:
    title = _optional_string(raw_node, "title", path)
    command = _optional_string(raw_node, "command", path)
    selected = _optional_bool(raw_node, "selected", path)
    if selected:
        selected_paths.append(f"{path}.selected")
    workdir = _resolve_workdir(
        _optional_string(raw_node, "workdir", path),
        inherited_workdir,
        f"{path}.workdir",
    )

    raw_children = raw_node.get("children", [])
    if raw_children is None:
        raw_children = []
    if not isinstance(raw_children, list):
        raise WorkspaceProfileError(f"{path}.children must be a list")

    children = []
    for index, child in enumerate(raw_children):
        child_path = f"{path}.children[{index}]"
        if not isinstance(child, dict):
            raise WorkspaceProfileError(f"{child_path} must be a mapping")
        children.append(_parse_node(child, child_path, workdir, selected_paths))

    return WorkspaceNode(
        title=title,
        workdir=str(workdir),
        command=command,
        selected=selected,
        children=children,
    )


def _validate_selected_paths(selected_paths: list[str]) -> None:
    if len(selected_paths) > 1:
        raise WorkspaceProfileError(
            f"{selected_paths[1]} cannot be true because "
            f"{selected_paths[0]} is already true"
        )


def _required_int(raw_profile: dict[str, Any], key: str) -> int:
    value = raw_profile.get(key)
    if not isinstance(value, int):
        raise WorkspaceProfileError(f"{key} must be an integer")
    return value


def _optional_string(raw_mapping: dict[str, Any], key: str, path: str | None = None) -> str | None:
    value = raw_mapping.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        field_path = f"{path}.{key}" if path else key
        raise WorkspaceProfileError(f"{field_path} must be a string")
    return value


def _optional_bool(raw_mapping: dict[str, Any], key: str, path: str) -> bool:
    if key not in raw_mapping:
        return False
    value = raw_mapping[key]
    if not isinstance(value, bool):
        raise WorkspaceProfileError(f"{path}.{key} must be a boolean")
    return value


def _resolve_workdir(value: str | None, inherited_workdir: Path, path: str) -> Path:
    if value is None:
        candidate = inherited_workdir
    else:
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = inherited_workdir / candidate

    resolved = candidate.resolve(strict=False)
    if not resolved.is_dir():
        raise WorkspaceProfileError(f"{path} points to a missing directory: {value or resolved}")
    return resolved


def export_workspace_profile(
    path: str | Path,
    roots: list[TerminalSession],
    selected_session: TerminalSession | None = None,
) -> None:
    """Atomically export live session trees as a version 1 workspace profile."""
    if not roots:
        raise WorkspaceProfileError("cannot export a profile without a root session")

    serialized_roots = [
        _serialize_session_node(root, selected_session)
        for root in roots
    ]
    profile_data: dict[str, Any] = {"version": 1}
    if len(serialized_roots) == 1:
        profile_data["root"] = serialized_roots[0]
    else:
        profile_data["roots"] = serialized_roots

    destination = Path(path).expanduser()
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            yaml.safe_dump(
                profile_data,
                temporary_file,
                allow_unicode=True,
                sort_keys=False,
            )
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, destination)
    except (OSError, yaml.YAMLError) as exc:
        if temporary_path is not None:
            with suppress(OSError):
                temporary_path.unlink(missing_ok=True)
        raise WorkspaceProfileError(
            f"cannot write workspace profile {destination}: {exc}"
        ) from exc


def _serialize_session_node(
    session: TerminalSession,
    selected_session: TerminalSession | None,
) -> dict[str, Any]:
    node: dict[str, Any] = {}
    if session.title is not None:
        node["title"] = session.title
    node["workdir"] = session.cwd
    if session is selected_session:
        node["selected"] = True
    if session.children:
        node["children"] = [
            _serialize_session_node(child, selected_session)
            for child in session.children
        ]
    return node
