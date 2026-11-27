#!/bin/sh
# 451 T355: the LINT of one crate after a REAL function-body edit in a warm tree (451 T347's small-run.sh, its edit and its rules:
# a statement with a new value at the head of the first function body of each file named), with NO build slot (L7R_BUILD_SLOTS=0,
# so no pass waits and its memory is its own), the run's process tree sampled by lint pass (lint-sample.py).
# The files are put back whatever happens. One run at a time, no load generator.
# With several files (every source of a crate), the edit is the crate's whole re-lint: the ceiling of "the crate alone".
# PRE="<command>" runs first, unsampled, after the edit (the negative: a dependency's edit, then the dependent's test run, then its lint).
# usage: [PRE="..."] lint-run.sh <out dir> <crate dir to lint> <label> <file> [<file> ...]      (from the tree's root)
out="$1"; crate="$2"; label="$3"; shift 3; f="$1"; n="$#"; here="$(dirname "$0")"
trap 'git checkout -- "$@"' EXIT INT TERM
python3 - "$@" <<'PY'
import re, sys, time
for p in sys.argv[1:]:
    s = open(p).read()
    m = re.search(r"\n(?:pub(?:\([a-z]+\))? )?fn [^;{]*\{\n", s)
    if not m: continue
    s = s[:m.end()] + "    let _t355_probe = std::hint::black_box(%s_u64);\n" % format(time.time_ns(), "_") + s[m.end():]
    open(p, "w").write(s)
PY
tag="$out/t355-$(echo "$crate" | tr / _)-$label"
if [ -n "$PRE" ]; then sh -c "$PRE" > "$tag.pre.log" 2>&1; echo "PRE exit $? ($PRE): $(tail -1 "$tag.pre.log")"; fi
printf '%s %s (%s, %s file(s)) load=%s cg_anon=%s MiB: ' "$crate" "$label" "$f" "$n" "$(cut -d' ' -f1 /proc/loadavg)" "$(awk '/^anon /{printf "%d", $2/1048576}' /sys/fs/cgroup/memory.stat)"
L7R_BUILD_SLOTS=0 python3 "$here/lint-sample.py" "$tag.tsv" -- scripts/gates/l7r-gate.sh rust lint --crate "$crate" > "$tag.log" 2>&1
grep -h '^rc=\|^  ' "$tag.log"
grep -h 'rust-checks:' "$tag.log" | tail -2
