#!/usr/bin/env bash
# test-cohort-gate.sh - the companion suite for cohort-gate.sh (constitution XVIII: a guard ships with its companion). It drives
# the gate on a small engine tree in a throwaway git repository - main's engine and a branch that changes it - with cohort
# records written as cohort_audit writes them: none, the escape, a landing and a fresh record, a seed newly failing against
# main's baseline, the same seed failing on main too, a failing fresh seed.
# GUARD_EDIT_OK: feature 386 - the new gate's companion.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE="$HERE/../../scripts/gates/cohort-gate.sh"
GUARD_LOG_DIR="$(mktemp -d)"; export GUARD_LOG_DIR
T="$(mktemp -d)"
trap 'rm -rf "$T" "$GUARD_LOG_DIR"' EXIT

pass=0; fail=0
ok() { if [ "$1" = "$2" ]; then pass=$((pass+1)); else fail=$((fail+1)); printf '  FAIL %s: got %s want %s\n' "$3" "$1" "$2"; fi; }
g() { git -C "$T" -c user.name=t -c user.email=t@t "$@" >/dev/null 2>&1; }
# rec <utc> <commit> <first seed> <failing seeds, comma-separated or empty>: a record as cohort_audit.write_record writes it - 48
# fixed seeds, the pinned rows and a 48-seed fresh block from 12345
rec() {
  python3 - "$T/dev/cohort-log" "$@" <<'PY'
import json, pathlib, sys
log, utc, commit, first, bad = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4]), {int(x) for x in sys.argv[5].split(",") if x}
seeds = [{"seed": n, "households": 12, "pins": {}, "how": "rolled", "verdict": "fail" if n in bad else "pass",
          "failures": ["lane_knots"] if n in bad else [], "counts": {"lane_knots": 1} if n in bad else {}, "form": "linear"}
         for n in [*range(first, first + 48), *range(901, 907)]]
seeds += [{"seed": n, "households": 12, "pins": {}, "how": "rolled", "verdict": "fail" if n in bad else "pass", "fresh": True,
           "failures": ["lane_knots"] if n in bad else [], "counts": {"lane_knots": 1} if n in bad else {}, "form": "linear"}
          for n in range(12345, 12345 + 48)]
log.mkdir(parents=True, exist_ok=True)
(log / f"{utc}-t-1.json").write_text(json.dumps({"utc": utc, "clone": "t", "feature": "", "commit": commit, "first_seed": first,
    "households": None, "count": len(seeds), "served": 0, "seeds": seeds}, indent=1) + "\n")
PY
}

# a tree with no cohort-landing target: silent
g init -q -b main; g commit -q --allow-empty -m root
( cd "$T" && "$GATE" >/dev/null 2>&1 ); ok "$?" 0 "no cohort-landing target, silent"

mkdir -p "$T/l7r/diagram/hamletgen" "$T/pool" "$T/scripts/gates"
cp "$HERE/../../scripts/gates/gate-stamp.py" "$T/scripts/gates/"  # the engine key loads it from the tree it reads
printf 'cohort-landing:\n\t@true\n' > "$T/Makefile"
printf 'X = 1\n' > "$T/l7r/diagram/hamletgen/rows.py"; printf 'p\n' > "$T/pool/p.txt"
g add -A; g commit -q -m "main's engine"; base="$(git -C "$T" rev-parse --short HEAD)"
g checkout -q -b work
printf 'X = 2\n' > "$T/l7r/diagram/hamletgen/rows.py"; g commit -qam "the work's engine"; head="$(git -C "$T" rev-parse --short HEAD)"

# no record on the landed engine: refused, naming the command
out="$( cd "$T" && "$GATE" 2>&1 )"; ok "$?" 1 "no landing record refuses"
case "$out" in *"no landing cohort"*"48-seed fresh block"*"make cohort-landing"*) ok y y "names the missing record and the command" ;; *) ok n y "names the missing record and the command" ;; esac

# the escape: no reason refused, a reason passes and is logged in the tree's bypass log
( cd "$T" && COHORT_OK=1 "$GATE" >/dev/null 2>&1 ); ok "$?" 1 "COHORT_OK without a reason"
( cd "$T" && COHORT_OK="a fixture with nothing rolled" "$GATE" >/dev/null 2>&1 ); ok "$?" 0 "COHORT_OK with a reason"
ok "$(find "$T/dev/bypass-log" -name '*.json' | wc -l | tr -d ' ')" 1 "the reason is in the bypass log"

# a record of MAIN's engine is not the landing record
rec 20261001T000000Z "$base" 1 ""
out="$( cd "$T" && "$GATE" 2>&1 )"; ok "$?" 1 "a record of main's engine does not count"

# the landing record on the landed engine, two fresh seeds failing: lands, the rate printed
rec 20261002T000000Z "$head" 1 "12350,12360"
out="$( cd "$T" && "$GATE" 2>&1 )"; ok "$?" 0 "the landing record passes, its failing fresh seeds no refusal"
case "$out" in *"fresh block from seed 12345: 2 of 48 failed (4%) - seeds 12350, 12360"*) ok y y "prints the fresh rate, never refuses on it" ;; *) ok n y "prints the fresh rate, never refuses on it" ;; esac

# seed 5 passes on main's engine and fails on the landed one: a regression, refused
rec 20261003T000000Z "$head" 1 "5"
out="$( cd "$T" && "$GATE" 2>&1 )"; ok "$?" 1 "a seed newly failing refuses"
case "$out" in *"seed 5 NEWLY FAILING"*) ok y y "names the regressed seed" ;; *) ok n y "names the regressed seed" ;; esac

# seed 5 failing the same way on main's engine too: pre-existing, lands
rec 20261003T000100Z "$base" 1 "5"; rec 20261003T000200Z "$head" 1 "5"
out="$( cd "$T" && "$GATE" 2>&1 )"; ok "$?" 0 "a pre-existing failure passes"
case "$out" in *"seed 5 PRE-EXISTING"*) ok y y "prints it pre-existing" ;; *) ok n y "prints it pre-existing" ;; esac

# a commit of docs, a docstring and a comment under l7r/ is the same engine: the landing record still counts (the GM, 2026-10-18)
printf 'docs\n' > "$T/l7r/diagram/CLAUDE.md"; printf '"""Rows."""\n# why\nX  =  2\n' > "$T/l7r/diagram/hamletgen/rows.py"
g add -A; g commit -qm "docs and a docstring"
( cd "$T" && "$GATE" >/dev/null 2>&1 ); ok "$?" 0 "a docs or docstring commit keeps the landing record"
printf 'X = 3\n' > "$T/l7r/diagram/hamletgen/rows.py"; g commit -qam "a code token"
( cd "$T" && "$GATE" >/dev/null 2>&1 ); ok "$?" 1 "a code token moved: the landing record no longer counts"

printf 'test-cohort-gate: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
