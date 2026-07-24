#!/bin/sh
set -eu

work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT

source_dir="$work_dir/source"
appdir="$work_dir/TreeStyleTerminal.AppDir"
multiarch="$(dpkg-architecture -qDEB_HOST_MULTIARCH)"
gdk_pixbuf_query="/usr/lib/$multiarch/gdk-pixbuf-2.0/gdk-pixbuf-query-loaders"
gtk_query_immodules="/usr/lib/$multiarch/libgtk-3-0/gtk-query-immodules-3.0"

if [ "$(dpkg --print-architecture)" != "amd64" ]; then
    echo "The current AppImage recipe supports amd64/x86_64 only." >&2
    exit 1
fi

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

version="$(
    sed -n 's/^__version__ = "\([^"]*\)"$/\1/p' \
        "$source_dir/src/tree_style_terminal/_version.py"
)"
case "$version" in
    '' | *[!0-9A-Za-z.+~-]*)
        echo "Could not read a safe application version." >&2
        exit 1
        ;;
esac

artifact_name="TreeStyleTerminal-${version}-x86_64.AppImage"
checksum_name="${artifact_name}.sha256"
inventory_name="TreeStyleTerminal-${version}-x86_64.third-party-licenses.txt"
artifact="$work_dir/$artifact_name"
package_list="$work_dir/runtime-packages"
: >"$package_list"

record_package() {
    package="$(
        dpkg-query --search "$1" 2>/dev/null |
            sed -n '1s/: .*//p' |
            sed 's/:.*//'
    )"
    if [ -n "$package" ]; then
        printf '%s\n' "$package" >>"$package_list"
    fi
}

mkdir -p \
    "$appdir/etc/fonts" \
    "$appdir/etc/ssl/certs" \
    "$appdir/usr/bin" \
    "$appdir/usr/lib/python3/dist-packages" \
    "$appdir/usr/lib/$multiarch" \
    "$appdir/usr/share/applications" \
    "$appdir/usr/share/doc/tree-style-terminal" \
    "$appdir/usr/share/icons/hicolor/512x512/apps" \
    "$appdir/usr/share/icons/hicolor/scalable/apps" \
    "$appdir/usr/share/metainfo"

install -m 0755 /usr/bin/python3.11 "$appdir/usr/bin/python3.11"
ln -s python3.11 "$appdir/usr/bin/python3"
ln -s ../../AppRun "$appdir/usr/bin/tree-style-terminal"
ln -s tree-style-terminal "$appdir/usr/bin/tst"
cp -a /usr/lib/python3.11 "$appdir/usr/lib/"
cp -a /usr/lib/python3/dist-packages/gi "$appdir/usr/lib/python3/dist-packages/"
cp -a /usr/lib/python3/dist-packages/yaml "$appdir/usr/lib/python3/dist-packages/"
cp -a \
    "$source_dir/src/tree_style_terminal" \
    "$appdir/usr/lib/python3/dist-packages/"

for package in \
    libpython3.11-minimal \
    libpython3.11-stdlib \
    python3-gi \
    python3-yaml \
    python3.11 \
    python3.11-minimal
do
    printf '%s\n' "$package" >>"$package_list"
done

cp -a "/usr/lib/$multiarch/girepository-1.0" "$appdir/usr/lib/$multiarch/"
cp -a "/usr/lib/$multiarch/gdk-pixbuf-2.0" "$appdir/usr/lib/$multiarch/"
cp -a "/usr/lib/$multiarch/gio" "$appdir/usr/lib/$multiarch/"
cp -a "/usr/lib/$multiarch/gtk-3.0" "$appdir/usr/lib/$multiarch/"
rm -f \
    "$appdir/usr/lib/$multiarch/gdk-pixbuf-2.0/2.10.0/loaders.cache" \
    "$appdir/usr/lib/$multiarch/gtk-3.0/3.0.0/immodules.cache"
gio-querymodules "$appdir/usr/lib/$multiarch/gio/modules"

for data_dir in glib-2.0 icons mime themes; do
    if [ -d "/usr/share/$data_dir" ]; then
        cp -a "/usr/share/$data_dir" "$appdir/usr/share/"
    fi
done
glib-compile-schemas "$appdir/usr/share/glib-2.0/schemas"

cp -a /etc/fonts/. "$appdir/etc/fonts/"
install -m 0644 \
    "$source_dir/packaging/appimage/fontconfig-appimage.conf" \
    "$appdir/etc/fonts/fontconfig-appimage.conf"
cp -a /usr/share/fontconfig "$appdir/usr/share/"
mkdir -p "$appdir/usr/share/fonts/truetype"
cp -a /usr/share/fonts/truetype/dejavu "$appdir/usr/share/fonts/truetype/"

for package in \
    adwaita-icon-theme \
    fontconfig-config \
    fonts-dejavu-core \
    gir1.2-gtk-3.0 \
    gir1.2-vte-2.91 \
    hicolor-icon-theme \
    libgdk-pixbuf2.0-common \
    libglib2.0-data \
    libgtk-3-common \
    shared-mime-info
do
    printf '%s\n' "$package" >>"$package_list"
done

install -m 0755 \
    "$gdk_pixbuf_query" \
    "$appdir/usr/bin/gdk-pixbuf-query-loaders"
install -m 0755 \
    "$gtk_query_immodules" \
    "$appdir/usr/bin/gtk-query-immodules-3.0"
install -m 0644 \
    /etc/ssl/certs/ca-certificates.crt \
    "$appdir/etc/ssl/certs/ca-certificates.crt"

install -m 0755 "$source_dir/packaging/appimage/AppRun" "$appdir/AppRun"
install -m 0644 \
    "$source_dir/data/de.cubigato.treestyleterminal.desktop" \
    "$appdir/usr/share/applications/de.cubigato.treestyleterminal.desktop"
sed -i '/^TryExec=/d' \
    "$appdir/usr/share/applications/de.cubigato.treestyleterminal.desktop"
install -m 0644 \
    "$source_dir/data/de.cubigato.treestyleterminal.metainfo.xml" \
    "$appdir/usr/share/metainfo/de.cubigato.treestyleterminal.metainfo.xml"
ln -s \
    de.cubigato.treestyleterminal.metainfo.xml \
    "$appdir/usr/share/metainfo/de.cubigato.treestyleterminal.appdata.xml"
install -m 0644 \
    "$source_dir/data/icons/hicolor/512x512/apps/de.cubigato.treestyleterminal.png" \
    "$appdir/usr/share/icons/hicolor/512x512/apps/de.cubigato.treestyleterminal.png"
install -m 0644 \
    "$source_dir/data/icons/hicolor/scalable/apps/de.cubigato.treestyleterminal.svg" \
    "$appdir/usr/share/icons/hicolor/scalable/apps/de.cubigato.treestyleterminal.svg"
install -m 0644 "$source_dir/LICENSE" "$appdir/usr/share/doc/tree-style-terminal/LICENSE"
install -m 0644 \
    /usr/share/common-licenses/CC0-1.0 \
    "$appdir/usr/share/doc/tree-style-terminal/CC0-1.0"
install -m 0644 \
    /opt/runtime-x86_64.LICENSE \
    "$appdir/usr/share/doc/tree-style-terminal/AppImage-runtime.LICENSE"

ln -s \
    usr/share/applications/de.cubigato.treestyleterminal.desktop \
    "$appdir/de.cubigato.treestyleterminal.desktop"
ln -s \
    usr/share/icons/hicolor/512x512/apps/de.cubigato.treestyleterminal.png \
    "$appdir/de.cubigato.treestyleterminal.png"
ln -s \
    usr/share/icons/hicolor/scalable/apps/de.cubigato.treestyleterminal.svg \
    "$appdir/de.cubigato.treestyleterminal.svg"

is_host_runtime_library() {
    case "$(basename "$1")" in
        ld-linux-x86-64.so.2 | \
        libc.so.6 | \
        libdl.so.2 | \
        libm.so.6 | \
        libpthread.so.0 | \
        libresolv.so.2 | \
        librt.so.1 | \
        libutil.so.1)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

copy_dependencies() {
    root="$(readlink -f "$1")"
    record_package "$root"
    lddtree -l "$root" |
        while IFS= read -r dependency; do
            dependency_name="$(basename "$dependency")"
            dependency="$(readlink -f "$dependency")"
            if [ "$dependency" = "$root" ] || is_host_runtime_library "$dependency"; then
                continue
            fi
            install -m 0644 \
                "$dependency" \
                "$appdir/usr/lib/$multiarch/$dependency_name"
            record_package "$dependency"
        done
}

copy_library() {
    library="$(readlink -f "$1")"
    install -m 0644 \
        "$library" \
        "$appdir/usr/lib/$multiarch/$(basename "$1")"
    record_package "$library"
    copy_dependencies "$library"
}

copy_dependencies /usr/bin/python3.11
copy_dependencies "$gdk_pixbuf_query"
copy_dependencies "$gtk_query_immodules"

copy_library "$(ldconfig -p | awk '/libgtk-3[.]so[.]0/{print $NF; exit}')"
copy_library "$(ldconfig -p | awk '/libvte-2[.]91[.]so[.]0/{print $NF; exit}')"

find \
    /usr/lib/python3.11/lib-dynload \
    /usr/lib/python3/dist-packages/gi \
    /usr/lib/python3/dist-packages/yaml \
    "/usr/lib/$multiarch/gdk-pixbuf-2.0" \
    "/usr/lib/$multiarch/gio/modules" \
    "/usr/lib/$multiarch/gtk-3.0/3.0.0/immodules" \
    -type f -name '*.so' -print |
    while IFS= read -r module; do
        copy_dependencies "$module"
    done

desktop-file-validate \
    "$appdir/usr/share/applications/de.cubigato.treestyleterminal.desktop"
appstreamcli validate --no-net \
    "$appdir/usr/share/metainfo/de.cubigato.treestyleterminal.metainfo.xml"

printf '%s\n' ca-certificates librsvg2-common >>"$package_list"
sort -u "$package_list" -o "$package_list"

third_party_dir="$appdir/usr/share/doc/tree-style-terminal/third-party"
mkdir -p "$third_party_dir"
inventory="$appdir/usr/share/doc/tree-style-terminal/THIRD_PARTY_LICENSES.txt"
{
    echo "Tree Style Terminal AppImage bundled component inventory"
    echo
    echo "Build baseline: Debian 12 (bookworm), snapshot 2026-07-01"
    echo "CPU architecture: x86_64"
    echo
    echo "AppImage type 2 runtime:"
    echo "  commit: 75849dce7cc37e4319b633df1f116ca895c71a12"
    echo "  sha256: 1cc49bcf1e2ccd593c379adb17c9f85a36d619088296504de95b1d06215aebbf"
    echo "  license: usr/share/doc/tree-style-terminal/AppImage-runtime.LICENSE"
    echo
    echo "Bundled Debian runtime packages:"
} >"$inventory"

while IFS= read -r package; do
    version_string="$(dpkg-query --show --showformat='${Version}' "$package")"
    package_doc_dir="$third_party_dir/$package"
    mkdir -p "$package_doc_dir"
    if [ -e "/usr/share/doc/$package/copyright" ]; then
        cp -L \
            "/usr/share/doc/$package/copyright" \
            "$package_doc_dir/copyright"
        license_path="usr/share/doc/tree-style-terminal/third-party/$package/copyright"
    else
        license_path="not present in the binary package"
    fi
    printf '  %s %s — %s\n' "$package" "$version_string" "$license_path" \
        >>"$inventory"
done <"$package_list"

cp "$inventory" "$work_dir/$inventory_name"

source_date_epoch="${SOURCE_DATE_EPOCH:-}"
if [ -z "$source_date_epoch" ] && [ -d /workspace/.git ]; then
    source_date_epoch="$(git -C /workspace log -1 --format=%ct 2>/dev/null || true)"
fi
if [ -z "$source_date_epoch" ]; then
    source_date_epoch=1735689600
fi
export SOURCE_DATE_EPOCH="$source_date_epoch"
export ARCH=x86_64
export VERSION="$version"

appimagetool \
    --no-appstream \
    --runtime-file /opt/runtime-x86_64 \
    "$appdir" \
    "$artifact"

cd "$work_dir"
sha256sum "$artifact_name" >"$checksum_name"

rm -f \
    "/output/$artifact_name" \
    "/output/$checksum_name" \
    "/output/$inventory_name"
install -m 0755 "$artifact" "/output/$artifact_name"
install -m 0644 "$checksum_name" "/output/$checksum_name"
install -m 0644 "$inventory_name" "/output/$inventory_name"

echo "AppImage: /output/$artifact_name"
echo "Checksum: /output/$checksum_name"
echo "License inventory: /output/$inventory_name"
