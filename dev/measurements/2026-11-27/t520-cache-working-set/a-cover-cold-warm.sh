#!/usr/bin/env bash
# T520 (a): what a coverage repair builder pays when its tree's coverage profile is gone - `l7r-gate.sh rust cover` (the phase T512 and T521 logged as make target rust-cover) of one gate crate
# COLD (an empty target directory: no tool binary, no cover-gate profile) against WARM (the T520 tree's own cache, its cover-gate
# last built 2026-11-27 16:19Z by T512's repair) and WARM after one source file touched. L7R_RUST_FRESH=1 so no kept result answers.
# Nothing of the real cache is removed; the cold target is a scratch directory, removed after.
# Usage: a-cover-cold-warm.sh <scratch-target-dir> <out.tsv>
set -u
COLD=${1:?scratch target dir}; OUT=${2:?out tsv}
TREE=/diagram/.clones/diagram-backlog-t269
CRATE=rust/gate/crates/measure
export L7R_RUST_FRESH=1 SPECIFY_FEATURE=451-time-retro-and-efficiency SPECIFY_FEATURE_DIRECTORY=specs/451-time-retro-and-efficiency L7R_BLOCKS=none
printf 'label\tcrate\tseconds\texit\tload_at_start\ttarget_gb_after\n' > "$OUT"
run() { # label [env...]
  local label=$1; shift
  local load t0 t1 rc gb=-
  load=$(cut -d' ' -f1 /proc/loadavg); t0=$(date +%s.%N)
  ( cd "$TREE" && env "$@" scripts/gates/l7r-gate.sh rust cover --crate "$CRATE" ) > "${OUT%.tsv}-$label.log" 2>&1; rc=$?
  t1=$(date +%s.%N)
  [ "$label" = cold ] && gb=$(du -sb "$COLD" | awk '{printf "%.2f", $1/1e9}')
  printf '%s\t%s\t%.1f\t%s\t%s\t%s\n' "$label" "$CRATE" "$(echo "$t1 - $t0" | bc)" "$rc" "$load" "$gb" >> "$OUT"
}
run warm
touch "$TREE/$CRATE/src/lib.rs"
run warm-touch
rm -rf "$COLD"; mkdir -p "$COLD"
run cold L7R_GATE_TARGET="$COLD" CARGO_TARGET_DIR="$COLD"
rm -rf "$COLD"
echo done >> "$OUT"
