#!/usr/bin/env bash
# test-claims-gate.sh - the companion suite for claims-gate.sh (constitution XVIII: a guard ships with its companion). It
# drives the guard on a small real engine tree in a throwaway git repository - an owed claim, a recorded one, an introduced
# finding, a pre-existing one, the escape with and without a reason, and a tree with no engine - rather than grepping it.
# GUARD_EDIT_OK: feature 316 - the new gate's companion.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE="$HERE/../../scripts/gates/claims-gate.sh"
GUARD_LOG_DIR="$(mktemp -d)"; export GUARD_LOG_DIR
T="$(mktemp -d)"
trap 'rm -rf "$T" "$GUARD_LOG_DIR"' EXIT

pass=0; fail=0
ok() { if [ "$1" = "$2" ]; then pass=$((pass+1)); else fail=$((fail+1)); printf '  FAIL %s: got %s want %s\n' "$3" "$1" "$2"; fi; }
g() { git -C "$T" -c user.name=t -c user.email=t@t "$@" >/dev/null 2>&1; }

# a tree with no engine: silent
g init -q -b main; g commit -q --allow-empty -m root
( cd "$T" && "$GATE" >/dev/null 2>&1 ); ok "$?" 0 "no engine, silent"

S="$T"
mkdir -p "$S/l7r/diagram/hamletgen" "$S/research/questions" "$S/buildings"
printf 'from . import rows\n' > "$S/l7r/diagram/hamletgen/__init__.py"
cat > "$S/l7r/diagram/hamletgen/rows.py" <<'PY'
"""Research: plumbing - NONE"""


def far_row(x):
    """Research: dry share - research/questions/0033-row-villages-resson.html"""
    return x * 2
PY
printf '<h2 id="row-villages-resson">Row villages</h2>\n<p>Farms face the street.</p>\n' > "$S/research/questions/0033-row-villages-resson.html"
printf '## Walls\n<!-- Research: walls - CONVENTION -->\n' > "$S/buildings.md"
printf '### Country shrine (a village district'"'"'s shrine)\n<!-- Research: precinct - UNRESEARCHED -->\n' > "$S/buildings/programs.md"

# owed: refused, naming the claim and the command
out="$( cd "$T" && "$GATE" 2>&1 )"; ok "$?" 1 "owed claims refuse"
case "$out" in *"owed (new): l7r/diagram/hamletgen/rows.py::far_row#dry share"*"make claims-bundle"*) ok y y "names the claim and the command" ;; *) ok n y "names the claim and the command" ;; esac

# the escape: no reason refused, a reason passes and is logged in the tree's bypass log
( cd "$T" && CLAIMS_OK=1 "$GATE" >/dev/null 2>&1 ); ok "$?" 1 "CLAIMS_OK without a reason"
( cd "$T" && CLAIMS_OK="a fixture with nothing checked" "$GATE" >/dev/null 2>&1 ); ok "$?" 0 "CLAIMS_OK with a reason"
ok "$(find "$S/dev/bypass-log" -name '*.json' | wc -l | tr -d ' ')" 1 "the reason is in the bypass log"

# every claim recorded IN-STEP: passes; then committed as the base
CLAIMS_PY="$HERE/../../scripts/record/claims.py" python3 - "$T" <<'PY'
import importlib.util, os, pathlib, sys
spec = importlib.util.spec_from_file_location("_claims", os.environ["CLAIMS_PY"]); cx = importlib.util.module_from_spec(spec); sys.modules["_claims"] = cx; spec.loader.exec_module(cx)
root = pathlib.Path(sys.argv[1]); cur = cx.current(root)
cx.save_index(root / cx.INDEX, {k: {"verdict": "IN-STEP", "code": r.code, "core": r.unit.core, "research": r.research, "date": "d", "note": ""} for k, r in cur.items()})
PY
( cd "$T" && "$GATE" >/dev/null 2>&1 ); ok "$?" 0 "every claim recorded"
g add -A; g commit -q -m base

# a finding introduced against an IN-STEP base: refused
python3 - "$S/dev/claims-index.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d["l7r/diagram/hamletgen/rows.py::far_row#dry share"]["verdict"] = "DRIFTED"
open(p, "w").write(json.dumps(d))
PY
out="$( cd "$T" && "$GATE" 2>&1 )"; ok "$?" 1 "an introduced finding refuses"
case "$out" in *"introduced: DRIFTED"*) ok y y "says introduced" ;; *) ok n y "says introduced" ;; esac

# the same finding at both ends: pre-existing, passes with the warning
g add -A; g commit -q -m drift
out="$( cd "$T" && "$GATE" 2>&1 )"; ok "$?" 0 "a pre-existing finding passes"
case "$out" in *"pre-existing: DRIFTED"*) ok y y "warns pre-existing" ;; *) ok n y "warns pre-existing" ;; esac

printf 'test-claims-gate: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
