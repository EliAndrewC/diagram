#!/bin/sh
# 451 T347: a builder's test run of one crate after a REAL function-body edit in a warm tree (T315's body-edit.sh edit: a statement
# with a new value at the head of the first function body of the file named), with NO build slot (L7R_BUILD_SLOTS=0, so the build
# never waits and its memory is its own), its process tree's memory sampled (mem-sample.py) and read by Phase span (windows.py).
# The file is put back whatever happens. One run at a time.
# With several files (every source of a crate: `all`), the edit is the crate's whole rebuild, the ceiling of "the crate alone".
# usage: small-run.sh <out dir> <crate dir> <label> <file> [<file> ...]      (from the tree's root; SPECIFY_FEATURE exported)
out="$1"; crate="$2"; label="$3"; shift 3; f="$1"; n="$#"; here="$(dirname "$0")"
events="$(git rev-parse --git-common-dir)/l7r-events/${SPECIFY_FEATURE}.jsonl"
trap 'git checkout -- "$@"' EXIT INT TERM
python3 - "$@" <<'PY'
import re, sys, time
for p in sys.argv[1:]:
    s = open(p).read()
    m = re.search(r"\n(?:pub(?:\([a-z]+\))? )?fn [^;{]*\{\n", s)
    if not m: continue
    s = s[:m.end()] + "    let _t347_probe = std::hint::black_box(%du64);\n" % time.time_ns() + s[m.end():]
    open(p, "w").write(s)
PY
tag="$out/$(echo "$crate" | tr / _)-$label"
before=$(($(wc -l < "$events") + 1))
printf '%s %s (%s, %s file(s)) load=%s cg_anon=%s MiB: ' "$crate" "$label" "$f" "$n" "$(cut -d' ' -f1 /proc/loadavg)" "$(awk '/^anon /{printf "%d", $2/1048576}' /sys/fs/cgroup/memory.stat)"
L7R_BUILD_SLOTS=0 python3 "$here/mem-sample.py" "$tag.tsv" -- make rust-test CRATE="$crate" > "$tag.log" 2>&1
tail -1 "$tag.log"
python3 "$here/windows.py" "$tag.tsv" "$events" "$before" "$(pwd)"
