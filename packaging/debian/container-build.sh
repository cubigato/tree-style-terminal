#!/bin/sh
set -eu

mode="${1:-package}"
case "$mode" in
    package | check) ;;
    *)
        echo "Usage: $0 [package|check]" >&2
        exit 2
        ;;
esac

work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT

source_dir="$work_dir/source"
mkdir -p "$source_dir"

tar \
    --exclude=.git \
    --exclude=.venv \
    --exclude=build \
    --exclude='*.egg-info' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude=.pytest_cache \
    -C /workspace \
    -cf - \
    . |
    tar -C "$source_dir" -xf -

cd "$source_dir"
dpkg-buildpackage --build=binary --unsigned-changes

changes_file="$(find "$work_dir" -maxdepth 1 -type f -name '*.changes' -print -quit)"
package_file="$(find "$work_dir" -maxdepth 1 -type f -name '*.deb' -print -quit)"

test -n "$changes_file"
test -n "$package_file"

lintian --fail-on error,warning "$changes_file"

if [ "$mode" = "check" ]; then
    package_name="$(dpkg-deb --field "$package_file" Package)"
    config_root="$work_dir/config"
    config_file="$config_root/tree-style-terminal/config.yaml"

    apt-get install -y "$package_file"
    "$source_dir/debian/tests/smoke"

    mkdir -p "$(dirname "$config_file")"
    printf '%s\n' '# package-manager-preservation-check' >"$config_file"
    config_checksum="$(sha256sum "$config_file")"

    XDG_CONFIG_HOME="$config_root" apt-get install -y --reinstall "$package_file"
    test "$(sha256sum "$config_file")" = "$config_checksum"

    XDG_CONFIG_HOME="$config_root" apt-get remove -y "$package_name"
    test "$(sha256sum "$config_file")" = "$config_checksum"
fi

cp "$package_file" /output/
echo "Debian package: /output/$(basename "$package_file")"
