"""Tests for application-to-terminal environment boundaries."""

from tree_style_terminal.runtime_environment import build_terminal_environment


def test_native_terminal_environment_is_preserved():
    source = {
        "HOME": "/home/tester",
        "LD_LIBRARY_PATH": "/opt/native/lib",
        "PATH": "/custom/bin:/usr/bin",
        "PYTHONPATH": "/work/python",
        "SHELL": "/bin/zsh",
    }

    assert build_terminal_environment(source) == {
        **source,
        "TERM": "xterm-256color",
    }


def test_appimage_terminal_environment_removes_bundle_runtime():
    appdir = "/tmp/.mount_TreeStyle"
    source = {
        "APPDIR": appdir,
        "APPIMAGE": "/downloads/TreeStyleTerminal.AppImage",
        "APPIMAGE_EXTRACT_AND_RUN": "1",
        "ARGV0": "./TreeStyleTerminal.AppImage",
        "OWD": "/home/tester/project",
        "TST_APPIMAGE": "1",
        "TST_APPIMAGE_CACHE": "/run/user/1000/tst",
        "LD_LIBRARY_PATH": f"{appdir}/usr/lib",
        "TST_APPIMAGE_HOST_LD_LIBRARY_PATH": "/opt/host/lib",
        "PYTHONHOME": f"{appdir}/usr",
        "PYTHONPATH": f"{appdir}/usr/lib/python3/dist-packages",
        "TST_APPIMAGE_HOST_PYTHONPATH": "/work/python",
        "GI_TYPELIB_PATH": f"{appdir}/usr/lib/girepository-1.0",
        "GIO_EXTRA_MODULES": f"{appdir}/usr/lib/gio/modules",
        "GIO_MODULE_DIR": f"{appdir}/usr/lib/gio/modules",
        "GIO_USE_VFS": "local",
        "GSETTINGS_SCHEMA_DIR": f"{appdir}/usr/share/glib-2.0/schemas",
        "FONTCONFIG_FILE": f"{appdir}/etc/fonts/fontconfig-appimage.conf",
        "GDK_PIXBUF_MODULE_FILE": "/run/user/1000/tst/gdk-loaders.cache",
        "GTK_IM_MODULE_FILE": "/run/user/1000/tst/immodules.cache",
        "XDG_DATA_DIRS": f"{appdir}/usr/share",
        "TST_APPIMAGE_HOST_XDG_DATA_DIRS": "/usr/local/share:/usr/share",
        "XDG_CACHE_HOME": "/run/user/1000/tst/cache",
        "TST_APPIMAGE_HOST_XDG_CACHE_HOME": "/home/tester/.cache",
        "SSL_CERT_FILE": f"{appdir}/etc/ssl/certs/ca-certificates.crt",
        "PATH": "/home/tester/bin:/usr/bin",
        "LANG": "de_DE.UTF-8",
        "SHELL": "/bin/zsh",
        "SSH_AUTH_SOCK": "/run/user/1000/ssh-agent",
        "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
        "TERM": "screen-256color",
    }

    environment = build_terminal_environment(source)

    assert environment == {
        "LD_LIBRARY_PATH": "/opt/host/lib",
        "PYTHONPATH": "/work/python",
        "XDG_DATA_DIRS": "/usr/local/share:/usr/share",
        "XDG_CACHE_HOME": "/home/tester/.cache",
        "PATH": "/home/tester/bin:/usr/bin",
        "LANG": "de_DE.UTF-8",
        "SHELL": "/bin/zsh",
        "SSH_AUTH_SOCK": "/run/user/1000/ssh-agent",
        "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
        "TERM": "screen-256color",
    }


def test_appimage_detection_requires_explicit_apprun_marker():
    source = {
        "APPDIR": "/tmp/unrelated",
        "LD_LIBRARY_PATH": "/tmp/unrelated/usr/lib",
    }

    assert build_terminal_environment(source) == {
        **source,
        "TERM": "xterm-256color",
    }


def test_explicitly_empty_host_value_is_restored():
    source = {
        "APPDIR": "/tmp/.mount_TreeStyle",
        "TST_APPIMAGE": "1",
        "LD_LIBRARY_PATH": "/tmp/.mount_TreeStyle/usr/lib",
        "TST_APPIMAGE_HOST_LD_LIBRARY_PATH": "",
    }

    assert build_terminal_environment(source)["LD_LIBRARY_PATH"] == ""
