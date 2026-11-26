#!/bin/sh
# 451 T347: one test run of reviews after a body edit, both wide slots of a SCRATCH slot directory held by `flock <file> sleep 60`.
# usage: OUT=<scratch dir> [F=<file to edit>] [L7R_BUILD_SLOTS_SMALL=0] lane-wait.sh <label> [hold|nohold]   (from the tree's root, SPECIFY_FEATURE exported; one run at a time)
label="$1"; hold="${2:-hold}"
S="${OUT:?OUT=<a scratch directory for the logs and the slot files>}"
SD=$S/t347-slots; mkdir -p "$SD"
f="${F:-rust/gate/crates/reviews/src/reviews/census.rs}"
events="$(git rev-parse --git-common-dir)/l7r-events/${SPECIFY_FEATURE}.jsonl"
trap 'git checkout -- "$f"' EXIT INT TERM
python3 - "$f" <<'PY'
import re, sys, time
p = sys.argv[1]
s = open(p).read()
m = re.search(r"\n(?:pub(?:\([a-z]+\))? )?fn [^;{]*\{\n", s)
s = s[:m.end()] + "    let _t347_probe = std::hint::black_box(%du64);\n" % time.time_ns() + s[m.end():]
open(p, "w").write(s)
PY
before=$(($(wc -l < "$events") + 1))
if [ "$hold" = hold ]; then
  flock "$SD/slot-0" sleep 60 &
  flock "$SD/slot-1" sleep 60 &
fi
t0=$(date +%s.%N)
L7R_BUILD_SLOT_DIR="$SD" make rust-test CRATE=rust/gate/crates/reviews > "$S/t347-wait-$label.log" 2>&1
code=$?
t1=$(date +%s.%N)
echo "$label: make exit $code, wall $(echo "$t1 - $t0" | bc) s, load $(cut -d' ' -f1 /proc/loadavg)"
tail -n +"$before" "$events" | python3 -c '
import sys, json, datetime
for l in sys.stdin:
    try: v = json.loads(l)
    except Exception: continue
    if v.get("ev") == "Phase" and v.get("src") == "rust" and "t269" in v.get("clone", ""):
        p = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        print("  ", v["step"], v.get("crates"), "code", v["code"], "%.3f s" % (p(v["t1"]) - p(v["t0"])).total_seconds())
'
tail -2 "$S/t347-wait-$label.log"
wait
