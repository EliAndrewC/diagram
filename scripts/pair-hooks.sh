#!/usr/bin/env bash
# pair-hooks.sh - THE GATE AND THE INDEPENDENT REVIEW RUN TOGETHER, OR NEITHER RUNS (feature 151).
#
# THE GM, 2026-08-29, after a time audit of feature 150's T55: "is there some way to make [it] happen
# automatically instead of reqiring you to remember it? Like is there a scripted way to have them both
# happen at the same time and that's the only way you can do either of them without some kind of
# override?" The measurement behind the ask: of T55's 79.8 minutes, 33.6 went on waiting for background
# verification, and 17 of those were the settlement-review - which ran LAST because it is dispatched from
# the author's memory rather than by the tooling. The review is not optional and never was (constitution
# I's rationale: the author is not a reliable reviewer of their own output; on 2026-07-27 three city maps
# shipped unreviewed and nothing warned), so the fix is to make the two halves inseparable and let them
# overlap.
#
# WHAT IT ENFORCES
#   - a GATE invocation (`done`, `maps`) with no settlement-review pending in this session and none
#     recorded for this exact engine content: a plain `make done` is REWRITTEN to `make verify`
#     (feature 164); every other shape is RECORDED AND PERMITTED with the DISPATCH NOW context
#     (GUARD_EDIT_OK: feature 212, GM 2026-09-07 - the header follows the pretool branch, which says
#     why, and spec 212 D7 records what a foreground gate costs the pairing); the refusal that used to
#     sit here fired 24 times against 98 waivers, and eleven of its real firings were shapes `verify`
#     cannot take;
#   - a SETTLEMENT-REVIEW dispatch is refused unless a gate is running or freshly green for that content;
#   - a turn may not END with a half-open pairing (a gate went green, no review was dispatched).
#
# THE OVERRIDE, which the GM named: PAIR_OK="<reason>" in the command (or in the agent's prompt). It runs
# the command and writes the reason to dev/bypass-log/ where `make bypass-audit` reads it. A one-sided
# case - a docs-only gate, an unattended idle run - is TAKEN, not carved out: the spec's own fidelity
# review struck a carve-out for exactly this, because an exemption removes the audit line the override
# leaves behind.
#
# WHAT "THE SAME CONTENT" MEANS: `l7r.diagram.ci engine-key worktree` - the project's own key, the one
# `.git/verification-state.json` already records and the gate already short-circuits on. The guard carries
# no second definition, and in particular no ink-diff detector of its own: "no ink change detected" is
# exactly how a pairing quietly becomes a gate running alone.
#
# MATCHES INVOCATIONS, NOT MENTIONS. The time audit that produced this feature was itself blocked three
# times by a guard that matched its own analysis text; `scripts/test-pair-hooks.sh` carries that case.
#
# MODES
#   pretool  (PreToolUse: Bash, Agent)  - the two refusals above
#   stop     (Stop)                     - the half-open pairing, refused once
#   state    (hand use / the test)      - print what the guard currently sees
set -uo pipefail

CLONE_ROOT=""
find_root() { # find_root [payload] - THIS SESSION'S CLONE; the cwd's git root only when nothing resolves
  # GUARD_EDIT_OK: feature 231 - THE GUARD READ THE MIRROR (GM 2026-09-12). On feature 228 the session's
  # shell stood in /diagram, so this guard keyed the MIRROR's tree, read and wrote the mirror's
  # pairing-state.json, found no gate for the clone's content and refused the review `make verify` had
  # just asked for; at turn end, the shell moved by then, it read the clone and fired half-open. The
  # answer is feature 204's: the session's clone from the same resolver the main-tree guard uses (the
  # claim map, then the transcript's last rename, then the sessions json; a subagent resolves to its
  # parent's clone). The cwd stays as the fallback for a payload that names no session.
  local resolved=""
  FELL_BACK_TO_MAIN=""
  if [ -n "${1:-}" ]; then
    resolved="$(printf '%s' "$1" | "$PAIR_HERE/clone-sync-hooks.sh" resolve 2>/dev/null | tail -1 || true)"
  fi
  if [ -n "$resolved" ] && [ -e "$resolved/.git" ]; then
    CLONE_ROOT="$resolved"
    return 0
  fi
  # GUARD_EDIT_OK: feature 231's amendment (GM 2026-09-12) - A FALLBACK ONTO MAIN'S TREE IS DISCLOSED,
  # NEVER SILENT. The resolver answers nothing for an unnamed session, or for a clone claimed but never
  # created; the cwd's git root is then still used, because a guard that cannot resolve a clone must not
  # refuse everything. But when that lands on MAIN's tree, this guard is judging the mirror's content - the
  # exact misreading that refused feature 228's review and then fired half-open on it - so every branch
  # that speaks says so. A clone (a path under `.clones/`) is the normal case and adds nothing.
  CLONE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  case "$CLONE_ROOT" in
    "" | */.clones/*) ;;
    *) [ -d "$CLONE_ROOT/.clones" ] && FELL_BACK_TO_MAIN=1 ;;
  esac
}

#: ONE string, so the five disclosures cannot drift apart (the amendment's spec review, 2026-09-12)
fallback_note() {
  [ -n "${FELL_BACK_TO_MAIN:-}" ] || return 0
  printf 'NOTE: this session'"'"'s clone could not be resolved (an unnamed session, or a clone claimed but never created), so this verdict was judged against MAIN'"'"'s tree, where the shell is standing - not against your work. Ask the GM to /rename this session, or run from your clone, and the pairing will read the right tree.'
}

review_owed_names() { # the maps whose manifest moved against main, space-separated ("" = no review owed)
  # GUARD_EDIT_OK: feature 231 - the ONE scripted answer (GM 2026-09-12: "the thing that determines whether
  # a settlement review is necessary is probably some kind of scripted check"), asked FRESH at every
  # decision point because the gate's own pool phase can move a manifest between its start and the turn's end.
  python3 "$PAIR_HERE/_review_owed.py" --root "$CLONE_ROOT" 2>/dev/null | tr '\n' ' ' | sed 's/ $//'
}
review_owed_why() { python3 "$PAIR_HERE/_review_owed.py" --root "$CLONE_ROOT" --why 2>/dev/null; }
review_snapshot() { # review_snapshot <map>... -> the snapshot lines (feature 231: taken wherever a review is found owed)
  local mirror=""
  case "$CLONE_ROOT" in */.clones/*) mirror="${CLONE_ROOT%%/.clones/*}" ;; esac
  python3 "$PAIR_HERE/_review_snapshot.py" --root "$CLONE_ROOT" ${mirror:+--mirror "$mirror"} "$@" 2>/dev/null | tr '\n' ' '
}

# GUARD_EDIT_OK: feature 164 - this guard now REWRITES the gate into the paired command, so it needs
# the shared matcher beside it and the firing log.
PAIR_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$PAIR_HERE/_guardlog.sh"

pairing_file() { printf '%s/.git/pairing-state.json' "${CLONE_ROOT:-.}"; }

engine_key() { # the working tree's engine key, or "" when it cannot be computed
  # THROUGH MAKE, because the engine refuses a bare interpreter (feature 127) - and cached, because the
  # Stop hook asks on every turn and the key costs ~0.4 s to compute. The cache is invalidated by the
  # clone's own index+worktree mtimes, so an edit re-keys it and a quiet turn does not pay.
  local skill="${CLONE_ROOT}/.claude/skills/diagram" cache="${CLONE_ROOT}/.git/pairing-key" stamp
  [ -d "$skill" ] || return 0
  stamp="$(find "$skill/l7r" "$skill/pool" -name '*.py' -newer "$cache" -print -quit 2>/dev/null || true)"
  if [ -s "$cache" ] && [ -z "$stamp" ]; then
    cat "$cache"
    return 0
  fi
  local key
  key="$( cd "$skill" && make -s engine-key REF=worktree 2>/dev/null | tr -d '[:space:]' )"
  [ -n "$key" ] && printf '%s' "$key" > "$cache"
  printf '%s' "$key"
}

read_field() { # read_field <file> <key> -> value ("" when absent)
  python3 - "$1" "$2" <<'PY' 2>/dev/null || true
import json, sys
try:
    print(json.load(open(sys.argv[1])).get(sys.argv[2], "") or "")
except Exception:
    print("")
PY
}

write_pairing() { # write_pairing <key> <field> <value>
  python3 - "$(pairing_file)" "$2" "$3" <<'PY' 2>/dev/null || true
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
try:
    d = json.loads(p.read_text())
except Exception:
    d = {}
d[sys.argv[2]] = sys.argv[3]
p.write_text(json.dumps(d, indent=2))
PY
}

review_pending() { # a settlement-review agent this session launched that has not finished
  local dir="$1"
  [ -n "$dir" ] && [ -d "$dir" ] || return 1
  local f
  for f in "$dir"/agent-*.jsonl; do
    [ -e "$f" ] || continue
    grep -ql "settlement-review" "$f" 2>/dev/null || continue
    # finished agents carry a final assistant turn with no pending tool_result; agent-stall-hooks.sh
    # owns that determination, so ask IT rather than keeping a second copy of the rule
    local aid; aid="$(basename "$f" .jsonl)"; aid="${aid#agent-}"   # the scanner prints the bare id
    bash "${CLONE_ROOT}/scripts/agent-stall-hooks.sh" pending "$dir" 2>/dev/null | grep -qx "$aid" && return 0
  done
  return 1
}

review_recorded() { # a review already recorded for this exact content
  local key="$1"
  [ -n "$key" ] || return 1
  [ "$(read_field "$(pairing_file)" review_key)" = "$key" ]
}

review_waived() { # the gate ran with PAIR_OK against this exact content, so no review is owed for it
  # THE ESCAPE HAS TO CLEAR THE GUARD IT ESCAPES (2026-08-29, the second time this fired). The stop
  # branch's own message says "record why it is not owed: PAIR_OK=... on your next gate run" - and
  # before this, doing exactly that logged the bypass and changed nothing the stop branch reads, so the
  # hook went on firing and told you to repeat the remedy you had just used. A guard whose documented
  # remedy does not clear it teaches a session to ignore the guard, which is the failure this project's
  # own rule about checking the escape FIRST exists to prevent.
  local key="$1"
  [ -n "$key" ] || return 1
  [ "$(read_field "$(pairing_file)" waived_key)" = "$key" ]
}

gate_running_or_fresh() { # a gate started for this content, or a green record against it
  local key="$1"
  [ -n "$key" ] || return 1
  [ "$(read_field "$(pairing_file)" gate_key)" = "$key" ] && return 0
  [ "$(read_field "${CLONE_ROOT}/.git/verification-state.json" engine_key)" = "$key" ]
}

log_bypass() { # the override's reason, where `make bypass-audit` reads it
  local why="$1" what="$2"
  local dir="${CLONE_ROOT}/.claude/skills/diagram/dev/bypass-log"
  [ -d "$dir" ] || return 0
  python3 - "$dir" "$why" "$what" <<'PY' 2>/dev/null || true
import datetime, hashlib, json, pathlib, sys
d, why, what = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
now = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
rec = {"utc": now, "guard": "pair-hooks", "what": what, "reason": why}
(d / f"{now}-{hashlib.sha256((now + what).encode()).hexdigest()[:6]}.json").write_text(json.dumps(rec, indent=2))
PY
}

# ---- the two refusals ---------------------------------------------------------------------------

INVOKES_GATE='(^|[;&|(]|[[:space:]])make([[:space:]]+[A-Za-z0-9_=./"-]+)*[[:space:]]+(done|maps)([[:space:]]|$)'

is_gate_invocation() { # an INVOCATION of the gate, not a mention of one
  local cmd="$1"
  # strip heredoc bodies and quoted strings: a script that TALKS about the gate is not running it
  local stripped
  stripped="$(printf '%s' "$cmd" | python3 -c '
import re, sys
t = sys.stdin.read()
t = re.sub(r"<<\s*.?(\w+).?.*?\n\1", " ", t, flags=re.S)   # heredocs
t = re.sub(r"\x27[^\x27]*\x27|\"[^\"]*\"", " ", t)          # quoted strings
print(t)
' 2>/dev/null || printf '%s' "$cmd")"
  # GUARD_EDIT_OK: feature 172 - A DRY RUN IS NOT AN INVOCATION. `make -n done` PRINTS the recipe and
  # executes nothing, so it starts no gate and owes no review - and this guard refused one, mine,
  # while I was checking that a recipe was wired up correctly. Same mention-versus-invocation family
  # as the rest: `-n`, `--dry-run`, `--just-print`, `--recon`, and `-q`/`--question`, which only asks
  # whether a target is up to date.
  case " $stripped " in
    *" make -n "*|*" make --dry-run "*|*" make --just-print "*|*" make --recon "*|*" make -q "*|*" make --question "*) return 1 ;;
  esac
  printf '%s' "$stripped" | grep -Eq "$INVOKES_GATE"
}

pretool() {
  local payload tool cmd dir prompt key
  payload="$(cat)"
  INPUT="$payload"   # GUARD_EDIT_OK: feature 231 - the firing log resolves the session's name from INPUT
  find_root "$payload"
  [ -n "$CLONE_ROOT" ] || exit 0
  tool="$(printf '%s' "$payload" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_name",""))' 2>/dev/null)"
  cmd="$(printf '%s' "$payload" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command",""))' 2>/dev/null)"
  prompt="$(printf '%s' "$payload" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get("tool_input",{})))' 2>/dev/null)"
  # THE AGENT TYPE, NOT THE PROMPT TEXT (2026-08-29). This branch used to grep the whole tool_input for
  # "settlement-review", which is a MENTION test rather than an INVOCATION test - the rule this project
  # states for every guard, broken by the guard's own author within a day of writing it. It fired on a
  # `spec-fidelity` dispatch whose prompt merely QUOTED the referent, blocking a spec review that owes no
  # gate at all because there is no map. The subagent type is the one field that says which agent is
  # actually being launched; `scripts/test-pair-hooks.sh` now proves both directions.
  atype="$(printf '%s' "$payload" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("subagent_type",""))' 2>/dev/null)"
  dir="$(printf '%s' "$payload" | python3 -c '
import json, pathlib, sys
d = json.load(sys.stdin)
tp = d.get("transcript_path") or ""
sid = d.get("session_id") or ""
print(str(pathlib.Path(tp).parent / sid / "subagents") if tp and sid else "")
' 2>/dev/null)"
  key="$(engine_key)"

  if [ "$tool" = "Bash" ] && is_gate_invocation "$cmd"; then
    # GUARD_EDIT_OK: feature 169 - an INVOCATION, not a mention. This one was already narrower than
    # its siblings (it demanded the `PAIR_OK=` assignment form), but a command grepping for that
    # string still escaped, and the branch WAIVES the review for this engine key - the most
    # consequential permit of the nine. The prompt-side branch below is deliberately NOT converted:
    # an agent prompt is prose, not a shell command, and the matcher blanks quoted regions, which
    # prose carries for ordinary reasons.
    # GUARD_EDIT_OK: feature 169 - `$payload`, not `$INPUT`. This file names its stdin `payload`;
    # `$INPUT` is empty here, so the waiver branch never fired and four of its own cases went red.
    # Second time in this feature that an escape was silently disabled by the wrong variable name
    # (no-poll's was `$HERE` vs `$NP_HERE`), which is the argument for testing an escape in BOTH
    # directions rather than only checking that mentions are rejected.
    if [ -n "$(printf '%s' "$payload" | "$PAIR_HERE/_hm_escape.py" escape PAIR_OK= 2>/dev/null)" ]; then
      guard_log pair escaped "$cmd" pair-ok-gate
      log_bypass "$(printf '%s' "$cmd" | sed -n 's/.*PAIR_OK=["\x27]\{0,1\}\([^"\x27]*\).*/\1/p')" "gate alone"
      [ -n "$key" ] && write_pairing "$(pairing_file)" waived_key "$key"   # ...and the stop branch honors it
      exit 0
    fi   # GUARD_EDIT_OK: feature 169 - closing the `if` that replaced this branch's `case`/`esac`
    # GUARD_EDIT_OK: feature 231 - NO LAYOUT CHANGE, NO REVIEW (GM 2026-09-12: "if there are no changes to
    # the actual way that the settlement is laid out, then we should not need to re review the settlement").
    # The gate runs as typed - no rewrite to verify, no review owed - when no pool manifest moved against
    # main. Nothing is recorded here: the stop branch asks again after the gate, which may have moved one.
    if [ -z "$(review_owed_names)" ]; then
      [ -n "$key" ] && write_pairing "$(pairing_file)" gate_key "$key"
      guard_log pair permitted "$cmd" review-not-owed
      # GUARD_EDIT_OK: feature 231 - no escaped quotes inside this single-quoted program: the shell keeps the
      # backslashes and python then refuses the line (the suite caught it). The reason arrives as an env var.
      # GUARD_EDIT_OK: feature 231's amendment - this branch carries the fallback disclosure, and an
      # APOSTROPHE inside the single-quoted program below closes it (the suite caught that too), so no
      # comment inside these python blocks carries one.
      PAIR_WHY="$(review_owed_why)" PAIR_NOTE="$(fallback_note)" python3 -c '
import json, os
why, note = os.environ["PAIR_WHY"], os.environ.get("PAIR_NOTE", "")
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": (
        "NO SETTLEMENT-REVIEW OWED: " + why + " (feature 231). The gate runs alone - no pool manifest moved, "
        "so a review would re-judge ink that has not changed. A glyph or page change with the same manifest is "
        "the GM to look at rather than the agent: hand the map back and say what moved. The waiver is recorded "
        "at turn end. If this gate MOVES a manifest, the review becomes owed and the stop hook says so."
        + (" " + note if note else "")),
}}))'
      # GUARD_EDIT_OK: feature 231's amendment - the marker moved out of the python block, where an
      # apostrophe would close the shell's own quoting
      exit 0
    fi
    if review_pending "$dir" || review_recorded "$key"; then
      [ -n "$key" ] && write_pairing "$(pairing_file)" gate_key "$key"
      exit 0
    fi
    # GUARD_EDIT_OK: feature 164 - REWRITE INTO THE PAIRED COMMAND INSTEAD OF REFUSING (GM 2026-08-30).
    # This branch named `make verify` in its own refusal and then spent a model round trip asking the
    # session to type it. `make verify` IS this gate plus the line that dispatches the review, so the
    # substitution is exact: the gate still runs, the pairing rule is unchanged, and what used to not
    # happen at all now happens correctly. Measured cause: 13 firings, 7 of them escaped with PAIR_OK
    # in the very next call. Only a plain `make done` converts - `_hm_make.py as-paired` declines
    # FULL, a second goal, or a command `gate-hooks` is already combining, because two rewrites racing
    # for one command would make the outcome depend on hook order.
    PAIRED=$(printf '%s' "$payload" | "$PAIR_HERE/_hm_make.py" as-paired 2>/dev/null || true)
    if [ -n "$PAIRED" ]; then
      guard_log pair rewrote "$cmd"
      # GUARD_EDIT_OK: feature 231's amendment - this branch carries the fallback disclosure
      printf '%s' "$payload" | REWRITTEN="$PAIRED" PAIR_NOTE="$(fallback_note)" python3 -c '
import json, os, sys
payload = json.load(sys.stdin).get("tool_input", {})
payload["command"] = os.environ["REWRITTEN"]
note = os.environ.get("PAIR_NOTE", "")
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "updatedInput": payload,
    "additionalContext": (
        "Rewritten to `make verify`: the same gate, started together with the review it owes. "
        "DISPATCH THE settlement-review IN THIS SAME TURN - verify prints which maps changed and "
        "then runs the gate in the background, so the review is not sitting on the critical path. "
        "If no review is owed for this delta, re-issue with PAIR_OK=\"<why>\" and the reason is "
        "logged." + (" " + note if note else "")),
}}))'
      # GUARD_EDIT_OK: feature 231's amendment - the fallback disclosure on the rewrite branch
      exit 0
    fi
    # GUARD_EDIT_OK: feature 212 - EVERY OTHER SHAPE IS RECORDED AND PERMITTED, NOT REFUSED (GM
    # 2026-09-07: "anytime we are able to say that a command was run incorrectly and then supply the
    # correct thing to do ... simply do the correct thing and then inform the session through hook
    # context that we have done it"). The census (specs/212 R1) found the rewrite above fired ONCE
    # while every real refusal since - eight `make maps`, three detached `make done` - was a shape
    # `verify` cannot take; the record for this branch was 24 refusals and 98 PAIR_OK waivers. What
    # `make verify` adds to the gate is two writes and a printf, so the hook does those itself and
    # lets the command run unchanged. A DETACHED run returns at once and the review overlaps the gate
    # exactly as under verify; a FOREGROUND run returns when the gate does, so the context says the
    # review will follow it and how to overlap them next time (spec D7 - the one place this changes
    # what feature 151 delivers, to be raised with the GM). The Stop hook is the backstop as before:
    # a turn may not end on the gate green with no review dispatched.
    [ -n "$key" ] && write_pairing "$(pairing_file)" gate_key "$key"
    guard_log pair permitted "$cmd" review-owed
    # GUARD_EDIT_OK: feature 231 - the maps from the one scripted answer (it used to be a HEAD~1 diff, which
    # saw only the last commit), and the reviewer's snapshot TAKEN HERE for the gate shapes verify cannot
    # take (GM 2026-09-12: "it should not be on you to remember to do that").
    maps="$(review_owed_names)"
    snap="$(review_snapshot $maps)"
    bg="$(printf '%s' "$payload" | python3 -c 'import json,sys; print("yes" if (json.load(sys.stdin).get("tool_input") or {}).get("run_in_background") else "")' 2>/dev/null)"
    detached=""
    case " $(printf '%s' "$cmd" | tr '\n' ' ') " in
      *" nohup "*|*" setsid "*|*"& "*|*"&) "*|*"&;"*) detached=yes ;;
    esac
    [ -n "$bg" ] && detached=yes
    # GUARD_EDIT_OK: feature 231 - the permit's context names the snapshot directories the reviewer reads
    # GUARD_EDIT_OK: feature 231's amendment - this branch carries the fallback disclosure
    printf '%s' "$payload" | PAIR_MAPS="${maps:-the delta}" PAIR_KEY="${key:0:12}" PAIR_DETACHED="$detached" PAIR_SNAP="$snap" PAIR_NOTE="$(fallback_note)" python3 -c '
import json, os, sys
maps, key, detached = os.environ["PAIR_MAPS"], os.environ["PAIR_KEY"], os.environ["PAIR_DETACHED"]
snap = os.environ["PAIR_SNAP"].strip()
maps = f"{maps} - review the SNAPSHOT, the gate evicts the pool renders: {snap}" if snap else maps
how = ("This run is detached, so it returns now and the review overlaps the gate."
       if detached else
       "This gate runs in the FOREGROUND, so you read this only when it returns and the review will "
       "start AFTER it, adding its whole runtime to the wall clock. To overlap them next time, detach "
       "the gate (`setsid nohup make ... > <log> 2>&1 &` - run_in_background reaps `make maps`) or use "
       "`make verify` for a plain gate.")
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": (
        f"GATE PERMITTED WITH A REVIEW OWED (engine key {key}). The gate and the independent "
        f"settlement-review run TOGETHER (GM 2026-08-29). DISPATCH NOW, in the same turn: "
        f"settlement-review over {maps}. {how} A turn may not end with this gate green and no review "
        f"dispatched. One-sided case (docs, tests, a guard script)? Say so: "
        f"PAIR_OK=\"<why this needs no review>\" <command> - the reason lands in dev/bypass-log/."
        + (" " + os.environ["PAIR_NOTE"] if os.environ.get("PAIR_NOTE") else "")),
}}))'
    # GUARD_EDIT_OK: feature 231's amendment - the fallback disclosure on the permit branch
    exit 0
  fi

  if [ "$tool" = "Agent" ] && { [ "$atype" = "settlement-review" ] || [ "$atype" = "building-review" ]; }; then
    # GUARD_EDIT_OK: feature 168 - the escape is recorded as well as logged to the bypass log; the two
    # answer different questions (that one carries the REASON, this one makes the RATE computable).
    # GUARD_EDIT_OK: feature 231 - AN ESCAPED REVIEW IS STILL A REVIEW: it records review_key as the normal
    # branch does, so the stop branch does not fire half-open on a review that actually ran (feature 228).
    case "$prompt" in *PAIR_OK*) guard_log pair escaped "$atype" pair-ok-review; log_bypass "named in the dispatch" "review alone"; [ -n "$key" ] && write_pairing "$(pairing_file)" review_key "$key"; exit 0;; esac
    if gate_running_or_fresh "$key"; then
      [ -n "$key" ] && write_pairing "$(pairing_file)" review_key "$key"
      exit 0
    fi
    printf '\n\033[1mBLOCKED: a settlement-review with no gate beside it.\033[0m\n' >&2
    printf 'Neither half runs alone (GM 2026-08-29). No gate is running for this content and no green\n' >&2
    printf 'record matches it, so the review would be adjudicating a map the suite has not checked.\n\n' >&2
    printf '    make verify        # starts the gate, then dispatch the review in the same turn\n\n' >&2
    printf 'Deliberately one-sided? Put PAIR_OK and the reason in the dispatch prompt.\n' >&2
    note="$(fallback_note)"; [ -n "$note" ] && printf '%s\n' "$note" >&2   # GUARD_EDIT_OK: 231's amendment
    guard_log pair blocked "$atype" review-without-gate   # GUARD_EDIT_OK: feature 168
    exit 2
  fi
  exit 0
}

stop() {
  local payload dir key
  payload="$(cat)"
  INPUT="$payload"   # GUARD_EDIT_OK: feature 231 - the firing log resolves the session's name from INPUT
  find_root "$payload"
  [ -n "$CLONE_ROOT" ] || exit 0
  key="$(engine_key)"
  dir="$(printf '%s' "$payload" | python3 -c '
import json, pathlib, sys
d = json.load(sys.stdin)
tp, sid = d.get("transcript_path") or "", d.get("session_id") or ""
print(str(pathlib.Path(tp).parent / sid / "subagents") if tp and sid else "")
' 2>/dev/null)"
  [ -n "$key" ] || exit 0
  # a gate ran green against this content, and nothing reviewed it
  [ "$(read_field "${CLONE_ROOT}/.git/verification-state.json" engine_key)" = "$key" ] || exit 0
  review_recorded "$key" && exit 0
  review_pending "$dir" && exit 0
  review_waived "$key" && exit 0
  # GUARD_EDIT_OK: feature 231 - NO LAYOUT CHANGE, NO REVIEW, asked again AFTER the gate (its pool phase may
  # have moved a manifest): nothing moved -> the automatic waiver is recorded against this content, with its
  # reason, once, so make audit can count how often a review was waived by the script rather than a person.
  if [ -z "$(review_owed_names)" ]; then
    write_pairing "$(pairing_file)" waived_key "$key"
    write_pairing "$(pairing_file)" waived_why "$(review_owed_why)"
    guard_log pair permitted "stop" review-not-owed
    exit 0
  fi
  [ "$(read_field "$(pairing_file)" stop_told)" = "$key" ] && exit 0   # once per content, never a loop
  write_pairing "$(pairing_file)" stop_told "$key"
  printf 'PAIRING HALF-OPEN: the gate went green on this content and no settlement-review looked at it.\n' >&2
  printf 'Dispatch one now, or record why it is not owed: PAIR_OK="<reason>" on your next gate run.\n' >&2
  note="$(fallback_note)"; [ -n "$note" ] && printf '%s\n' "$note" >&2   # GUARD_EDIT_OK: 231's amendment
  guard_log pair blocked "stop" half-open-pairing   # GUARD_EDIT_OK: feature 168
  exit 2
}

state() {
  find_root
  local key; key="$(engine_key)"
  printf 'clone       %s\n' "${CLONE_ROOT:-<none>}"
  printf 'engine key  %s\n' "${key:0:12}"
  printf 'gate key    %s\n' "$(read_field "$(pairing_file)" gate_key | cut -c1-12)"
  printf 'review key  %s\n' "$(read_field "$(pairing_file)" review_key | cut -c1-12)"
  printf 'recorded    %s\n' "$(read_field "${CLONE_ROOT}/.git/verification-state.json" engine_key | cut -c1-12)"
}

case "${1:-}" in
  pretool) pretool ;;
  stop) stop ;;
  state) state ;;
  *) printf 'usage: pair-hooks.sh pretool|stop|state\n' >&2; exit 64 ;;
esac
