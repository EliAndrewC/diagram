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
# times by a guard that matched its own analysis text; `tests/hooks/test-pair-hooks.sh` carries that case.
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
  python3 "$PAIR_HERE/../reviews/review_owed.py" --root "$CLONE_ROOT" 2>/dev/null | tr '\n' ' ' | sed 's/ $//'
}
# GUARD_EDIT_OK: feature 248 (GM 2026-09-14) - ONE MAP PER REVIEW AGENT, EVERY OWED MAP DISPATCHED, AND WHETHER
# THEY RAN IN PARALLEL RECORDED. Feature 247's review was one agent over four maps, serialized: 11 of the
# feature's 36 minutes. The reviewer's contract and docs/reviews.md both said "one map per agent" and were
# disregarded, which is the GM's point: *"the point of the tooling is to make the correct thing happen
# automatically without you or I needing to remember the precise ways to not get it subtly wrong in a costly
# way"*. What a hook CAN do: refuse the wrong shape before the agent starts, hold the turn open until every
# owed map has its own dispatch, and measure the rest. What it cannot: launch an agent, split one call into
# several, or force several calls into one message - so parallelism is recorded, never refused (spec D4).
PARALLEL_SPAN_S=60   # a definition, not a measurement: parallel calls land within seconds, a sequential one is a model turn later

pair_now() { # the clock, injectable ONLY in a fixture (the seams-only-in-a-fixture rule every guard here follows)
  case "$CLONE_ROOT" in
    */test-*|*/tmp.*|/tmp/*) if [ -n "${PAIR_NOW:-}" ]; then printf '%s' "$PAIR_NOW"; return 0; fi ;;
  esac
  date +%s
}

maps_named_by() { # maps_named_by <prompt file> -> the pool maps the dispatch asks a review of (research R5), space-separated
  python3 "$PAIR_HERE/../reviews/review_prereq.py" named --clone "$CLONE_ROOT" --prompt-file "$1" 2>/dev/null | tr '\n' ' ' | sed 's/ $//'
}

record_dispatch() { # record_dispatch <map> <key> -> "" or "parallel <span>" / "serialized <span>" when the last owed map was just dispatched at <key>
  python3 - "$(pairing_file)" "$1" "$2" "$(pair_now)" "$PARALLEL_SPAN_S" $(review_owed_names) <<'PY' 2>/dev/null || true
import json, pathlib, sys
p, name, key, now, span_s, owed = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6:]
try:
    d = json.loads(p.read_text())
except Exception:
    d = {}
disp = d.setdefault("dispatched", {})
def complete():
    return bool(owed) and all(isinstance(disp.get(m), dict) and disp[m].get("key") == key for m in owed)
before = complete()
disp[name] = {"key": key, "at": now}
p.write_text(json.dumps(d, indent=2))
if complete() and not before:
    ats = [int(disp[m]["at"]) for m in owed]
    span = max(ats) - min(ats)
    print(("parallel" if span < span_s else "serialized") + f" {span}")
PY
}

# GUARD_EDIT_OK: feature 294 - THE REVIEW IS FIVE CHECKS, EACH OWED ON ITS OCCASION (GM 2026-10-01: the glyph check is
# "a category of thing"; research R1 sorts every check). Every branch that asked about `settlement-review` alone now asks
# about any of the five, and what it counts is an owed UNIT (`<check>:<subject>`, `review_owed.py`), not a moved map.
REVIEW_AGENTS="settlement-review building-review glyph-check size-audit fix-check"
REVIEW_AGENTS_RE="settlement-review|building-review|glyph-check|size-audit|fix-check"
is_review_agent() { case " $REVIEW_AGENTS " in *" $1 "*) return 0 ;; esac; return 1; }

# GUARD_EDIT_OK: feature 164 - this guard now REWRITES the gate into the paired command, so it needs
# the shared matcher beside it and the firing log.
PAIR_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$PAIR_HERE/lib/guardlog.sh"

pairing_file() { printf '%s/.git/pairing-state.json' "${CLONE_ROOT:-.}"; }

engine_key() { # the working tree's engine key, or "" when it cannot be computed
  # THROUGH MAKE, because the engine refuses a bare interpreter (feature 127) - and cached, because the
  # Stop hook asks on every turn and the key costs ~0.4 s to compute. The cache is invalidated by the
  # clone's own index+worktree mtimes, so an edit re-keys it and a quiet turn does not pay.
  local skill="${CLONE_ROOT}" cache="${CLONE_ROOT}/.git/pairing-key" stamp
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

# GUARD_EDIT_OK: feature 294 US6 - a review is dispatched on a GREEN gate for this content, never beside a running one:
# a gate that went red mid-review cost ~36 NOT-REVIEWABLE runs (research R0). Green is the gate stamp, as the reviewer's
# own `make review-paired-gate` reads it; the verification record is the fallback where no stamp script exists.
gate_green() { # gate_green <key> - a green gate has seen exactly this content
  local key="$1"
  [ -n "$key" ] || return 1
  # GUARD_EDIT_OK: feature 294 - the stamp alone when it exists: the verification record is last-event-wins, so a green
  # `make test-file` would read as a gate (feature 240's note on `gate_state`)
  if [ -f "${CLONE_ROOT}/scripts/gates/gate-stamp.py" ]; then
    ( cd "${CLONE_ROOT}" 2>/dev/null && python3 "${CLONE_ROOT}/scripts/gates/gate-stamp.py" --fresh diagram >/dev/null 2>&1 )
    return $?
  fi
  [ "$(read_field "${CLONE_ROOT}/.git/verification-state.json" engine_key)" = "$key" ]
}

# GUARD_EDIT_OK: feature 294 FR-009 - the rounds a unit has had in the active feature: one per distinct engine key it was
# dispatched at, kept in .git/review-rounds.json as {feature: {unit: [keys]}}.
round_number() { # round_number <unit> <key> -> the round this dispatch would be
  python3 - "${CLONE_ROOT}/.git/review-rounds.json" "${CLONE_ROOT}/.specify/feature.json" "$1" "$2" <<'PY' 2>/dev/null || echo 0
import json, pathlib, sys
rec, pointer, unit, key = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3], sys.argv[4]
try:
    feature = json.loads(pointer.read_text()).get("feature_directory", "") or "none"
except Exception:
    feature = "none"
try:
    d = json.loads(rec.read_text())
except Exception:
    d = {}
# GUARD_EDIT_OK: feature 374 batch 4, the round arbiter's tooling fix - A LANDED BATCH'S ROUNDS ARE SPENT, NOT COUNTED: a feature
# that lands batch by batch keeps its rounds per unit, so a sheet reviewed twice in batch 1 and revised again in batch 4 met the
# cap on its first review of the new layout. A round is kept as `key@epoch`; one dispatched before the feature's tasks.md last
# landed on origin/main belonged to a landed batch. A bare key (before this fix) still counts.
import subprocess
try:
    landed = int(subprocess.run(["git", "-C", str(rec.parent.parent), "log", "-1", "--format=%ct", "origin/main", "--", f"{feature}/tasks.md"], capture_output=True, text=True).stdout.strip() or 0)
except Exception:
    landed = 0
# GUARD_EDIT_OK: feature 374 batch 5, the round arbiter's tooling fix - a bare key (kept before the epoch fix) reads as epoch 0, so
# it is spent once the feature's tasks.md has landed at all: batch 4's bare keys counted into batch 5, its first round read as round 5
live = [k for k in d.get(feature, {}).get(unit, []) if (int(k.rsplit("@", 1)[1]) if "@" in k else 0) >= landed]
keys = [k.split("@", 1)[0] for k in live]
print(len(keys) + (0 if key in keys else 1))
PY
}
record_round() { # record_round <unit> <key> - count this dispatch's round
  python3 - "${CLONE_ROOT}/.git/review-rounds.json" "${CLONE_ROOT}/.specify/feature.json" "$1" "$2" <<'PY' 2>/dev/null || true
import json, pathlib, sys
rec, pointer, unit, key = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3], sys.argv[4]
try:
    feature = json.loads(pointer.read_text()).get("feature_directory", "") or "none"
except Exception:
    feature = "none"
try:
    d = json.loads(rec.read_text())
except Exception:
    d = {}
import time
keys = d.setdefault(feature, {}).setdefault(unit, [])
if key not in [k.split("@", 1)[0] for k in keys]:
    keys.append(f"{key}@{int(time.time())}")
rec.write_text(json.dumps(d, indent=1))
PY
}

# GUARD_EDIT_OK: feature 294 US6 - gate_running_or_fresh retired: a review no longer runs beside a gate (gate_green above)
log_bypass() { # the override's reason, where `make bypass-audit` reads it
  local why="$1" what="$2"
  local dir="${CLONE_ROOT}/dev/bypass-log"
  [ -d "$dir" ] || return 0
  dir="$dir/$(date -u +%Y-%m)"; mkdir -p "$dir" 2>/dev/null || return 0   # GUARD_EDIT_OK: 2026-10-02 - a month folder, as every log writer
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
  # actually being launched; `tests/hooks/test-pair-hooks.sh` now proves both directions.
  atype="$(printf '%s' "$payload" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("subagent_type",""))' 2>/dev/null)"
  dir="$(printf '%s' "$payload" | python3 -c '
import json, pathlib, sys
d = json.load(sys.stdin)
tp = d.get("transcript_path") or ""
sid = d.get("session_id") or ""
print(str(pathlib.Path(tp).parent / sid / "subagents") if tp and sid else "")
' 2>/dev/null)"
  key="$(engine_key)"

  # GUARD_EDIT_OK: the round arbiter's tooling fix on hour:374@2 (feature 383) - THE STEP-BACK FIRES ON THE HOUR: past it, a
  # gate or an agent dispatch is refused until `make step-back` opens the hour (the round arbiter's own dispatch passes), so
  # an hour is reviewed as an hour and not only when the feature next ticks (batch 17's ran 216 minutes).
  if { [ "$tool" = "Bash" ] && is_gate_invocation "$cmd"; } || [ "$tool" = "Agent" ]; then
    local due_why
    due_why="$(python3 "$CLONE_ROOT/scripts/reviews/checkpoint.py" due --root "$CLONE_ROOT" --tool "$tool" --agent "$atype" 2>/dev/null)"
    if [ -n "$due_why" ]; then
      guard_log pair refused "$tool ${atype:-$cmd}" step-back-due
      printf '\n\033[1mBLOCKED: %s\033[0m\n' "$due_why" >&2
      exit 2
    fi
  fi

  if [ "$tool" = "Bash" ] && is_gate_invocation "$cmd"; then
    # GUARD_EDIT_OK: feature 383 FR-003 - the gate's PAIR_OK waiver is retired with the stop branch, its only reader: with
    # nothing owed at a gate's start there is nothing for it to waive (a review dispatch's own PAIR_OK, below, stays).
    # GUARD_EDIT_OK: feature 383 FR-003 (the GM 2026-10-12: "why are we comparing our stuff to main when we're not ready to
    # land there?") - THE GATE RUNS AS TYPED. A review comes due on the feature's hour (the checkpoint, `make tick`'s hold) or
    # at the landing (review-gate.sh), never at a gate's start: the rewrite into `make verify`, the permit naming the owed
    # units and the snapshot taken here are retired with the stop branch's demand that a green gate's turn dispatch them.
    # `make verify` still writes the snapshot and one prompt per owed unit, and the checkpoint and the push name it.
    [ -n "$key" ] && write_pairing "$(pairing_file)" gate_key "$key"
    guard_log pair permitted "$cmd" gate-as-typed
    exit 0
  fi

  if [ "$tool" = "Agent" ] && is_review_agent "$atype"; then
    # GUARD_EDIT_OK: feature 248 FR-001 - A DISPATCH ASKS FOR EXACTLY ONE UNIT (one map, before feature 294), refused
    # BEFORE the agent starts, with no escape token - a multi-unit review is never the right shape. The refusal hands
    # back the per-unit prompt files `make verify` (or the permit branch above) wrote, one Agent call each.
    # GUARD_EDIT_OK: feature 294 - every one of the five checks is held to the same shape, the same prerequisites, a
    # GREEN gate (not a running one: US6, a NOT-REVIEWABLE outcome never costs a run) and a cap of two rounds per unit
    # per feature (FR-009); past it the round arbiter rules (GUARD_EDIT_OK: feature 379 FR-010 retired the GM's-words waiver).
    ptext="$(printf '%s' "$payload" | python3 -c 'import json,sys; print((json.load(sys.stdin).get("tool_input") or {}).get("prompt") or "")' 2>/dev/null)"
    # GUARD_EDIT_OK: feature 375 FR-003(a) - DECIDE FIRST: a review check waits for its task's decisions' verdict
    decide_why="$(printf '%s' "$ptext" | python3 -c 'import re,sys; m=re.search(r"\bDECIDE_OK=\"([^\"]*)\"", sys.stdin.read()); r=m.group(1) if m else ""; print(r if len(r.split())>=2 and len(r)>=8 else "")' 2>/dev/null)"
    if [ -n "$decide_why" ]; then
      guard_log pair escaped "$decide_why" decide-ok
    else
      why="$(python3 "$PAIR_HERE/../gates/plan_gate.py" decided "${CLONE_ROOT:-.}" 2>/dev/null)"
      if [ -n "$why" ]; then
        # GUARD_EDIT_OK: feature 385 T22 - the refusal names the check and its unit, so a batch of identical refusals is counted right
        printf '\nBLOCKED: %s on %s: %s\n(or DECIDE_OK="<reason>" in the prompt; scripts/hooks/pair-hooks.sh, feature 375)\n' "$atype" "$(printf '%s' "$ptext" | grep -oE '[^ `"]*/MANIFEST\.md|/tmp/l7r-check/[^ `")]*' | head -1 | grep . || echo 'its prompt')" "$why" >&2
        guard_log pair blocked "$atype" decide-first
        exit 2
      fi
    fi
    nf="$(mktemp)"; printf '%s' "$ptext" > "$nf"
    named="$(maps_named_by "$nf")"; rm -f "$nf"
    if [ "$(printf '%s\n' $named | grep -c .)" -gt 1 ]; then
      printf '\n\033[1mBLOCKED: this %s asks for %s units in ONE agent - one unit per agent, all in this same message.\033[0m\n' "$atype" "$(printf '%s\n' $named | grep -c .)" >&2
      printf 'The sweeps share no work across maps, so one agent serializes them (feature 247: four maps, 11 of 36 minutes).\n' >&2
      printf 'Dispatch one agent per unit now, each with the contents of its prompt file:\n' >&2
      for m in $named; do
        pf="${CLONE_ROOT}/.git/review-snapshot/$m/dispatch.md"
        if [ -f "$pf" ]; then printf '    %s\n' "$pf" >&2; else printf '    %s: no prompt file (not owed, or the snapshot was never taken - `make verify` writes it)\n' "$m" >&2; fi
      done
      printf 'There is no escape for this shape (feature 248 D1).\n' >&2
      guard_log pair blocked "$atype" review-multi-map
      exit 2
    fi
    # GUARD_EDIT_OK: feature 375 amendment 9, FR-040 (the GM 2026-10-12: glyph-check "run periodically rather than every time a
    # map changes ... once after every hour") - A GLYPH CHECK IS DISPATCHED WHEN IT IS DUE: on the feature's hour, all owed units
    # together, or at landing (`review_owed.py --glyph-gate`); before then it is refused, naming when it comes due.
    glyph_escaped=""
    if [ "$atype" = "glyph-check" ] && [ -n "$named" ] && [ -f "${CLONE_ROOT:-.}/scripts/reviews/review_owed.py" ]; then
      case "$ptext" in
        *GLYPH_DUE_OK=*)
          why="$(printf '%s' "$ptext" | python3 -c 'import re,sys; m=re.search(r"GLYPH_DUE_OK=\"([^\"]*)\"", sys.stdin.read()); print(m.group(1) if m else "")' 2>/dev/null)"
          if [ -z "$why" ] || ! printf '%s' "$why" | python3 "${CLONE_ROOT}/scripts/hooks/lib/hookmatch.py" reason-ok >/dev/null 2>&1; then
            printf '\n\033[1mBLOCKED: GLYPH_DUE_OK needs a REASON\033[0m (two words, eight characters, in quotes) - it is what a later audit reads.\n' >&2
            guard_log pair blocked "$atype" glyph-due-no-reason
            exit 2
          fi
          guard_log pair escaped "$atype" glyph-due-ok
          log_bypass "GLYPH_DUE_OK: $why" "glyph check before its hour"
          glyph_escaped="--escaped"
          ;;
        *)
          for m in $named; do
            if ! early="$(python3 "${CLONE_ROOT}/scripts/reviews/review_owed.py" --root "$CLONE_ROOT" --glyph-gate "$m" 2>/dev/null)"; then
              printf '\n\033[1mBLOCKED: %s\033[0m\n' "$early" >&2
              printf 'Owed glyph units wait for the hour and go out together; `make verify` names them and when they come due.\n' >&2
              printf 'A check that must run now: GLYPH_DUE_OK="<why>" in the dispatch prompt.\n' >&2
              guard_log pair blocked "$atype:$m" glyph-not-due
              exit 2
            fi
          done
          ;;
      esac
    fi
    # GUARD_EDIT_OK: feature 240 FR-003 to FR-006 - A REVIEW ROUND IS NOT SPENT ON AN UNVERIFIED FIX: every finding
    # of the unit's last verdict verified or accepted; every map current and complete; every quoted figure backed. Its
    # escape is REVIEW_PREREQ_OK="<why>", apart from PAIR_OK, which answers a different question.
    if [ -n "${CLONE_ROOT:-}" ] && [ -f "${CLONE_ROOT}/scripts/reviews/review_prereq.py" ]; then
      case "$ptext" in
        *REVIEW_PREREQ_OK=*)
          why="$(printf '%s' "$ptext" | python3 -c 'import re,sys; m=re.search(r"REVIEW_PREREQ_OK=\"([^\"]*)\"", sys.stdin.read()); print(m.group(1) if m else "")' 2>/dev/null)"
          if [ -z "$why" ] || ! printf '%s' "$why" | python3 "${CLONE_ROOT}/scripts/hooks/lib/hookmatch.py" reason-ok >/dev/null 2>&1; then
            printf '\n\033[1mBLOCKED: REVIEW_PREREQ_OK needs a REASON\033[0m (two words, eight characters, in quotes) - it is what a later audit reads.\n' >&2
            guard_log pair blocked "$atype" review-prereq-no-reason
            exit 2
          fi
          guard_log pair escaped "$atype" review-prereq-ok
          log_bypass "REVIEW_PREREQ_OK: $why" "review prerequisites"
          ;;
        *)
          pf="$(mktemp)"; printf '%s' "$ptext" > "$pf"
          green=no
          ( cd "${CLONE_ROOT}" 2>/dev/null && python3 "${CLONE_ROOT}/scripts/gates/gate-stamp.py" --fresh diagram >/dev/null 2>&1 ) && green=yes
          problems="$(python3 "${CLONE_ROOT}/scripts/reviews/review_prereq.py" check --clone "$CLONE_ROOT" --maps "${named:-$(review_owed_names)}" --prompt-file "$pf" --gate-green "$green" 2>&1)"
          rc=$?; rm -f "$pf"
          if [ "$rc" -ne 0 ]; then
            printf '\n\033[1mBLOCKED: this %s would spend its round on work that has not been verified.\033[0m\n' "$atype" >&2
            printf 'A review round costs minutes; each item below costs seconds to fix (feature 240):\n\n' >&2
            printf '%s\n' "$problems" | sed 's/^/  - /' >&2
            printf '\nDeliberately reviewing a map left in this state? Put REVIEW_PREREQ_OK="<why>" in the dispatch prompt.\n' >&2
            guard_log pair blocked "$atype" review-prerequisites-unmet
            exit 2
          fi
          ;;
      esac
    fi
    # GUARD_EDIT_OK: feature 294 FR-009 - AT MOST TWO ROUNDS PER UNIT PER FEATURE: a round is a dispatch at a new engine
    # key; the third waits for the round arbiter (GUARD_EDIT_OK: feature 379 FR-010 retired the GM's-words waiver here).
    if [ -n "$named" ] && [ -n "$key" ]; then
      rounds="$(round_number "$named" "$key")"
      if [ "${rounds:-0}" -gt 2 ]; then
        # GUARD_EDIT_OK: feature 379 amendment 2, FR-010 (the GM 2026-10-10: "things should go to the arbiter at the point where
        # they were previously coming to me") - the GM's-words waiver of this cap is RETIRED: past it the arbiter alone rules.
        case "$ptext" in
          *)
            # GUARD_EDIT_OK: feature 375 FR-011 - past the cap THE ROUND ARBITER rules, not the GM's waiver: each `continue`
            # ruling lifts the cap by one round; `accept` or `process-fault` closes the unit; an unruled third round trips it.
            arb="$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import hm_arbiter as a
from pathlib import Path
root, unit, n = Path(sys.argv[2]), sys.argv[3], int(sys.argv[4])
shut = a.closed(root, f"round:{unit}@")
if shut:
    print(f"closed\tthe round arbiter closed {unit} ({shut}) - what is left is filed; the session does not re-ask (FR-011)")
elif n - 2 > a.continues(root, f"round:{unit}@"):
    a.trip(root, f"round:{unit}@{n}", "round", unit, f"round {n} of a review check")
    print("owed\t" + a.refusal([f"round:{unit}@{n}"], root))  # GUARD_EDIT_OK: feature 375 amendment 2 - a batch at the cap is named as one
else:
    print("continue\t")' "$PAIR_HERE/lib" "${CLONE_ROOT:-.}" "$atype|$named" "$rounds" 2>/dev/null)"
            case "$arb" in
              continue*) guard_log pair permitted "$atype:$named" review-round-arbiter-continue ;;
              *)
                printf '\n\033[1mBLOCKED: round %s of %s for %s in this feature - the cap is two (feature 294 FR-009).\033[0m\n' "$rounds" "$named" "$atype" >&2
                printf '%s\n' "${arb#*$'\t'}" >&2
                guard_log pair blocked "$atype:$named" review-round-cap
                exit 2
                ;;
            esac
            ;;
        esac
      fi
    fi
    # GUARD_EDIT_OK: feature 240 FR-002 - the dispatch records WHICH content it reviews; the agent copies this key
    # into its verdict record, and review-gate.sh reads the verdict at the push (GUARD_EDIT_OK: feature 383 retired the stop branch).
    [ -n "$key" ] && write_pairing "$(pairing_file)" review_dispatch_key "$key"
    # GUARD_EDIT_OK: feature 248 FR-003/FR-004 - a PERMITTED dispatch is recorded (the unit, the key, the clock) on
    # BOTH permitting paths, and its round counted (feature 294).
    dispatched_note() {
      local m span
      [ -n "$named" ] && [ -n "$key" ] || return 0
      for m in $named; do
        # GUARD_EDIT_OK: feature 375 amendment 9, D53/D55 - a glyph dispatch on the hour (or escaped) opens a batch BEFORE its
        # dispatch is stamped, so the batch's own first unit reads as dispatched and the rest stay due
        [ "$atype" = "glyph-check" ] && python3 "${CLONE_ROOT:-.}/scripts/reviews/review_owed.py" --root "${CLONE_ROOT:-.}" --glyph-dispatched "$m" $glyph_escaped >/dev/null 2>&1
        span="$(record_dispatch "$m" "$key")"
        record_round "$m" "$key"
        guard_log pair permitted "$atype:$m" review-dispatched
        case "$span" in
          parallel*)   guard_log pair permitted "$atype:${span#parallel }s" reviews-parallel ;;
          serialized*) guard_log pair permitted "$atype:${span#serialized }s" reviews-serialized ;;
        esac
      done
    }
    case "$prompt" in *PAIR_OK*) guard_log pair escaped "$atype" pair-ok-review; log_bypass "named in the dispatch" "review alone"; dispatched_note; exit 0;; esac
    if gate_green "$key"; then
      dispatched_note
      exit 0
    fi
    printf '\n\033[1mBLOCKED: a %s with no green gate for this content.\033[0m\n' "$atype" >&2
    printf 'A review is dispatched once the gate is GREEN on the content it reviews (feature 294, US6): a gate that\n' >&2
    printf 'goes red under a running review makes the round NOT-REVIEWABLE, and that round is the cost this avoids.\n\n' >&2
    printf '    make verify        # starts the gate and writes the owed prompts; dispatch when it reports green\n\n' >&2
    printf 'Deliberately one-sided? Put PAIR_OK and the reason in the dispatch prompt.\n' >&2
    note="$(fallback_note)"; [ -n "$note" ] && printf '%s\n' "$note" >&2
    guard_log pair blocked "$atype" review-without-gate
    exit 2
  fi
  exit 0
}


# GUARD_EDIT_OK: feature 383 FR-003 - the STOP branch is retired: a turn may end on a green gate with reviews owed, which
# come due on the feature's hour (the checkpoint's hold on `make tick`) or at the landing (review-gate.sh).
# GUARD_EDIT_OK: feature 385 T22 (plan D44; the round arbiter's fix on hour:385-approach-checklist@11) - the turn's end IS held
# for one thing: an Agent dispatch a guard refused that was neither sent again nor recorded dropped (`make dispatch-dropped`).
# Measured: a refused impl-drift was never re-sent and the session idled 5 h "waiting on" it (scripts/hooks/lib/hm_dropped.py).
stop() {
  local payload; payload="$(cat)"
  find_root "$payload"
  [ -n "${CLONE_ROOT:-}" ] || exit 0
  printf '%s' "$payload" | python3 "$PAIR_HERE/lib/hm_dropped.py" stop --root "$CLONE_ROOT" && exit 0
  guard_log pair blocked "stop" dispatch-dropped
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
