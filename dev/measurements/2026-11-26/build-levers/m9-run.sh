#!/bin/bash
# usage: m9-run.sh <label> <family: gate|guard|mode_a> <cmd: test|cover> <mode: cold|warm|keep> [ENV=VAL ...]
# cold: empties the run's target dir first; warm: touches the family's root source file first; keep: neither.
S=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad
TREE=${M9_TREE:-/diagram/.clones/diagram-backlog-m9}
label=$1 fam=$2 cmd=$3 mode=$4; shift 4
T=$HOME/.cache/l7r-cargo-target/diagram-backlog-m9-$label
cd "$TREE" || exit 2
case $fam in
  gate) crates=(rust/gate $(ls -d rust/gate/crates/*/)); touchf=rust/gate/crates/core/src/lib.rs ;;
  guard) crates=(rust/guard rust/guard/shared); touchf=rust/guard/shared/src/lib.rs ;;
  mode_a) crates=(rust/mode_a); touchf=rust/mode_a/src/lib.rs ;;
esac
args=(); for c in "${crates[@]}"; do args+=(--crate "${c%/}"); done
[ "$mode" = cold ] && rm -rf "$T"
[ "$mode" = warm ] && touch "$touchf"
load=$(cut -d' ' -f1 /proc/loadavg)
log=$S/m9-log-$label-$fam-$cmd-$mode-$(date +%s).txt
t0=$(date +%s.%N)
env "$@" CARGO_TARGET_DIR="$T" L7R_RUST_FRESH=1 scripts/gates/l7r-gate.sh rust $cmd "${args[@]}" >"$log" 2>&1
rc=$?
t1=$(date +%s.%N)
sz=$(du -sb "$T" 2>/dev/null | cut -f1)
printf '%s\t%s\t%s\t%s\trc=%s\t%.1fs\t%.2fGB\tload=%s\t%s\n' "$label" "$fam" "$cmd" "$mode" "$rc" "$(echo "$t1-$t0"|bc)" "$(echo "$sz/1000000000"|bc -l)" "$load" "$*" | tee -a $S/m9-raw.tsv
