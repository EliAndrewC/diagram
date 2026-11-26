#!/bin/sh
# 451 T315: one FRESH gate test run of a crate, timed around the process, its build and test Phase lines read beside it.
# `before` is the time from the command's start to its first Phase line, `after` from its last to the command's end.
# NOFRESH=1 leaves `FRESH=1` out, as a builder's own run after an edit has it (the kept result is keyed by content, so an edited crate
# runs anyway); FRESH=1 costs a REASON check through the whole `l7r-gate` tool, rebuilt first where any gate source moved.
# usage: gate-run.sh <crate dir> <out dir> <label>     (run from the tree's root; one run at a time)
crate="$1"; out="$2"; label="$3"
events="$(git rev-parse --git-common-dir)/l7r-events/${SPECIFY_FEATURE}.jsonl"
before=$(wc -l < "$events")
load=$(cut -d' ' -f1 /proc/loadavg)
log="$out/$(echo "$crate" | tr / _)-$label.log"
start=$(date +%s.%N)
if [ -n "${NOFRESH:-}" ]; then
  /usr/bin/time -f "%e %U %S" -o "$log.time" make rust-test CRATE="$crate" > "$log" 2>&1
else
  /usr/bin/time -f "%e %U %S" -o "$log.time" make rust-test CRATE="$crate" FRESH=1 REASON="T315 measures a warm run" > "$log" 2>&1
fi
rc=$?
end=$(date +%s.%N)
tail -n +"$((before + 1))" "$events" | grep '"ev":"Phase"' | grep "$(pwd)\"" | START=$start END=$end python3 -c '
import sys, json, datetime, os
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
out = {}; first = last = None
for l in sys.stdin:
    e = json.loads(l)
    out[e["step"]] = out.get(e["step"], 0) + ts(e["t1"]) - ts(e["t0"])
    first = first or ts(e["t0"]); last = ts(e["t1"])
if first:  # before the first phase: the wrapper, its tool build where a source it builds from moved, the kept key; after the last: the record
    out["before"] = first - float(os.environ["START"]); out["after"] = float(os.environ["END"]) - last
print(" ".join(f"{k}={v:.2f}" for k, v in out.items()))' > "$log.phases"
inner=$(grep -o 'finished in [0-9.]*s' "$log" | tr '\n' ' ')
printf '%s %s rc=%s load=%s wall/user/sys=%s phases: %s libtest: %s\n' "$crate" "$label" "$rc" "$load" "$(tail -1 "$log.time")" "$(cat "$log.phases")" "$inner"
