#!/usr/bin/env bash
# install-chromium.sh - the headless Chromium the browser crate (`rust/browser/`, feature 449 T146) drives, pinned by
# `chromium.pin` beside this script: downloaded once from Chrome for Testing into ~/.cache/l7r-chromium/<version>/, its SHA-256
# checked, with the system libraries and fonts it needs. setup-dev-env.sh runs it; it runs alone too, and is idempotent.
#
# WHY NOT PLAYWRIGHT'S INSTALL (`ask:449-phase4-slices` Q4, `ask:449-T80-order`: one browser crate over CDP, never a Playwright
# dependency): `python3 -m playwright install --with-deps chromium` fetched this same build into ~/.cache/ms-playwright and apt-installed
# the packages below; the crate needs neither Playwright nor its cache. The package lists are Playwright 1.62's own for this
# distribution (`ubuntu26.04-x64`: its `chromium` libraries and the fonts of its `tools`, which change how a page's text renders),
# so a fresh container renders as the old one did.
set -euo pipefail
HERE=$(cd "${BASH_SOURCE[0]%/*}" && pwd)
# shellcheck source=chromium.pin
. "$HERE/chromium.pin"
DEST="${L7R_CHROMIUM_HOME:-$HOME/.cache/l7r-chromium}/$CHROMIUM_VERSION"
BIN="$DEST/chrome-headless-shell-linux64/chrome-headless-shell"

LIBS=(libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 libatspi2.0-0t64 libcairo2 libcups2t64 libdbus-1-3 libdrm2 libgbm1
      libglib2.0-0t64 libnspr4 libnss3 libpango-1.0-0 libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3
      libxkbcommon0 libxrandr2
      fonts-noto-color-emoji fonts-unifont libfontconfig1 libfreetype6 xfonts-cyrillic xfonts-scalable fonts-liberation
      fonts-ipafont-gothic fonts-wqy-zenhei fonts-tlwg-loma-otf fonts-freefont-ttf unzip)
missing=()
for p in "${LIBS[@]}"; do dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p"); done
if [ "${#missing[@]}" -gt 0 ]; then
    sudo apt-get install -y -q "${missing[@]}" >/dev/null
fi

if [ ! -x "$BIN" ]; then
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    curl -sSfL -o "$tmp/shell.zip" \
        "https://storage.googleapis.com/chrome-for-testing-public/$CHROMIUM_VERSION/linux64/chrome-headless-shell-linux64.zip"
    got=$(sha256sum "$tmp/shell.zip" | cut -d' ' -f1)
    if [ "$got" != "$CHROMIUM_SHA256" ]; then
        echo "install-chromium: the download's SHA-256 is $got, not the pinned $CHROMIUM_SHA256 - check chromium.pin" >&2
        exit 1
    fi
    mkdir -p "$DEST"
    unzip -q -o "$tmp/shell.zip" -d "$DEST"
fi
# the proof it launches: the version it reports is the pinned one
"$BIN" --version | grep -q "$CHROMIUM_VERSION" || { echo "install-chromium: $BIN does not report $CHROMIUM_VERSION" >&2; exit 1; }
