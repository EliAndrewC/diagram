#!/usr/bin/env bash
# test-entry-gate.sh - the companion suite for entry-gate.sh, the record gate (constitution XVIII: a guard without one
# turns the gate red). It drives the guard with real edits to a real question page rather than grepping it: a grep proves
# a branch EXISTS, not that it fires. Feature 311 rewrote it: the page it edited had become a pointer
# (`contents.json#field-archetypes`) and nothing ran it, because `make hooks-test` listed only `*-hooks.sh` - it is on the
# roster now.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
GATE="$HERE/entry-gate.sh"
PAGE="$ROOT/research/questions/0094-rooms-for-a-parley-across-a-border.html"
BL="$ROOT/dev/bypass-log"
# ISOLATE THE CENSUS (feature 169) AND THE ANSWERS (feature 311): a suite that drives a recording guard writes into
# throwaway stores, or its fixtures land in the live guard census and the clone's own answer records.
GUARD_LOG_DIR="$(mktemp -d)"; export GUARD_LOG_DIR
RECORD_CHECKS_DIR="$(mktemp -d)"; export RECORD_CHECKS_DIR

pass=0; fail=0
ok() { if [ "$1" = "$2" ]; then pass=$((pass+1)); else fail=$((fail+1)); printf '  FAIL %s: got %s want %s\n' "$3" "$1" "$2"; fi; }

BAK="$(mktemp)"; cp "$PAGE" "$BAK"
BL_BEFORE="$(find "$BL" -name '*.json' | wc -l)"
restore() {
  cp "$BAK" "$PAGE"; rm -f "$BAK"
  rm -rf "$GUARD_LOG_DIR" "$RECORD_CHECKS_DIR"
  # any bypass-log entry this suite created goes too, however it exited - the log is a record of real
  # bypasses and a test's fixtures have no business in it
  while [ "$(find "$BL" -name '*.json' | wc -l)" -gt "$BL_BEFORE" ]; do
    rm -f "$(find "$BL" -name '*.json' -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)"   # GUARD_EDIT_OK: 2026-10-02 - no SIGPIPE'd ls across month folders
  done
}
trap restore EXIT
edit() { python3 - "$PAGE" "$1" "$2" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text()
assert sys.argv[2] in s
p.write_text(s.replace(sys.argv[2], sys.argv[3], 1))
PY
}
answer_all() { python3 - "$ROOT" <<'PY'
import pathlib, sys
sys.path.insert(0, sys.argv[1] + "/scripts")
import _record_owed as ro
root = pathlib.Path(sys.argv[1])
for u in ro.unanswered(root):
    ro.write_answer(ro.store(root), u.slug, u.fingerprint, "0/0/0")
PY
}

# the delta this clone carries may owe units of its own, answered in the clone's real store; the throwaway store starts
# with them answered, so every case below measures only what the suite itself changes
answer_all

# 1. a tree with no record change is quiet - the guard must not fire on correct work
( cd "$ROOT" && "$GATE" >/dev/null 2>&1 ); ok $? 0 "no record change is quiet"

# 2. a comment and a re-wrap change no words, so they owe nothing
edit "<p>Where two powers" "<p><!-- probe -->Where  two powers"
( cd "$ROOT" && "$GATE" >/dev/null 2>&1 ); ok $? 0 "a comment and a re-wrap owe nothing"
cp "$BAK" "$PAGE"

# 3. reworded findings owe checks, and the refusal names them with the command that answers each
edit "a short way apart." "a short distance apart."
out="$( cd "$ROOT" && "$GATE" 2>&1 )"; ok $? 1 "an owed unit with no answer refuses"
case "$out" in *"quote-check:0094#kyakhta-trade-enwiki"*"make check-bundle Q=0094 FOR=quote-check"*) r=0 ;; *) r=1 ;; esac
ok "$r" 0 "the refusal names the unit and its bundle command"

# 4. answered at this content: quiet; the words move again: the answer is stale and it refuses again
answer_all
( cd "$ROOT" && "$GATE" >/dev/null 2>&1 ); ok $? 0 "answered units ship"
edit "a short distance apart." "a short walk apart."
( cd "$ROOT" && "$GATE" >/dev/null 2>&1 ); ok $? 1 "a stale answer refuses"

# 5. the escapes must SAY WHY - a bare token is refused, not honored (feature 170's rule)
( cd "$ROOT" && RECORD_CHECKS_OK=x "$GATE" >/dev/null 2>&1 ); ok $? 1 "a bare RECORD_CHECKS_OK is refused"
( cd "$ROOT" && ENTRY_DRIFT_OK=x "$GATE" >/dev/null 2>&1 ); ok $? 1 "a bare ENTRY_DRIFT_OK is refused"

# 6. ENTRY_DRIFT_OK discharges the entry-drift units only: the quote-check units still refuse
( cd "$ROOT" && ENTRY_DRIFT_OK="a probe moved no finding" "$GATE" >/dev/null 2>&1 ); ok $? 1 "ENTRY_DRIFT_OK leaves the other units owed"

# 7. a real RECORD_CHECKS_OK reason discharges every unit AND lands in dev/bypass-log/
before=$(find "$BL" -name '*.json' | wc -l)
( cd "$ROOT" && RECORD_CHECKS_OK="a probe sentence, no check owed" "$GATE" >/dev/null 2>&1 ); ok $? 0 "a reason discharges it"
after=$(find "$BL" -name '*.json' | wc -l)
ok "$after" "$((before+1))" "the reason is recorded in dev/bypass-log/"
grep -rlq --include='*.json' "a probe sentence, no check owed" "$BL"; ok $? 0 "the recorded entry carries the reason"   # GUARD_EDIT_OK: 2026-10-02 - the entry is in its month folder

# 8. restoring the page goes quiet again - the guard tracks the tree, not a latch
cp "$BAK" "$PAGE"
( cd "$ROOT" && "$GATE" >/dev/null 2>&1 ); ok $? 0 "quiet again once the page is restored"

printf 'test-entry-gate: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
