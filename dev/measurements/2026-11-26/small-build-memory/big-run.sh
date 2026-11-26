#!/bin/sh
# 451 T347: one of the builds the slot was made for, sampled alone (mem-sample.py) WHILE HOLDING A BUILD SLOT, so it is never a third
# large build on the machine: the slot's own flock is taken here (the first free, else a wait on slot-0) and the command runs with the
# holder's mark, so the gate under it takes no second.
#   cold  <crate dir>  cargo test --no-run of the crate's manifest into an EMPTY scratch target directory (every dependency compiled:
#                      what a new tree's first test build is), the gate's own words; the scratch directory is removed after
#   cover <crate dir> <file>  the gate's coverage pass of the crate after a body edit of the file, in the tree's own coverage directory
# usage: big-run.sh <out dir> cold|cover <crate dir> [<file>]      (from the tree's root; SPECIFY_FEATURE exported)
out="$1"; kind="$2"; crate="$3"; f="$4"; here="$(dirname "$0")"; slots="$HOME/.cache/l7r-build-slots"
tag="$out/$(echo "$crate" | tr / _)-$kind"
events="$(git rev-parse --git-common-dir)/l7r-events/${SPECIFY_FEATURE}.jsonl"; before=$(($(wc -l < "$events") + 1))
# -E 200: a slot that is held is told apart from the command's own exit (the first form of this line ran a red command again in the
# next slot: the coverage row below is its first run, read from the log; its samples were overwritten by the second)
held() { for s in slot-0 slot-1; do flock -n -E 200 "$slots/$s" "$@"; rc=$?; [ "$rc" = 200 ] || return "$rc"; done; flock "$slots/slot-0" "$@"; }
printf '%s %s load=%s cg_anon=%s MiB: ' "$crate" "$kind" "$(cut -d' ' -f1 /proc/loadavg)" "$(awk '/^anon /{printf "%d", $2/1048576}' /sys/fs/cgroup/memory.stat)"
case "$kind" in
cold)
  t="$HOME/.cache/l7r-cargo-target/t347-cold-scratch"; rm -rf "$t"
  CARGO_TARGET_DIR="$t" L7R_BUILD_SLOT_HELD=1 held python3 "$here/mem-sample.py" "$tag.tsv" -- \
    cargo test --no-run --message-format=json --quiet --manifest-path "$(pwd)/$crate/Cargo.toml" > "$tag.log" 2>&1
  rm -rf "$t" ;;
cover)
  trap 'git checkout -- "$f"' EXIT INT TERM
  python3 - "$f" <<'PY'
import re, sys, time
p = sys.argv[1]; s = open(p).read()
m = re.search(r"\n(?:pub(?:\([a-z]+\))? )?fn [^;{]*\{\n", s)
s = s[:m.end()] + "    let _t347_probe = std::hint::black_box(%du64);\n" % time.time_ns() + s[m.end():]
open(p, "w").write(s)
PY
  L7R_BUILD_SLOT_HELD=1 held python3 "$here/mem-sample.py" "$tag.tsv" -- scripts/gates/l7r-gate.sh rust cover --crate "$crate" > "$tag.log" 2>&1 ;;
esac
grep "^rc=" "$tag.log" | tail -1
python3 "$here/windows.py" "$tag.tsv" "$events" "$before" "$(pwd)"
