#!/usr/bin/env bash
# review-round-hooks.sh - a spec-fidelity round after the first reads the DIFF, by the tooling's hand.
# (GUARD_EDIT_OK: feature 249 - a NEW guard.)
#
# THE DEFECT (GM 2026-09-14). The spec reviewer's contract has said since feature 236 that a round after
# the first reads only the changed passages - the GM's "only rereviewing the new stuff" - and that a
# reviewer not told which passages changed should ASK rather than re-read. On 2026-09-14 two rounds of
# one small spec amendment each read every file end to end (165k and 110k tokens; over half of an
# eleven-minute change), because the session's dispatch handed over the whole spec and whole-spec
# questions. The rule was right and the prompt asked for more than the rule. The GM's ruling:
#
#   "I think that it is okay for subsequent rounds to essentially review the paragraphs that have
#   changed or the items that have changed or what have you. I think that would be much quicker"
#
#   "I want this all to be automatic since instructions are not reliably followed, but things which
#   happen automatically enforced by make files or by tooling such as hooks are more likely to
#   actually be implemented."
#
# WHAT IT DOES. A REWRITE, never a refusal (feature 164's ladder): on a `spec-fidelity` dispatch that is
# a SPEC review (MODE 2 or 3 - a MODE 4 plan review and a MODE 1 exception check pass untouched) of a
# feature this guard has seen before, the prompt is PREPENDED with a preamble - the round number within
# the pass, the previous round's verdict verbatim from the session's own subagent transcripts, the diff
# of the feature directory against the snapshot taken at the previous dispatch, and the instruction to
# read only that plus grep hits - and the session's own prompt follows unchanged. The first dispatch
# takes the snapshot silently. Every branch records; the one refusal is the reason floor every escape
# carries (`REVIEW_ROUND_OK="<reason>"` for a deliberate full re-read).
#
# The decision is `_hm_review_round.py judge` (a function, so the suite and a replay can drive it);
# this file resolves the session's clone, logs the branch and prints what the harness reads.
#
# Modes:
#   pretool (PreToolUse, Agent)   the rewrite / the snapshot / the pass-through, recorded
#   state <clone> <feature>       the round and whether a snapshot exists (the suite reads it)
set -uo pipefail

MODE=${1:-}
RR_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$RR_HERE/_guardlog.sh"

pretool() {
  local clone verdict event rule detail code out err
  INPUT="$(cat)"   # the firing log resolves the session's name from INPUT
  clone="$(printf '%s' "$INPUT" | "$RR_HERE/clone-sync-hooks.sh" resolve 2>/dev/null | tail -1)"
  verdict="$(printf '%s' "$INPUT" | REVIEW_ROUND_CLONE="$clone" python3 "$RR_HERE/_hm_review_round.py" judge 2>/dev/null)" || exit 0
  [ -n "$verdict" ] || exit 0
  event="$(printf '%s' "$verdict" | python3 -c 'import json,sys; v=json.load(sys.stdin); print(v.get("event",""))' 2>/dev/null)"
  [ -n "$event" ] || exit 0
  # one process reads the rest; the verdict is small
  IFS=$'\t' read -r rule code detail < <(printf '%s' "$verdict" | python3 -c 'import json,sys; v=json.load(sys.stdin); print(v.get("rule",""), v.get("exit",0), v.get("detail","").replace("\t"," ").replace("\n"," "), sep="\t")' 2>/dev/null)
  out="$(printf '%s' "$verdict" | python3 -c 'import json,sys; sys.stdout.write(json.load(sys.stdin).get("stdout",""))' 2>/dev/null)"
  err="$(printf '%s' "$verdict" | python3 -c 'import json,sys; sys.stdout.write(json.load(sys.stdin).get("stderr",""))' 2>/dev/null)"
  guard_log review-round "$event" "$detail" "$rule"
  [ -n "$out" ] && printf '%s\n' "$out"
  [ -n "$err" ] && printf '%s' "$err" >&2
  exit "${code:-0}"
}

case "$MODE" in
  pretool) pretool ;;
  state) python3 "$RR_HERE/_hm_review_round.py" state "${2:?clone}" "${3:?feature}" ;;
  *) echo "review-round-hooks: unknown mode '$MODE' (want: pretool | state <clone> <feature>)" >&2; exit 1 ;;
esac
