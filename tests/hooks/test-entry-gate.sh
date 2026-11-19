#!/usr/bin/env bash
# test-entry-gate.sh - the companion suite for entry-gate.sh, the record gate (constitution XVIII: a guard without one
# turns the gate red). It drives the guard with real edits to a real question page rather than grepping it: a grep proves
# a branch EXISTS, not that it fires. Feature 311 rewrote it: the page it edited had become a pointer
# (`contents.json#field-archetypes`) and nothing ran it, because `make hooks-test` listed only `*-hooks.sh` - it is on the
# roster now.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REAL="$(git -C "$HERE" rev-parse --show-toplevel)"
GATE="$HERE/../../scripts/gates/entry-gate.sh"
# A THROWAWAY CLONE, NOT THE LIVE TREE (feature 329, found when this suite's probe text - "a short walk apart." - was
# swept into a commit by a `git commit -a` made while hooks-test ran). The suite edits a real question page to drive
# the guard; it now edits that page in a local clone of HEAD, whose origin/main is HEAD, so the delta the guard sees is
# exactly the suite's own edits. The guard's scripts still come from HERE - the working copy under test.
# TWO CLONES, SIDE BY SIDE (feature 449 T205): each record gate here computes the tree's owed units, about 1.5-2 s, nine of them, and
# one after another they made this suite the full hook run's longest (53.7 s and 36.0 s in two runs, 20.6 s alone, 2026-11-19). Case 4
# answers and re-stales the units, six of the nine; the other cases need only an edited page. So case 4 runs in a clone of its own,
# dealt beside the rest by tests/hooks/parts.sh (`run_parts`, PARTS_MAX-capped like every split suite), each clone the case's own:
# its page, its bypass log, its guard log and its answers' store, all removed with it.
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
ok() { if [ "$1" = "$2" ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); printf '  FAIL %s: got %s want %s\n' "$3" "$1" "$2"; fi; }
# fixture: a fresh clone in its own directory under the part's $T, the page and its pristine copy, and throwaway stores - a suite that
# drives a recording guard writes into them, or its fixtures land in the live guard census (feature 169) and the clone's own answer
# records (feature 311)
fixture() {
  local d; d=$(mktemp -d -p "$T")
  ROOT="$d/clone"
  git clone -q "$REAL" "$ROOT" || { echo "test-entry-gate: could not clone $REAL"; exit 1; }
  PAGE="$ROOT/research/questions/0094-rooms-for-a-parley-across-a-border.html"
  BL="$ROOT/dev/bypass-log"
  BAK="$d/page.bak"; cp "$PAGE" "$BAK"
  GUARD_LOG_DIR="$d/guard-log"; RECORD_CHECKS_DIR="$d/checks"; mkdir -p "$GUARD_LOG_DIR" "$RECORD_CHECKS_DIR"
  export GUARD_LOG_DIR RECORD_CHECKS_DIR
}
edit() {
  local text; text="$(cat "$PAGE"; printf x)"; text="${text%x}"
  case "$text" in *"$1"*) ;; *) printf '  FAIL edit: not in the page: %s\n' "$1"; exit 1 ;; esac
  printf '%s' "${text/"$1"/"$2"}" > "$PAGE"
}
# Every unit the clone owes, answered at its content through the record tools' own command (feature 449 T149: through
# `scripts/owed_door.py`'s writer until its door left with `entry_owed.py`); a reason stands in for a bundle, its bypass record
# in the throwaway clone, which goes with it.
# ONE ANSWER PER CHECK (feature 449 T122): each `--answer` computes the tree's owed units again, about 1 s, and one call a unit
# was 11 calls, half the suite's 22.8 s and the full hook run's bound beside idle-tests (2026-11-17). A check's units are named
# together - its notes on a question by `--q` and `--notes k,k`, its other subjects by `--kind s,s` - so the same units are
# answered, and case 4 still proves every one of them is (the gate goes quiet). The three modal-research units are answered
# as a session answers them, by one `CHECK=modal-research` (its agent's three checks): 11 calls became 3.
answer_all() {
  local g="$HERE/../../scripts/gates/l7r-gate.sh" check q notes kinds
  "$g" record record-owed --root "$ROOT" --unanswered --slugs | awk '
    { i = index($0, ":"); if (!i) next; c = substr($0, 1, i - 1); s = substr($0, i + 1); j = index(s, "#")
      if (c == "modal-accuracy" || c == "modal-references" || c == "modal-gaps") { c = "modal-research"; if ((c, s) in seen) next; seen[c, s] = 1 }
      if (j) { k = c "|" substr(s, 1, j - 1); sep = (k in notes) ? "," : ""; notes[k] = notes[k] sep substr(s, j + 1) }
      else { sep = (c in kinds) ? "," : ""; kinds[c] = kinds[c] sep s } }
    END { for (k in notes) { split(k, p, "|"); c = p[1]; print k "|" notes[k] "|" (c in done ? "" : kinds[c]); done[c] = 1 }
          for (c in kinds) if (!(c in done)) print c "|||" kinds[c] }' |
  while IFS='|' read -r check q notes kinds; do
    "$g" record record-owed --root "$ROOT" --answer "$check" --result 0/0/0 ${q:+--q "$q"} ${notes:+--notes "$notes"} \
      ${kinds:+--kind "$kinds"} --reason "the suite answers its own edits" >/dev/null
  done
}

# The throwaway clone carries no delta of its own: its origin/main is the HEAD it was cloned from, so nothing is owed before
# the suite's edits and case 1 holds that.

case_main() {  # cases 1-3 and 5-8, one clone; 3 record gates, about 5 s alone (2026-11-19)
fixture

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

# (case 4, the answers, is case_answers, in a clone of its own; the units case 3 left owed stand unanswered here, as case 4 leaves
# them stale in its clone - owed either way, which is what 5-7 drive)

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
}

case_answers() {  # case 4, its own clone; 6 record gates, about 10 s alone (2026-11-19)
fixture
# case 3's reword, the state case 4 answers
edit "a short way apart." "a short distance apart."

# 4. answered at this content: quiet; the words move again: the answer is stale and it refuses again
answer_all
( cd "$ROOT" && "$GATE" >/dev/null 2>&1 ); ok $? 0 "answered units ship"
edit "a short distance apart." "a short walk apart."
( cd "$ROOT" && "$GATE" >/dev/null 2>&1 ); ok $? 1 "a stale answer refuses"
}

CASES=(case_answers case_main)
declare -A WEIGHT=([case_answers]=10 [case_main]=5)  # seconds, each alone, measured 2026-11-19
# shellcheck source=/dev/null
source "$HERE/parts.sh"
run_parts 2

printf 'test-entry-gate: %d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
