#!/bin/sh
# 451 T347: two test builds after a body edit, of two crates neither of which builds from the other, started together, both wide
# slots of a SCRATCH slot directory held by `flock <file> sleep 30`. The second crate builds into a target directory of its own
# ($OUT/t347-pair-target). WHAT IT SHOWED (lane-results.md): two runs of ONE tree never meet in the lane - the run lock (runlock.rs)
# is joined in the tree's own target directory as well as the one named, so the second run waits for the first whole; each then
# takes the lane and no wide slot. Two builds queue in the lane only from two trees. Mode `lane` shows the queue with one real
# build: the lane's own file is held by `flock small-0 sleep 10` beside the two wide holders.
# usage: OUT=<scratch dir> lane-pair.sh <label> [hold|warm|lane]   (from the tree's root, SPECIFY_FEATURE exported; one run at a time)
#   warm: no edit and no holder, the two runs one after the other - run it until both crates' `slot-tell` lines read code 0.
label="$1"; mode="${2:-hold}"
S="${OUT:?OUT=<a scratch directory for the logs, the slot files and the second target directory>}"
SD=$S/t347-slots; mkdir -p "$SD"
A=rust/gate/crates/reviews; fa=$A/src/reviews/census.rs
B=rust/gate/crates/plan; fb=$B/src/plan/status.rs
events="$(git rev-parse --git-common-dir)/l7r-events/${SPECIFY_FEATURE}.jsonl"
one() { L7R_BUILD_SLOT_DIR="$SD" make rust-test CRATE=$A > "$S/t347-pair-$label-a.log" 2>&1; echo "a: exit $? at $(date +%s.%N)"; }
two() { L7R_BUILD_SLOT_DIR="$SD" CARGO_TARGET_DIR="$S/t347-pair-target" make rust-test CRATE=$B > "$S/t347-pair-$label-b.log" 2>&1; echo "b: exit $? at $(date +%s.%N)"; }
before=$(($(wc -l < "$events") + 1))
t0=$(date +%s.%N)
if [ "$mode" = warm ]; then
  one; two
else
  trap 'git checkout -- "$fa" "$fb"' EXIT INT TERM
  python3 - "$fa" "$fb" <<'PY'
import re, sys, time
for p in sys.argv[1:]:
    s = open(p).read()
    m = re.search(r"\n(?:pub(?:\([a-z]+\))? )?fn [^;{]*\{\n", s)
    s = s[:m.end()] + "    let _t347_probe = std::hint::black_box(%du64);\n" % time.time_ns() + s[m.end():]
    open(p, "w").write(s)
PY
  flock "$SD/slot-0" sleep 30 &
  flock "$SD/slot-1" sleep 30 &
  t0=$(date +%s.%N)
  if [ "$mode" = lane ]; then
    flock "$SD/small-0" sleep 10 &
    t0=$(date +%s.%N)
    one
  else
    one & a=$!
    two & b=$!
    wait $a $b
  fi
fi
echo "$label ($mode): started $t0, load $(cut -d' ' -f1 /proc/loadavg)"
tail -n +"$before" "$events" | T0="$t0" TREE="$(basename "$(git rev-parse --show-toplevel)")" python3 -c '
import sys, json, datetime, os
t = float(os.environ["T0"])
p = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
for l in sys.stdin:
    try: v = json.loads(l)
    except Exception: continue
    if v.get("ev") == "Phase" and v.get("src") == "rust" and v.get("clone", "").endswith(os.environ["TREE"]):
        print("  %-10s %-28s code %s  from %+.3f s for %.3f s" % (v["step"], ",".join(v.get("crates") or []) or "-", v["code"], p(v["t0"]) - t, p(v["t1"]) - p(v["t0"])))
'
wait
