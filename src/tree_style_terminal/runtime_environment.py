"""Runtime environment boundaries for processes launched inside terminals."""

from __future__ import annotations

import os
from collections.abc import Mapping

APPIMAGE_RUNTIME_VARIABLES = {
    "APPIMAGE",
    "APPDIR",
    "ARGV0",
    "OWD",
    "APPIMAGE_EXTRACT_AND_RUN",
    "TST_APPIMAGE",
}

APPIMAGE_PATH_VARIABLES = {
    "GI_TYPELIB_PATH",
    "GIO_EXTRA_MODULES",
    "GTK_PATH",
    "LD_LIBRARY_PATH",
    "PYTHONPATH",
    "XDG_DATA_DIRS",
}

APPIMAGE_PRIVATE_VARIABLES = {
    "FONTCONFIG_FILE",
    "FONTCONFIG_SYSROOT",
    "GDK_PIXBUF_MODULE_FILE",
    "GIO_MODULE_DIR",
    "GSETTINGS_SCHEMA_DIR",
    "GIO_USE_VFS",
    "GTK_IM_MODULE_FILE",
    "PYTHONHOME",
    "XDG_CACHE_HOME",
}
APPIMAGE_HOST_VARIABLE_PREFIX = "TST_APPIMAGE_HOST_"


def is_appimage_environment(environment: Mapping[str, str]) -> bool:
    """Return whether the application is running through its AppImage AppRun."""
    return environment.get("TST_APPIMAGE") == "1" and bool(
        environment.get("APPDIR")
    )


def build_terminal_environment(
    source: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Build the environment inherited by a shell or workspace command."""
    environment = dict(os.environ if source is None else source)
    if is_appimage_environment(environment):
        _remove_appimage_runtime(environment)

    environment.setdefault("TERM", "xterm-256color")
    return environment


def _remove_appimage_runtime(environment: dict[str, str]) -> None:
    appdir = environment["APPDIR"]

    overridden_variables = APPIMAGE_PATH_VARIABLES | APPIMAGE_PRIVATE_VARIABLES
    for name in overridden_variables:
        host_name = f"{APPIMAGE_HOST_VARIABLE_PREFIX}{name}"
        if host_name in environment:
            environment[name] = environment[host_name]
        else:
            environment.pop(name, None)

    for name in APPIMAGE_RUNTIME_VARIABLES:
        environment.pop(name, None)

    ssl_cert_file = environment.get("SSL_CERT_FILE")
    if ssl_cert_file and _is_bundled_path(ssl_cert_file, appdir):
        environment.pop("SSL_CERT_FILE")

    for name in list(environment):
        if name.startswith("TST_APPIMAGE_"):
            environment.pop(name)


def _is_bundled_path(value: str, appdir: str) -> bool:
    if not value or not os.path.isabs(value):
        return False

    normalized_value = os.path.normpath(value)
    normalized_appdir = os.path.normpath(appdir)
    try:
        return os.path.commonpath((normalized_value, normalized_appdir)) == (
            normalized_appdir
        )
    except ValueError:
        return False
