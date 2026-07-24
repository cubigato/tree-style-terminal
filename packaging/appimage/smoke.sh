#!/bin/sh
set -eu

artifact="$(find /artifacts -maxdepth 1 -type f -name '*.AppImage' -print -quit)"
test -n "$artifact"

file "$artifact" | grep -q 'ELF 64-bit'
APPIMAGE_EXTRACT_AND_RUN=1 "$artifact" --help >/tmp/tst-appimage-help
grep -q 'Tree Style Terminal' /tmp/tst-appimage-help

smoke_dir="$(mktemp -d)"
weston_pid=""
cleanup() {
    if [ -n "$weston_pid" ]; then
        kill "$weston_pid" 2>/dev/null || true
        wait "$weston_pid" 2>/dev/null || true
    fi
    rm -rf "$smoke_dir"
}
trap cleanup EXIT
profile="$smoke_dir/workspace.yml"
environment_file="$smoke_dir/terminal-environment"
cwd_file="$smoke_dir/terminal-cwd"
shell_file="$smoke_dir/terminal-shell"

cat >"$profile" <<EOF
version: 1
roots:
  - title: AppImage smoke
    workdir: "$smoke_dir"
    command: >-
      env > "$environment_file";
      pwd > "$cwd_file";
      printf '%s\n' "\$0" > "$shell_file"
EOF

run_gui_smoke() {
    backend="$1"
    log_file="/tmp/tst-appimage-$backend.log"
    rm -f "$environment_file" "$cwd_file" "$shell_file"

    set +e
    if [ "$backend" = "x11" ]; then
        APPIMAGE_EXTRACT_AND_RUN=1 \
        HOME="$smoke_dir/home" \
        GI_TYPELIB_PATH="$smoke_dir/host-typelibs" \
        GIO_EXTRA_MODULES="$smoke_dir/host-gio-modules" \
        LANG=C.UTF-8 \
        LD_LIBRARY_PATH="$smoke_dir/host-libraries" \
        PATH=/usr/local/bin:/usr/bin:/bin \
        PYTHONPATH="$smoke_dir/host-python" \
        SHELL=/bin/sh \
        SSH_AUTH_SOCK="$smoke_dir/host-ssh-agent" \
        TST_SMOKE_HOST_VALUE=preserved \
        XDG_CACHE_HOME="$smoke_dir/host-cache" \
        XDG_CONFIG_HOME="$smoke_dir/config" \
        XDG_DATA_DIRS="$smoke_dir/host-data" \
        xvfb-run -a "$artifact" --profile "$profile" >"$log_file" 2>&1 &
    else
        APPIMAGE_EXTRACT_AND_RUN=1 \
        GDK_BACKEND=wayland \
        HOME="$smoke_dir/home" \
        GI_TYPELIB_PATH="$smoke_dir/host-typelibs" \
        GIO_EXTRA_MODULES="$smoke_dir/host-gio-modules" \
        LANG=C.UTF-8 \
        LD_LIBRARY_PATH="$smoke_dir/host-libraries" \
        PATH=/usr/local/bin:/usr/bin:/bin \
        PYTHONPATH="$smoke_dir/host-python" \
        SHELL=/bin/sh \
        SSH_AUTH_SOCK="$smoke_dir/host-ssh-agent" \
        TST_SMOKE_HOST_VALUE=preserved \
        WAYLAND_DISPLAY=tst-wayland \
        XDG_CACHE_HOME="$smoke_dir/host-cache" \
        XDG_CONFIG_HOME="$smoke_dir/config" \
        XDG_DATA_DIRS="$smoke_dir/host-data" \
        XDG_RUNTIME_DIR="$smoke_dir/wayland-runtime" \
        env -u DISPLAY "$artifact" --profile "$profile" >"$log_file" 2>&1 &
    fi
    app_pid=$!

    attempt=0
    while [ "$attempt" -lt 100 ] && [ ! -s "$environment_file" ]; do
        sleep 0.1
        attempt=$((attempt + 1))
    done

    kill "$app_pid" 2>/dev/null
    wait "$app_pid" 2>/dev/null
    set -e

    if [ ! -s "$environment_file" ]; then
        echo "The AppImage did not complete its $backend terminal smoke command:" >&2
        cat "$log_file" >&2
        exit 1
    fi
    if grep -q '^Fontconfig error:' "$log_file"; then
        echo "The AppImage reported a Fontconfig error under $backend:" >&2
        cat "$log_file" >&2
        exit 1
    fi
    test "$(cat "$cwd_file")" = "$smoke_dir"
    test "$(cat "$shell_file")" = "/bin/sh"
    grep -q '^TST_SMOKE_HOST_VALUE=preserved$' "$environment_file"
    grep -q "^SSH_AUTH_SOCK=$smoke_dir/host-ssh-agent$" "$environment_file"
    grep -q "^GI_TYPELIB_PATH=$smoke_dir/host-typelibs$" "$environment_file"
    grep -q "^GIO_EXTRA_MODULES=$smoke_dir/host-gio-modules$" "$environment_file"
    grep -q "^LD_LIBRARY_PATH=$smoke_dir/host-libraries$" "$environment_file"
    grep -q "^PYTHONPATH=$smoke_dir/host-python$" "$environment_file"
    grep -q "^XDG_CACHE_HOME=$smoke_dir/host-cache$" "$environment_file"
    grep -q "^XDG_DATA_DIRS=$smoke_dir/host-data$" "$environment_file"

    for variable in \
        APPDIR \
        APPIMAGE \
        APPIMAGE_EXTRACT_AND_RUN \
        ARGV0 \
        FONTCONFIG_FILE \
        FONTCONFIG_SYSROOT \
        GDK_PIXBUF_MODULE_FILE \
        GIO_MODULE_DIR \
        GIO_USE_VFS \
        GSETTINGS_SCHEMA_DIR \
        GTK_IM_MODULE_FILE \
        OWD \
        PYTHONHOME \
        TST_APPIMAGE
    do
        if grep -q "^${variable}=" "$environment_file"; then
            echo "Bundled runtime variable leaked into the host shell: $variable" >&2
            sort "$environment_file" >&2
            exit 1
        fi
    done
}

run_gui_smoke x11

mkdir -m 0700 "$smoke_dir/wayland-runtime"
XDG_RUNTIME_DIR="$smoke_dir/wayland-runtime" \
    weston \
    --backend=headless-backend.so \
    --idle-time=0 \
    --socket=tst-wayland \
    >"/tmp/tst-appimage-weston.log" 2>&1 &
weston_pid=$!

attempt=0
while [ "$attempt" -lt 100 ] && \
    [ ! -S "$smoke_dir/wayland-runtime/tst-wayland" ]; do
    sleep 0.1
    attempt=$((attempt + 1))
done
if [ ! -S "$smoke_dir/wayland-runtime/tst-wayland" ]; then
    echo "The headless Wayland compositor did not start:" >&2
    cat /tmp/tst-appimage-weston.log >&2
    exit 1
fi

run_gui_smoke wayland

echo "AppImage X11, Wayland, extract-and-run, and host-shell smoke checks passed."
