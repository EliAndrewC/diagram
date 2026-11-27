#!/usr/bin/env bash
# t507: two scratch guards from the tree's HEAD, never the tree itself - `clean` (HEAD as it stands) and `stamps` (HEAD with
# t507-stamps.patch: wall, CPU and page-fault stamps around the read, the partial parse, the work and the drop).
# usage: t507-build.sh <tree> <scratch dir>     ->  <scratch>/bin/l7r-guard-clean, <scratch>/bin/l7r-guard-stamps
set -euo pipefail
TREE=$1 OUT=$2
HERE=$(cd "$(dirname "$0")" && pwd)
rm -rf "$OUT/src" && mkdir -p "$OUT/src" "$OUT/bin"
git -C "$TREE" archive HEAD rust .cargo | tar -x -C "$OUT/src"   # rust/Cargo.lock is tracked: the tree's pins
cmp "$TREE/rust/Cargo.lock" "$OUT/src/rust/Cargo.lock"
cd "$OUT/src/rust"
export CARGO_TARGET_DIR="$OUT/target"
cargo build --profile tool -p l7r_guard --bin l7r-guard >"$OUT/build-clean.log" 2>&1
cp "$CARGO_TARGET_DIR/tool/l7r-guard" "$OUT/bin/l7r-guard-clean"
# the patch's paths are rust-clean/guard/... and rust/guard/...: strip two
(cd guard && git apply -p2 "$HERE/t507-stamps.patch")
cargo build --profile tool -p l7r_guard --bin l7r-guard >"$OUT/build-stamps.log" 2>&1
cp "$CARGO_TARGET_DIR/tool/l7r-guard" "$OUT/bin/l7r-guard-stamps"
echo built "$OUT/bin/l7r-guard-clean" "$OUT/bin/l7r-guard-stamps"
