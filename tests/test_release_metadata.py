"""Consistency tests for shared Linux release metadata."""

from __future__ import annotations

import configparser
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

from tree_style_terminal import APPLICATION_ID, __version__

PROJECT_ROOT = Path(__file__).parents[1]
DESKTOP_FILE = PROJECT_ROOT / "data" / f"{APPLICATION_ID}.desktop"
METAINFO_FILE = PROJECT_ROOT / "data" / f"{APPLICATION_ID}.metainfo.xml"
SCALABLE_ICON = (
    PROJECT_ROOT
    / "data"
    / "icons"
    / "hicolor"
    / "scalable"
    / "apps"
    / f"{APPLICATION_ID}.svg"
)
PNG_ICON = (
    PROJECT_ROOT
    / "data"
    / "icons"
    / "hicolor"
    / "512x512"
    / "apps"
    / f"{APPLICATION_ID}.png"
)


def _desktop_entry() -> configparser.SectionProxy:
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str
    parser.read(DESKTOP_FILE, encoding="utf-8")
    return parser["Desktop Entry"]


def _metainfo_root() -> ET.Element:
    return ET.parse(METAINFO_FILE).getroot()


def test_runtime_and_desktop_identity_are_permanent():
    desktop = _desktop_entry()
    metainfo = _metainfo_root()

    assert APPLICATION_ID == "de.cubigato.treestyleterminal"
    assert DESKTOP_FILE.stem == APPLICATION_ID
    assert desktop["Icon"] == APPLICATION_ID
    assert metainfo.findtext("id") == APPLICATION_ID
    assert metainfo.findtext("launchable") == f"{APPLICATION_ID}.desktop"
    assert SCALABLE_ICON.stem == APPLICATION_ID
    assert SCALABLE_ICON.is_file()
    assert PNG_ICON.is_file()


def test_version_has_one_authoritative_python_source():
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)

    assert pyproject["project"]["dynamic"] == ["version"]
    assert (
        pyproject["tool"]["setuptools"]["dynamic"]["version"]["attr"]
        == "tree_style_terminal._version.__version__"
    )
    latest_release = _metainfo_root().find("releases/release")
    assert latest_release is not None
    assert latest_release.attrib["version"] == __version__


def test_desktop_entry_uses_normal_exec_launch_and_both_commands_are_declared():
    desktop = _desktop_entry()
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        scripts = tomllib.load(pyproject_file)["project"]["scripts"]

    assert desktop["Exec"] == "tree-style-terminal"
    assert desktop["TryExec"] == "tree-style-terminal"
    assert desktop.get("DBusActivatable") is None
    assert scripts == {
        "tree-style-terminal": "tree_style_terminal.main:main",
        "tst": "tree_style_terminal.main:main",
    }


def test_metainfo_references_the_shared_screenshot_and_licenses():
    metainfo = _metainfo_root()
    screenshot = PROJECT_ROOT / "assets" / "screenshots" / "tree-style-terminal.png"

    assert metainfo.findtext("metadata_license") == "CC0-1.0"
    assert metainfo.findtext("project_license") == "Apache-2.0"
    assert screenshot.is_file()
    assert metainfo.findtext("screenshots/screenshot/image").endswith(
        "/assets/screenshots/tree-style-terminal.png"
    )
