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

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
project_root="$(CDPATH= cd -- "$script_dir/../.." && pwd)"
output_dir="$project_root/build/debian"
containerfile="$script_dir/Containerfile"
podman="${PODMAN:-podman}"
image="${DEB_IMAGE:-localhost/tree-style-terminal-deb-builder:debian-13}"

if ! command -v "$podman" >/dev/null 2>&1; then
    echo "Podman is required to build the Debian package." >&2
    exit 1
fi

mkdir -p "$output_dir"

"$podman" build \
    --tag "$image" \
    --file "$containerfile" \
    "$project_root"

"$podman" run \
    --rm \
    --network none \
    --security-opt label=disable \
    --volume "$project_root:/workspace:ro" \
    --volume "$output_dir:/output:rw" \
    "$image" \
    "$mode"
