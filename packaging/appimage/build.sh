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
output_dir="$project_root/build/appimage"
podman="${PODMAN:-podman}"
builder_image="${APPIMAGE_BUILD_IMAGE:-localhost/tree-style-terminal-appimage-builder:debian-12}"
smoke_image="${APPIMAGE_SMOKE_IMAGE:-localhost/tree-style-terminal-appimage-smoke:debian-12}"

if ! command -v "$podman" >/dev/null 2>&1; then
    echo "Podman is required to build the AppImage." >&2
    exit 1
fi

if [ "$(uname -m)" != "x86_64" ]; then
    echo "The current AppImage recipe supports x86_64 hosts only." >&2
    exit 1
fi

mkdir -p "$output_dir"

"$podman" build \
    --tag "$builder_image" \
    --file "$script_dir/Containerfile" \
    "$project_root"

"$podman" run \
    --rm \
    --network none \
    --security-opt label=disable \
    --volume "$project_root:/workspace:ro" \
    --volume "$output_dir:/output:rw" \
    "$builder_image"

if [ "$mode" = "check" ]; then
    "$podman" build \
        --tag "$smoke_image" \
        --file "$script_dir/Containerfile.smoke" \
        "$project_root"

    "$podman" run \
        --rm \
        --network none \
        --security-opt label=disable \
        --volume "$output_dir:/artifacts:ro" \
        "$smoke_image"
fi
