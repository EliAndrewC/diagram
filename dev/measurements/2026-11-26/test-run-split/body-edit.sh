#!/bin/sh
# 451 T315: a REAL edit's rebuild - a statement put at the head of the first function body of each file named (a new value each
# time, so the binary changes and the tests run), through the gate as a builder runs it (gate-run.sh, no FRESH). The files are put
# back whatever happens.
# usage: body-edit.sh <out dir> <crate dir> <label> <file> [<file> ...]      (from the tree's root)
out="$1"; crate="$2"; label="$3"; shift 3
trap 'git checkout -- "$@"' EXIT INT TERM
for f in "$@"; do
  python3 - "$f" <<'PY'
import re, sys, time
p = sys.argv[1]; s = open(p).read()
m = re.search(r"\n(?:pub(?:\([a-z]+\))? )?fn [^;{]*\{\n", s)
s = s[:m.end()] + "    let _t315_probe = std::hint::black_box(%du64);\n" % time.time_ns() + s[m.end():]
open(p, "w").write(s)
PY
done
NOFRESH=1 "$(dirname "$0")/gate-run.sh" "$crate" "$out" "$label"
