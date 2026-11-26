#!/bin/sh
# 451 T315: a one-line edit's rebuild, crate by crate, through the gate (gate-run.sh): a constant appended to the crate's lib.rs
# (e1), the line taken out again (e2), then the test executable deleted with no source changed (link: rustc starts, finds every
# codegen unit in its incremental cache and links - an UPPER BOUND on the link). The file is put back whatever happens.
# With no executable named the link step is left out.
# usage: edit-probe.sh <out dir> <crate dir> [<test executable>]      (from the tree's root)
out="$1"; crate="$2"; exe="$3"; here="$(dirname "$0")"
lib="$crate/src/lib.rs"
trap 'git checkout -- "$lib"' EXIT INT TERM
"$here/gate-run.sh" "$crate" "$out" probe-warm
printf '\npub const T315_PROBE: u8 = 1;\n' >> "$lib"
"$here/gate-run.sh" "$crate" "$out" probe-e1
git checkout -- "$lib"
"$here/gate-run.sh" "$crate" "$out" probe-e2
[ -n "$exe" ] || exit 0
rm -f "$exe"
"$here/gate-run.sh" "$crate" "$out" probe-link
