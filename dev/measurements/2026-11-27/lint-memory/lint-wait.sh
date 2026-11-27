#!/bin/sh
# 451 T355: one `make builder-checks` of reviews after a body edit, both wide slots of a SCRATCH slot directory held by
# `flock <file> sleep 60` (451 T347's lane-wait.sh, with the builder's whole first tier in the place of its test run: the test
# build, then the lint's passes, then the format check). Its slot lines and its lint line are read from the event log.
# F names the file(s) edited; a dependency's body edit does not move its dependent's lint key (the key reads a dependency's
# interface), so the negative edits a file of core AND one of reviews.
# usage: OUT=<scratch dir> [F="<file to edit> ..."] [L7R_BUILD_SLOTS_SMALL=0] lint-wait.sh <label> [hold|nohold]   (from the tree's root, SPECIFY_FEATURE exported; one run at a time)
label="$1"; hold="${2:-hold}"
S="${OUT:?OUT=<a scratch directory for the logs and the slot files>}"
SD=$S/t355-slots; mkdir -p "$SD"
f="${F:-rust/gate/crates/reviews/src/reviews/census.rs}"
events="$(git rev-parse --git-common-dir)/l7r-events/${SPECIFY_FEATURE}.jsonl"
here="$(basename "$(pwd)")"
trap 'git checkout -- $f' EXIT INT TERM
python3 - $f <<'PY'
import re, sys, time
for p in sys.argv[1:]:
    s = open(p).read()
    m = re.search(r"\n(?:pub(?:\([a-z]+\))? )?fn [^;{]*\{\n", s)
    s = s[:m.end()] + "    let _t355_probe = std::hint::black_box(%s_u64);\n" % format(time.time_ns(), "_") + s[m.end():]
    open(p, "w").write(s)
PY
before=$(($(wc -l < "$events") + 1))
if [ "$hold" = hold ]; then
  flock "$SD/slot-0" sleep 60 &
  flock "$SD/slot-1" sleep 60 &
fi
t0=$(date +%s.%N)
L7R_BUILD_SLOT_DIR="$SD" make builder-checks CRATE=rust/gate/crates/reviews > "$S/t355-wait-$label.log" 2>&1
code=$?
t1=$(date +%s.%N)
echo "$label: make exit $code, wall $(echo "$t1 - $t0" | bc) s, load $(cut -d' ' -f1 /proc/loadavg)"
tail -n +"$before" "$events" | python3 -c '
import sys, json, datetime
for l in sys.stdin:
    try: v = json.loads(l)
    except Exception: continue
    if v.get("ev") == "Phase" and v.get("src") == "rust" and v.get("clone", "").endswith(sys.argv[1]):
        p = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        print("  ", v["step"], v.get("crates"), "code", v["code"], "%.3f s" % (p(v["t1"]) - p(v["t0"])).total_seconds())
' "$here"
grep -h "rust-checks:" "$S/t355-wait-$label.log" | tail -3
wait
