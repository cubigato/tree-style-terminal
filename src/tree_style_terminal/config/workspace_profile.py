"""
Workspace profile loading and validation.

Workspace profiles are self-contained YAML files used to create a startup
session tree. They are separate from the normal application config file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class WorkspaceProfileError(Exception):
    """Raised when a workspace profile file is invalid."""


@dataclass(frozen=True)
class WorkspaceNode:
    """A validated session node from a workspace profile."""

    title: str | None
    workdir: str
    command: str | None = None
    children: list[WorkspaceNode] = field(default_factory=list)


@dataclass(frozen=True)
class WorkspaceProfile:
    """A validated workspace profile."""

    path: Path
    version: int
    name: str | None
    root: WorkspaceNode


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

    root = raw_profile.get("root")
    if not isinstance(root, dict):
        raise WorkspaceProfileError("root must be a mapping")

    return WorkspaceProfile(
        path=profile_path,
        version=version,
        name=name,
        root=_parse_node(root, "root", inherited_workdir),
    )


def _parse_node(raw_node: dict[str, Any], path: str, inherited_workdir: Path) -> WorkspaceNode:
    title = _optional_string(raw_node, "title", path)
    command = _optional_string(raw_node, "command", path)
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
        children.append(_parse_node(child, child_path, workdir))

    return WorkspaceNode(
        title=title,
        workdir=str(workdir),
        command=command,
        children=children,
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
