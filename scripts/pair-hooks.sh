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
#   - a GATE invocation (`done`, `maps`) is refused unless a settlement-review is pending in this session,
#     or one has already been recorded for this exact engine content, or `make verify` started it;
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
find_root() { # the clone this command is about: the cwd's git root
  CLONE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
}

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
  printf '%s' "$stripped" | grep -Eq "$INVOKES_GATE"
}

pretool() {
  local payload tool cmd dir prompt key
  payload="$(cat)"
  find_root
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
    case "$cmd" in *PAIR_OK=*)
      log_bypass "$(printf '%s' "$cmd" | sed -n 's/.*PAIR_OK=["\x27]\{0,1\}\([^"\x27]*\).*/\1/p')" "gate alone"
      [ -n "$key" ] && write_pairing "$(pairing_file)" waived_key "$key"   # ...and the stop branch honors it
      exit 0;;
    esac
    if review_pending "$dir" || review_recorded "$key"; then
      [ -n "$key" ] && write_pairing "$(pairing_file)" gate_key "$key"
      exit 0
    fi
    printf '\n\033[1mBLOCKED: the gate and the independent review run TOGETHER.\033[0m\n' >&2
    printf 'No settlement-review is pending in this session and none is recorded for this content.\n' >&2
    printf 'The review catches what the author cannot (four real findings on the last map, one of them\n' >&2
    printf 'a berm about to ship), and dispatched AFTER the gate it adds its whole runtime to the wall\n' >&2
    printf 'clock - 17 minutes of T55 sat there. Start both at once instead:\n\n' >&2
    printf '    make verify        # starts this gate and prints the review to dispatch in the same turn\n\n' >&2
    printf 'One-sided case (docs, tests, a guard script, an unattended run)? Take it deliberately:\n' >&2
    printf '    PAIR_OK="<why this needs no review>" <your command>\n' >&2
    printf '(the reason lands in dev/bypass-log/ where make bypass-audit reads it; GM 2026-08-29)\n' >&2
    exit 2
  fi

  if [ "$tool" = "Agent" ] && { [ "$atype" = "settlement-review" ] || [ "$atype" = "building-review" ]; }; then
    case "$prompt" in *PAIR_OK*) log_bypass "named in the dispatch" "review alone"; exit 0;; esac
    if gate_running_or_fresh "$key"; then
      [ -n "$key" ] && write_pairing "$(pairing_file)" review_key "$key"
      exit 0
    fi
    printf '\n\033[1mBLOCKED: a settlement-review with no gate beside it.\033[0m\n' >&2
    printf 'Neither half runs alone (GM 2026-08-29). No gate is running for this content and no green\n' >&2
    printf 'record matches it, so the review would be adjudicating a map the suite has not checked.\n\n' >&2
    printf '    make verify        # starts the gate, then dispatch the review in the same turn\n\n' >&2
    printf 'Deliberately one-sided? Put PAIR_OK and the reason in the dispatch prompt.\n' >&2
    exit 2
  fi
  exit 0
}

stop() {
  local payload dir key
  payload="$(cat)"
  find_root
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
  [ "$(read_field "$(pairing_file)" stop_told)" = "$key" ] && exit 0   # once per content, never a loop
  write_pairing "$(pairing_file)" stop_told "$key"
  printf 'PAIRING HALF-OPEN: the gate went green on this content and no settlement-review looked at it.\n' >&2
  printf 'Dispatch one now, or record why it is not owed: PAIR_OK="<reason>" on your next gate run.\n' >&2
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
