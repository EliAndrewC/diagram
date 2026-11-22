#!/usr/bin/env bash
# Tests for the disk floor and the cache's cleanup (feature 451 T158; rust/guard/src/guards/scratch_sweep_hooks/disk.rs): make done,
# make land and make closing-checks refuse first below the free-space floor, naming the free space, the largest build directories, what
# make cache-clean frees and the command; DISK_OK="<reason>" is the escape, recorded; make cache-clean takes a dead tree's idle build
# directory, never a live tree's, and nothing while a build runs.
# Run: tests/hooks/test-disk-floor.sh   (exit 0 = all green)
#
# The cache is a fixture (SCRATCH_SWEEP_CARGO, SCRATCH_SWEEP_CLONES), so the refusal's walk reads it and not the real one; the floor is
# set past any disk (L7R_DISK_FLOOR_GB) to refuse, and to 0 to pass.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
GUARD="$ROOT/scripts/hooks/l7r-guard.sh"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

mkdir -p "$T/cargo/live-clone/debug" "$T/cargo/gone-trial/debug" "$T/clones/live-clone" "$T/state"
head -c 4096 /dev/zero > "$T/cargo/live-clone/debug/x"
head -c 4096 /dev/zero > "$T/cargo/gone-trial/debug/x"
# its dep-info names a tree that is gone: proven dead (451 T158; a build directory with none is kept)
echo "x: $T/gone-trial/rust/a.rs" > "$T/cargo/gone-trial/debug/x.d"
touch -d '2 days ago' "$T/cargo/gone-trial/debug/x" "$T/cargo/gone-trial/debug/x.d" "$T/cargo/gone-trial/debug" "$T/cargo/gone-trial"
# a stand-in process table (SCRATCH_SWEEP_PROC): no build runs in it unless a case plants one, whatever runs on the machine
mkdir -p "$T/proc/1"; echo bash > "$T/proc/1/comm"
export SCRATCH_SWEEP_PROC="$T/proc" SCRATCH_SWEEP_CARGO="$T/cargo" SCRATCH_SWEEP_CLONES="$T/clones" SCRATCH_SWEEP_MIRROR="$T/diagram" SCRATCH_SWEEP_STATE="$T/state"
unset DISK_OK

echo "1. below the floor the guard refuses, naming the space, the targets and the command"
out=$(L7R_DISK_FLOOR_GB=1000000000 "$GUARD" --scratch-sweep floor </dev/null 2>&1); rc=$?
[ "$rc" = 1 ] && ok "refused (exit 1)" || no "refused" "exit $rc: $out"
for want in "REFUSED: " "below the 1000000000.0 GB floor" "live-clone  (a live tree's" "gone-trial  (no live tree's" "make cache-clean frees" 'DISK_OK="<reason>"'; do
  case $out in *"$want"*) ok "names: $want" ;; *) no "names: $want" "$out" ;; esac
done
out=$(L7R_DISK_FLOOR_GB=0 "$GUARD" --scratch-sweep floor </dev/null 2>&1); rc=$?
[ "$rc" = 0 ] && [ -z "$out" ] && ok "above the floor: silent, exit 0" || no "above the floor" "exit $rc: $out"

echo "2. make done, make land and make closing-checks stop at the floor before anything else runs"
for target in "done" "land F=451 T=T0" "closing-checks T=T0"; do
  # shellcheck disable=SC2086 # the target and its arguments, word-split on purpose
  out=$(L7R_DISK_FLOOR_GB=1000000000 make -C "$ROOT" --no-print-directory $target </dev/null 2>&1); rc=$?
  case $out in
    *"REFUSED: "*"below the 1000000000.0 GB floor"*) [ "$rc" != 0 ] && ok "make $target refused at the floor" || no "make $target" "exit 0" ;;
    *) no "make $target refused at the floor" "exit $rc: $(printf '%s' "$out" | head -5)" ;;
  esac
done
out=$(make -C "$ROOT" --no-print-directory -n done DISK_OK="the disk is checked by hand" </dev/null 2>&1)
case $out in
  *"DISK_OK"*) case $out in *"--scratch-sweep floor"*) no "DISK_OK skips the floor" "$out" ;; *) ok "DISK_OK takes the escape in place of the floor" ;; esac ;;
  *) no "DISK_OK takes the escape" "$(printf '%s' "$out" | head -5)" ;;
esac

echo "3. make cache-clean takes the dead tree's idle build directory, never the live tree's"
out=$(make -C "$ROOT" --no-print-directory cache-clean DRY=1 </dev/null 2>&1); rc=$?
case $out in *"would remove $T/cargo/gone-trial "*) ok "DRY=1 lists the dead one" ;; *) no "DRY=1 lists" "exit $rc: $out" ;; esac
[ -d "$T/cargo/gone-trial" ] && ok "DRY=1 removes nothing" || no "DRY=1 removes nothing"
mkdir -p "$T/proc/42"; echo rustc > "$T/proc/42/comm"
out=$(make -C "$ROOT" --no-print-directory cache-clean </dev/null 2>&1); rc=$?
case $out in *"a build runs (42 rustc)"*) [ "$rc" != 0 ] && [ -d "$T/cargo/gone-trial" ] && ok "a build runs: refused, nothing removed" || no "held" "$out" ;; *) no "a build holds the cleanup" "exit $rc: $out" ;; esac
rm -rf "$T/proc/42"
out=$(make -C "$ROOT" --no-print-directory cache-clean </dev/null 2>&1); rc=$?
[ "$rc" = 0 ] && [ ! -e "$T/cargo/gone-trial" ] && [ -d "$T/cargo/live-clone" ] && ok "the dead one removed, the live one kept" || no "removal" "exit $rc: $out"

echo
echo "test-disk-floor: $PASS passed, $FAIL failed"
[ "$FAIL" = 0 ]
