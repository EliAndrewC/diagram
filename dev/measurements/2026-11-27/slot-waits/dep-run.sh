#!/bin/sh
# 451 T420 (3): a builder's test build of one crate after a REAL function-body edit of a SHARED crate it builds on (T347's
# small-run.sh edit: a statement with a new value at the head of the first function body of the file named), its process tree's
# memory sampled and each rustc's crate named (this folder's mem-sample.py), read by Phase span (T347's windows.py). The build
# slot is left ON (unlike T347): the build takes a wide slot as a builder's would, and a wait for one is its own Phase line.
# The file is put back whatever happens. One run at a time.
# usage: dep-run.sh <out dir> <crate to build> <label> <file to edit | -> (from the tree's root; SPECIFY_FEATURE exported)
out="$1"; crate="$2"; label="$3"; f="$4"; here="$(dirname "$0")"; t347="$here/../../2026-11-26/small-build-memory"
events="$(git rev-parse --git-common-dir)/l7r-events/${SPECIFY_FEATURE}.jsonl"
if [ "$f" != "-" ]; then
  trap 'git checkout -- "$f"' EXIT INT TERM
  python3 - "$f" <<'PY'
import re, sys, time
p = sys.argv[1]
s = open(p).read()
m = re.search(r"\n(?:pub(?:\([a-z]+\))? )?fn [^;{]*\{\n", s)
s = s[:m.end()] + "    let _t420_probe = std::hint::black_box(%du64);\n" % time.time_ns() + s[m.end():]
open(p, "w").write(s)
PY
fi
tag="$out/$(echo "$crate" | tr / _)-$label"
before=$(($(wc -l < "$events") + 1))
printf '%s %s (edit %s) load=%s cg_anon=%s MiB: ' "$crate" "$label" "$f" "$(cut -d' ' -f1 /proc/loadavg)" "$(awk '/^anon /{printf "%d", $2/1048576}' /sys/fs/cgroup/memory.stat)"
python3 "$here/mem-sample.py" "$tag.tsv" -- make rust-test CRATE="$crate" > "$tag.log" 2>&1
tail -1 "$tag.log"
python3 "$t347/windows.py" "$tag.tsv" "$events" "$before" "$(pwd)"
printf '  rustc units: %s; crates: %s\n' "$(wc -l < "$tag.tsv.crates")" "$(cut -f2 "$tag.tsv.crates" | sort -u | tr '\n' ' ')"
