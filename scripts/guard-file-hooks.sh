#!/usr/bin/env bash
# guard-file-hooks.sh - a PreToolUse hook that intercepts edits to the files that ARE the guards
# (feature 127, layer 3).
#
# WHY. Layers 1 and 2 close every workaround tier this project has actually observed. The tiers ABOVE
# those - forge a makefile, edit a guard, disable the hook system - were never reached, and the
# reason is worth stating because it is what this layer preserves: none of them can be presented as
# diligence. `REF_WHY="pre-push verification"` reads as conscientious; quietly weakening the Makefile
# does not.
#
# So this layer is not about stopping a determined operator, which is impossible with a shell. It is
# about making sure the remaining routes stay UNMISTAKABLE - you cannot take one by accident, in a
# hurry, while believing you are being careful.
#
# NOT `.claude/agents/*.md`, deliberately. That was in the first draft of the spec and the fidelity
# reviewer removed it as unrequested: editing an agent definition cannot start a 25-minute run, so it
# bypasses nothing here, and this project has a STANDING PROCEDURE for improving review subagents
# that a reason-prompt would obstruct on every use. A guard with no threat behind it is pure friction,
# and friction is what teaches people to click past guards that matter.
#
# ESCAPE: put GUARD_EDIT_OK in the edit, with a reason. Editing a guard is legitimate - this feature
# does it constantly - and the point is that it be DELIBERATE and visible in the diff, not forbidden.
set -uo pipefail

MODE="${1:-pretool}"
[ "$MODE" = pretool ] || exit 0

INPUT=$(cat)

# GUARD_EDIT_OK: feature 164 - SAY IT WHEN THE FILE IS OPENED, not after the edit is written
# (GM 2026-08-30: *"a tool could ... return additional context"*). Measured: 29 firings of the block
# below, and 28 were followed by the SAME edit again carrying the marker - a round trip each, spent
# telling a session something it could have known before it started writing. A Read of a guard file
# now carries that one line, free, and the refusal stays exactly as it was for anyone who edits
# without it.
TOOL=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_name",""))
except Exception: print("")' 2>/dev/null || true)
if [ "$TOOL" = "Read" ]; then
  printf '%s' "$INPUT" | python3 -c '
import json, re, sys
try:
    path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "") or ""
except Exception:
    raise SystemExit
guard = re.search(r"(/\.claude/skills/diagram/Makefile|/scripts/[\w-]+-hooks\.sh|/\.claude/settings\.json|/dev/switches\.json)$", path)
if guard and not re.search(r"/scripts/test-[\w-]+-hooks\.sh$", path):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": (
            "This is a GUARD file. An edit to it is refused unless the edit itself contains "
            "GUARD_EDIT_OK and a short reason - put the intent in the diff, where the GM reads it. "
            "Say which you are doing: fixing a guard that fires on correct work, adding a guard or "
            "an operation, or making a guard stop blocking something you want (that last one is what "
            "the rule exists to catch)."),
    }}))
' 2>/dev/null || true
  # GUARD_EDIT_OK: feature 164 - the teach-at-Read is recorded too, so its worth is a total
  GF_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  # shellcheck source=/dev/null
  . "$GF_HERE/_guardlog.sh"
  guard_log guard-file reminded "$(guard_cmd)" read-reminder   # GUARD_EDIT_OK: feature 169 - the slug
  # this branch was missing, so the census could not tell the Read reminder (56 firings on
  # 2026-08-30) from the block and the escape. Whether 56/day is too many is a separate question,
  # left to the GM with the census in hand rather than answered here.
  exit 0
fi

read -r FILE NEW <<<"$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try:
    d = json.load(sys.stdin).get("tool_input", {})
    body = (d.get("new_string") or "") + (d.get("content") or "")
    print(d.get("file_path", "*"), "GUARD_EDIT_OK" in body)
except Exception:
    print("* False")')"

# GUARD_EDIT_OK: feature 168 - the escape is recorded (its rate is what this project acts on), and so
# is the refusal below. Nothing about what this guard forbids changes.
GF2_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$GF2_HERE/_guardlog.sh"
# GUARD_EDIT_OK: feature 170 - the marker must carry a REASON, not merely be present. The repository's
# own convention already writes it that way (135 of the tree's occurrences use the colon form), so this
# makes the convention the rule, through the same floor every command guard uses.
if [ "$NEW" = "True" ]; then
  GF_REASON=$(printf '%s' "$INPUT" | "$GF2_HERE/_hm_escape.py" escape-reason GUARD_EDIT_OK 2>/dev/null)
  if [ -z "$GF_REASON" ]; then
    printf 'BLOCKED: GUARD_EDIT_OK with no reason given.\n\n' >&2
    printf 'The marker is what puts your intent in the diff, where the GM reads it - a bare marker puts\n' >&2
    printf 'nothing there. Write it the way the rest of the tree does:\n\n' >&2
    printf '    # GUARD_EDIT_OK: <why this edit to a guard is legitimate>\n\n' >&2
    printf 'Two words and eight characters is the whole bar (GM 2026-08-30, feature 170).\n' >&2
    guard_log guard-file blocked "$FILE" GUARD_EDIT_OK-no-reason
    exit 2
  fi
  guard_log guard-file escaped "$GF_REASON" guard-edit-ok
  exit 0
fi

case "$FILE" in
  */.claude/skills/diagram/Makefile|*/scripts/*-hooks.sh|*/.claude/settings.json) ;;
  # (GUARD_EDIT_OK: feature 132 - the iteration switches are a guard; a hand edit is flagged like any other, the
  #  make targets `ci-off` / `ci-on` / `scope-lock` / `scope-unlock` are the supported write path)
  */.claude/skills/diagram/dev/switches.json) ;;
  *) exit 0 ;;
esac

# A hook editing its own test file is how these get maintained; only the guards themselves are held.
case "$FILE" in */scripts/test-*-hooks.sh) exit 0 ;; esac

cat >&2 <<TAIL
BLOCKED: $FILE is a GUARD, not ordinary source.

The guards are what stop an expensive run being started by picking a different command. Weakening
one silently is the only remaining bypass that does not announce itself, so an edit here has to be
deliberate rather than incidental.

If the edit is legitimate - and it often is, these files get maintained like any other - put
GUARD_EDIT_OK in it with a short reason. That is not a formality: it puts the intent in the diff,
where the GM reads it.

Before you do, check which of these you are actually doing:
  - fixing a guard that fires on correct work        -> legitimate, and important; say so
  - adding a new guard or a new operation            -> legitimate; say so
  - making a guard stop blocking something you want  -> that is the thing this exists to catch

(scripts/guard-file-hooks.sh; feature 127)
TAIL
guard_log guard-file blocked "$FILE" no-marker   # GUARD_EDIT_OK: feature 168
exit 2
