#!/usr/bin/env bash
# t562 lever B: CARGO_INCREMENTAL=0 against the default for a COVERAGE build - `l7r-gate.sh rust cover --crate <crate>`
# on a `git archive` copy of HEAD, into scratch target directories (never a live cache). For each setting: cold (empty target),
# then warm after one source file is touched. Bytes written are the wrapper shell's /proc/self/io after its children are reaped
# (inclusive). Usage: t562-incr-ab.sh <scratch-dir> <out.tsv> [crate]
set -u
S=${1:?scratch}; OUT=${2:?tsv}; CRATE=${3:-rust/phases}
SRC=$S/src
rm -rf "$SRC"; mkdir -p "$SRC"
git -C /diagram/.clones/diagram-backlog-t270 archive HEAD | tar -x -C "$SRC"
export L7R_RUST_FRESH=1 SPECIFY_FEATURE=462-efficiency-backlog SPECIFY_FEATURE_DIRECTORY=specs/462-efficiency-backlog L7R_BLOCKS=none
printf 'setting\tphase\tseconds\texit\tload\twrite_GB\tsyscw\tcancelled_GB\ttarget_GB\ttarget_files\tincr_GB\tincr_files\n' > "$OUT"
run() { # setting phase target [env...]
  local setting=$1 phase=$2 T=$3; shift 3
  local load t0 t1 io
  load=$(cut -d' ' -f1 /proc/loadavg); t0=$(date +%s.%N)
  io=$(bash -c 'cd "$1" && shift && env "$@" scripts/gates/l7r-gate.sh rust cover --crate "'"$CRATE"'" > "'"${OUT%.tsv}"'-'"$setting-$phase"'.log" 2>&1; echo "rc=$?"; cat /proc/$$/io' _ "$SRC" L7R_GATE_TARGET="$T" CARGO_TARGET_DIR="$T" "$@")
  t1=$(date +%s.%N)
  local rc wb sc cw
  rc=$(sed -n 's/^rc=//p' <<<"$io"); wb=$(awk '/^write_bytes/{print $2}' <<<"$io"); sc=$(awk '/^syscw/{print $2}' <<<"$io"); cw=$(awk '/^cancelled_write_bytes/{print $2}' <<<"$io")
  local tg tf ig if_
  tg=$(du -sb "$T" | awk '{printf "%.2f",$1/1e9}'); tf=$(find "$T" -type f | wc -l)
  ig=$(find "$T" -path '*incremental*' -type f -printf '%s\n' | awk '{s+=$1}END{printf "%.2f",s/1e9}'); if_=$(find "$T" -path '*incremental*' -type f | wc -l)
  printf '%s\t%s\t%.1f\t%s\t%s\t%.2f\t%s\t%.2f\t%s\t%s\t%s\t%s\n' "$setting" "$phase" "$(echo "$t1 - $t0" | bc)" "$rc" "$load" "$(echo "$wb/1000000000" | bc -l)" "$sc" "$(echo "$cw/1000000000" | bc -l)" "$tg" "$tf" "$ig" "$if_" >> "$OUT"
}
for setting in default incr0; do
  T=$S/target-$setting; rm -rf "$T"; mkdir -p "$T"
  extra=(); [ "$setting" = incr0 ] && extra=(CARGO_INCREMENTAL=0)
  run "$setting" prime "$T" "${extra[@]}"   # builds the tool (same setting) and the cover profile once
  rm -rf "$T"/cover-*                         # cold cover profile, warm tool
  run "$setting" cold "$T" "${extra[@]}"
  echo "// t562 touch" >> "$SRC/$CRATE/src/counts.rs"
  run "$setting" warm-edit "$T" "${extra[@]}"
done
echo done >> "$OUT"
