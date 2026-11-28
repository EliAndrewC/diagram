#!/usr/bin/env bash
# install-onnxruntime.sh - the ONNX Runtime the embedder crate (`rust/embed/`, feature 449 T138) loads, pinned by `onnxruntime.pin`
# beside this script: Microsoft's release archive downloaded once from the project's GitHub releases into
# ~/.cache/l7r-onnxruntime/<version>/, its SHA-256 checked. setup-dev-env.sh runs it; it runs alone too, and is idempotent.
#
# WHY A PINNED RELEASE, NOT ORT'S BUILD-TIME DOWNLOAD OR THE PYTHON WHEEL'S COPY (feature 449 T138, `ask:449-phase4-slices` Q11: the same
# BGE-M3 weights through the same kind of runtime): the `ort` crate the toolchain here builds (2.0.0-rc.10; rc.11 and later want a newer
# Rust than 1.87) downloads ONNX Runtime 1.22 of its own when it links statically, a different runtime from the 1.31.1 the Python ran;
# the wheel's `libonnxruntime.so` leaves with the Python. The crate loads this library at run time (`load-dynamic`), so no cargo build,
# test or coverage run needs it, and only `l7r-embed serve` opens it. Where Microsoft's archive does not download (its repository
# answered 404 on 2026-11-28), the same version's PyPI wheel is the fallback, its library extracted to the same path (the pin's FALLBACK).
set -euo pipefail
HERE=$(cd "${BASH_SOURCE[0]%/*}" && pwd)
# shellcheck source=onnxruntime.pin
. "$HERE/onnxruntime.pin"
V=$ONNXRUNTIME_VERSION
DEST="${L7R_ONNXRUNTIME_HOME:-$HOME/.cache/l7r-onnxruntime}/$V"
LIB="$DEST/onnxruntime-linux-x64-$V/lib/libonnxruntime.so.$V"

if [ ! -f "$LIB" ]; then
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    mkdir -p "$DEST"
    if curl -sSfL -o "$tmp/ort.tgz" \
        "https://github.com/microsoft/onnxruntime/releases/download/v$V/onnxruntime-linux-x64-$V.tgz"; then
        got=$(sha256sum "$tmp/ort.tgz" | cut -d' ' -f1)
        if [ "$got" != "$ONNXRUNTIME_SHA256" ]; then
            echo "install-onnxruntime: the download's SHA-256 is $got, not the pinned $ONNXRUNTIME_SHA256 - check onnxruntime.pin" >&2
            exit 1
        fi
        # the library alone: the headers and the CMake files are for a C build, which nothing here does
        tar -xzf "$tmp/ort.tgz" -C "$DEST" --no-same-owner --no-same-permissions "onnxruntime-linux-x64-$V/lib/libonnxruntime.so.$V"
    else
        # Microsoft's release unreachable (onnxruntime.pin's FALLBACK): the same version's PyPI wheel, its library alone
        echo "install-onnxruntime: Microsoft's release archive did not download; using PyPI's $V wheel (onnxruntime.pin)" >&2
        curl -sSfL -o "$tmp/ort.whl" "$ONNXRUNTIME_WHEEL_URL"
        got=$(sha256sum "$tmp/ort.whl" | cut -d' ' -f1)
        if [ "$got" != "$ONNXRUNTIME_WHEEL_SHA256" ]; then
            echo "install-onnxruntime: the wheel's SHA-256 is $got, not the pinned $ONNXRUNTIME_WHEEL_SHA256 - check onnxruntime.pin" >&2
            exit 1
        fi
        mkdir -p "$(dirname "$LIB")"
        python3 -I -c 'import sys, zipfile; open(sys.argv[3], "wb").write(zipfile.ZipFile(sys.argv[1]).read(sys.argv[2]))' \
            "$tmp/ort.whl" "onnxruntime/capi/libonnxruntime.so.$V" "$LIB"
    fi
fi
# the proof it is the pinned build: the library names its version
grep -aq "$V" "$LIB" || { echo "install-onnxruntime: $LIB does not name $V" >&2; exit 1; }
