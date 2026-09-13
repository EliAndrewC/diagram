#!/usr/bin/env bash
# escalation-hooks.sh - findings do not reach the GM until an independent check has filtered them.
# (GUARD_EDIT_OK: a NEW guard.)
#
# THE DEFECT (GM 2026-09-12). A session sent the GM five "judgment calls" off the back of two
# settlement reviews. Three came back as corrections rather than rulings: two rested on no project
# norm at all - a dwelling count measured against a scoring radius no rule uses as a bar, and a
# distance measured against a maximum that does not exist - and one had already been answered by a
# measurement taken an hour earlier on a layout that no longer existed. The GM:
#
#   "I'm trying to figure out why you keep escalating things to me that when I look at them don't seem
#   like problems because it might be that I simply do not understand why they are problems. And,
#   thus, I'm concerned that I will be ignoring something bad."
#
# That is the cost, and it is not the wasted minute: an escalation that turns out to be nothing
# teaches the GM to doubt their own reading of the ones that matter.
#
# WHY A GUARD AND NOT A THIRD COPY OF THE RULE. The rule existed in TWO places already - the review
# agent's own output contract ("QUESTIONABLE ... needs a RESEARCH PASS - never 'a GM ruling'") and
# constitution XII ("a reviewer writing 'this wants a one-line ruling' has identified a QUESTION, not
# delegated it") - and was disregarded anyway. The GM's ruling on that:
#
#   "If we already had a rule in two places and it was still disregarded, then it sounds like we need
#   another process change. Like maybe when you have findings to escalate to me ... you do a final
#   subagent check on that writeup to check whether what you are about to tell me is actually
#   something that matters so you can edit out all the things I keep having to 'decide' but which are
#   not actual decisions."
#
# So: a review agent's completion ARMS a requirement, and an `escalation-check` dispatch DISARMS it.
# The turn may not close in between. This is the `pair-hooks.sh` shape deliberately - the gate and the
# review run together, neither alone - because it is the one enforcement in this repository that has
# held: it keys on a thing the harness can see (an Agent dispatch) rather than on the session's prose,
# which no hook can read.
#
# WHAT IT DOES NOT DO. It cannot tell whether a turn's final message actually carries findings; the
# trigger is that a REVIEW RAN, which is when findings exist. A review that found nothing to escalate
# still costs one cheap filter pass, and that is the accepted price of an enforcement that works -
# stated here rather than discovered later. A session that genuinely has nothing to filter says so
# through the escape, with its reason, and the reason is audited like every other escape.
#
# ESCAPE: ESCALATION_OK="<reason>" in the dispatch prompt or in a command. Recorded to the guard log
# and to dev/bypass-log/ like every other escape, and it must say WHY (two words, eight characters -
# `_hookmatch.py escape_reason`).
#
# Modes:
#   pretool (PreToolUse, Agent) arm on a review dispatch; disarm on an escalation-check dispatch
#   stop    (Stop) refuse to close a turn with findings unfiltered; once per armed review, never a loop
#   state   print what is armed (the suite and `make audit` use this)
#   arm <clone> <agent>  /  disarm <clone>   seams for the suite, refused outside a fixture
set -uo pipefail
MODE=${1:-}
EH_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$EH_HERE/_guardlog.sh"

# THE AGENTS WHOSE FINDINGS REACH THE GM. Derived from nothing on purpose - it is a short, stated
# roster, and a new reviewer is a deliberate addition here rather than an automatic one, because an
# agent whose output the session does not relay (a source reader, a quote checker) must not arm this.
REVIEW_AGENTS="settlement-review building-review size-audit"
FILTER_AGENT="escalation-check"

state_file() { printf '%s/.git/escalation-state.json' "$1"; }

clone_of() { git -C "${1:-$PWD}" rev-parse --show-toplevel 2>/dev/null; }

read_field() { # read_field <file> <key>
  [ -f "$1" ] || return 0
  python3 -c '
import json, sys
try:
    print((json.load(open(sys.argv[1])) or {}).get(sys.argv[2], "") or "")
except Exception:
    print("")' "$1" "$2" 2>/dev/null
}

write_field() { # write_field <file> <key> <value>
  python3 -c '
import json, os, sys
p, k, v = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    d = json.load(open(p)) or {}
except Exception:
    d = {}
d[k] = v
os.makedirs(os.path.dirname(p), exist_ok=True)
tmp = p + ".tmp"
json.dump(d, open(tmp, "w"))
os.replace(tmp, p)' "$1" "$2" "$3" 2>/dev/null || true
}

arm() {   # arm <clone> <which review>
  write_field "$(state_file "$1")" armed_by "$2"
  write_field "$(state_file "$1")" armed_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  write_field "$(state_file "$1")" told ""
}

disarm() { # disarm <clone>
  write_field "$(state_file "$1")" armed_by ""
  write_field "$(state_file "$1")" told ""
}

pretool() {
  local payload tool atype prompt clone
  payload="$(cat)"
  INPUT="$payload"   # the firing log resolves the session's name from INPUT
  tool="$(printf '%s' "$payload" | python3 -c 'import json,sys; print((json.load(sys.stdin) or {}).get("tool_name","") or "")' 2>/dev/null)"
  [ "$tool" = "Agent" ] || exit 0
  atype="$(printf '%s' "$payload" | python3 -c 'import json,sys; print(((json.load(sys.stdin) or {}).get("tool_input") or {}).get("subagent_type","") or "")' 2>/dev/null)"
  prompt="$(printf '%s' "$payload" | python3 -c 'import json,sys; print(((json.load(sys.stdin) or {}).get("tool_input") or {}).get("prompt","") or "")' 2>/dev/null)"
  clone="$(clone_of)"
  [ -n "$clone" ] || exit 0

  if [ "$atype" = "$FILTER_AGENT" ]; then
    disarm "$clone"
    guard_log escalation permitted "$atype" filter-ran
    exit 0
  fi
  case " $REVIEW_AGENTS " in
    *" $atype "*) ;;
    *) exit 0 ;;
  esac
  # A MENTION IS NOT AN INVOCATION, but an agent PROMPT is prose with no command grammar - the same
  # stated exclusion `pair-hooks.sh` takes for its own agent branch. A substring is the honest test here.
  case "$prompt" in *ESCALATION_OK*) guard_log escalation escaped "$atype" escalation-ok; disarm "$clone"; exit 0;; esac
  arm "$clone" "$atype"
  guard_log escalation armed "$atype" review-dispatched
  # TOLD AT DISPATCH, FREE, so the block below is never the first the session hears of it: an
  # additionalContext on an allowed call costs no round trip, a block costs one (feature 164's ladder).
  printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"A review is running, so its findings will need the escalation-check filter before any of them reach the GM: dispatch `escalation-check` with your DRAFT writeup as the prompt, and it returns keep/cut/rewrite per item with the norms it could not verify. The GM asked for this after three findings reached them that no project norm supported (2026-09-12). If you will relay nothing, say so with ESCALATION_OK=\"<reason>\"."}}'
  exit 0
}

stop() {
  local clone armed key
  INPUT="$(cat)"
  clone="$(clone_of)"
  [ -n "$clone" ] || exit 0
  armed="$(read_field "$(state_file "$clone")" armed_by)"
  [ -n "$armed" ] || exit 0
  key="$(read_field "$(state_file "$clone")" armed_at)"
  [ "$(read_field "$(state_file "$clone")" told)" = "$key" ] && exit 0   # once per armed review, never a loop
  write_field "$(state_file "$clone")" told "$key"
  printf 'FINDINGS UNFILTERED: %s returned and no escalation-check has read what you are about to tell the GM.\n' "$armed" >&2
  printf 'Dispatch `escalation-check` with your draft as the prompt - it cuts the items that name no norm,\n' >&2
  printf 'the ones the record already answers, and your own process narrative ("a bug, then I fixed it").\n' >&2
  printf 'Relaying nothing from this review? Re-dispatch with ESCALATION_OK="<reason>".\n' >&2
  guard_log escalation blocked "stop" findings-unfiltered
  exit 2
}

case "$MODE" in
  pretool) pretool ;;
  stop) stop ;;
  state)
    C="$(clone_of "${2:-$PWD}")"
    printf 'clone     %s\n' "${C:-<none>}"
    printf 'armed by  %s\n' "$(read_field "$(state_file "$C")" armed_by)"
    printf 'armed at  %s\n' "$(read_field "$(state_file "$C")" armed_at)"
    printf 'told      %s\n' "$(read_field "$(state_file "$C")" told)" ;;
  # THE SEAMS ARE FIXTURE-ONLY, the rule every guard with test seams here follows: a real clone must
  # not be armed or disarmed from the command line, or the enforcement is one command away from off.
  arm|disarm)
    case "${2:-}" in
      */test-*|*/tmp.*|/tmp/*) ;;
      *) echo "escalation-hooks: $MODE is a test seam and takes a fixture path" >&2; exit 2 ;;
    esac
    [ "$MODE" = arm ] && arm "$2" "${3:-settlement-review}" || disarm "$2" ;;
  *) exit 0 ;;
esac
