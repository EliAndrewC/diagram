#!/usr/bin/env bash
# T520 (b): a pool tree's first builder-checks COLD (an empty target directory, as a tree held cold would be at its next handout)
# against WARM (the tree's own cache), for the guard and one gate crate, run from the T520 tree. Nothing of the real cache is removed:
# the cold runs build into $1 (a scratch directory, removed after), the warm runs read the tree's own cache.
# Every run is L7R_RUST_FRESH=1: a kept green result (in the clone's git directory, not the target) otherwise answers for the crate
# and no build runs - the first try, kept in void-kept/, timed only the l7r-rust tool binary's cold build (94-98 s, 1.02 GB).
# warm = the tree's own cache, nothing changed; warm-touch = one source file of the crate touched (an edit's rebuild).
# Usage: b-cold-warm.sh <scratch-target-dir> <out.tsv>
set -u
COLD=${1:?scratch target dir}; OUT=${2:?out tsv}
TREE=/diagram/.clones/diagram-backlog-t269
export L7R_RUST_FRESH=1 SPECIFY_FEATURE=451-time-retro-and-efficiency SPECIFY_FEATURE_DIRECTORY=specs/451-time-retro-and-efficiency L7R_BLOCKS=none
printf 'label\tcrate\tseconds\texit\tload_at_start\ttarget_gb_after\n' > "$OUT"
run() { # label crate [env...]
  local label=$1 crate=$2; shift 2
  local load t0 t1 rc gb
  load=$(cut -d' ' -f1 /proc/loadavg); t0=$(date +%s.%N)
  ( cd "$TREE" && env "$@" make builder-checks CRATE="$crate" ) > "${OUT%.tsv}-$label-${crate//\//_}.log" 2>&1; rc=$?
  t1=$(date +%s.%N)
  if [ "$label" = cold ]; then gb=$(du -sb "$COLD" | awk '{printf "%.2f", $1/1e9}'); else gb=-; fi
  printf '%s\t%s\t%.1f\t%s\t%s\t%s\n' "$label" "$crate" "$(echo "$t1 - $t0" | bc)" "$rc" "$load" "$gb" >> "$OUT"
}
for crate in rust/guard rust/gate/crates/measure; do
  run warm "$crate"
  touch "$TREE/$crate/src/lib.rs" 2>/dev/null || touch "$TREE/$crate/src/main.rs"
  run warm-touch "$crate"
  rm -rf "$COLD"; mkdir -p "$COLD"
  run cold "$crate" L7R_GATE_TARGET="$COLD" CARGO_TARGET_DIR="$COLD"
  run cold-again "$crate" L7R_GATE_TARGET="$COLD" CARGO_TARGET_DIR="$COLD"
done
rm -rf "$COLD"
echo done >> "$OUT"
