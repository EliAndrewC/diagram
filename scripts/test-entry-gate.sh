#!/usr/bin/env bash
# test-entry-gate.sh - the companion suite for entry-gate.sh (constitution XVIII: a guard without one
# turns the gate red). It drives the guard with real payloads rather than grepping it: a grep proves a
# branch EXISTS, not that it fires.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
GATE="$HERE/entry-gate.sh"
PAGE="$ROOT/.claude/skills/diagram/research/archetypes.html"
BL="$ROOT/.claude/skills/diagram/dev/bypass-log"
pass=0; fail=0
ok() { if [ "$1" = "$2" ]; then pass=$((pass+1)); else fail=$((fail+1)); printf '  FAIL %s: got %s want %s\n' "$3" "$1" "$2"; fi; }

BAK="$(mktemp)"; cp "$PAGE" "$BAK"
restore() { cp "$BAK" "$PAGE"; rm -f "$BAK"; }
trap restore EXIT

# 1. a clean tree is quiet - the guard must not fire on correct work
( cd "$ROOT" && "$GATE" >/dev/null 2>&1 ); ok $? 0 "clean tree is quiet"

# 2. a section moved under an unchanged modal REFUSES
python3 - "$PAGE" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text()
p.write_text(s.replace("Both are drawn.", "Both are drawn, and a probe sentence stands here.", 1))
PY
( cd "$ROOT" && "$GATE" >/dev/null 2>&1 ); ok $? 1 "an unresolved pair refuses"

# 3. the escape must SAY WHY - a bare token is refused, not honored (feature 170's rule)
( cd "$ROOT" && ENTRY_DRIFT_OK=x "$GATE" >/dev/null 2>&1 ); ok $? 1 "a bare token is refused"

# 4. a real reason discharges it AND lands in dev/bypass-log/, which is what `make audit` reads
before=$(find "$BL" -name '*.json' | wc -l)
( cd "$ROOT" && ENTRY_DRIFT_OK="a probe sentence moved no finding" "$GATE" >/dev/null 2>&1 ); ok $? 0 "a reason discharges it"
after=$(find "$BL" -name '*.json' | wc -l)
ok "$after" "$((before+1))" "the reason is recorded in dev/bypass-log/"
newest="$(find "$BL" -name '*.json' -newer "$BAK" | head -1)"
[ -n "$newest" ] && grep -q "a probe sentence moved no finding" "$newest"; ok $? 0 "the recorded entry carries the reason"
[ -n "$newest" ] && rm -f "$newest"

# 5. restoring the page goes quiet again - the guard tracks the tree, not a latch
restore; trap - EXIT; BAK="$(mktemp)"; cp "$PAGE" "$BAK"; trap restore EXIT
( cd "$ROOT" && "$GATE" >/dev/null 2>&1 ); ok $? 0 "quiet again once the section is restored"

printf 'test-entry-gate: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
