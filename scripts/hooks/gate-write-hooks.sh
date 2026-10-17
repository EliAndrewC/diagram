#!/usr/bin/env bash
# gate-write-hooks.sh - REFUSE a write to the working tree while this tree's own `make done` runs.
# (GUARD_EDIT_OK: feature 385 T02, plan D13 - a NEW guard, amendment 1's FR-010, the GM 2026-10-17: "a guard, not a reminder".)
#
# WHY. A gate ends by checking that the tree did not move while it ran (`preflight.py --tree-check`: HEAD and the tracked
# files) - a run that saw half of one change and half of another vouches for neither. In T01 of feature 385 the session voided
# two gates this way, the second an hour after the round arbiter named the slip: a ledger row, a fix to the very wait it was
# using. Checklist C6 said "nothing is written while a gate runs"; a reminder did not hold, so this guard does.
#
# WHAT IT REFUSES, only while a `make done` of THIS tree runs (`lib/own-make.sh`): an Edit or Write of a file inside the tree,
# and a Bash command that moves HEAD or what the gate compares - `git commit`, `git add` (a staged new file is in the end check's
# `git diff --name-only HEAD`), and the targets that write tracked files (`make append`,
# the ledger; `make claims-checked` / `claims-triaged`, the claims index; `make record-checked`, a REPLY's filed rows in found.jsonl;
# `make tick`, tasks.md; `make accept`, gm-review.jsonl).
# NOT refused: the record target that writes only under `.git/` (`make modal-triaged`), which moves nothing the gate checks - the
# plan review measured both refusals above (a staged file, a REPLY's append) - and a guard that fires on correct work
# teaches a session to bypass every guard.
#
# ESCAPE: GATE_WRITE_OK="<reason>" in the command (or the edit), recorded like every escape.
#
# Wired from .claude/settings.json for Bash and for Edit|Write. Tested by tests/hooks/test-gate-write-hooks.sh.

set -u
MODE="${1:-}"
INPUT=$(cat 2>/dev/null || true)
[ "$MODE" = "pretool" ] || exit 0

GW_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# the cheap test first: no gate of this tree running, nothing to refuse
"$GW_HERE/lib/own-make.sh" --no-print-directory done >/dev/null 2>&1 || "$GW_HERE/lib/own-make.sh" done >/dev/null 2>&1 || exit 0

# shellcheck source=/dev/null
. "$GW_HERE/lib/guardlog.sh"
if escape_or_refuse gate-write GATE_WRITE_OK gate-write-ok "$GW_HERE"; then exit 0; fi

WHAT=$(printf '%s' "$INPUT" | GW_TOP="$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)" python3 -c '
import json, os, re, sys
try:
    p = json.load(sys.stdin)
except Exception:
    sys.exit(0)
tool, ti, top = p.get("tool_name", ""), p.get("tool_input") or {}, os.environ["GW_TOP"]
if tool in ("Edit", "Write", "NotebookEdit"):
    f = os.path.realpath(str(ti.get("file_path") or ti.get("notebook_path") or ""))
    if f.startswith(os.path.realpath(top) + os.sep):
        print(f"an {tool} of {os.path.relpath(f, top)}")
elif tool == "Bash":
    cmd = str(ti.get("command") or "")
    if re.search(r"\bgit\b[^;&|]*\b(commit|add)\b", cmd):
        print("a git commit or add (it moves HEAD, or what the gate compares against it)")
    else:
        m = re.search(r"\bmake\b[^;&|]*?\b(append|claims-checked|claims-triaged|record-checked|tick|accept)\b", cmd)
        if m:
            print(f"make {m.group(1)} (it writes a tracked record)")
' 2>/dev/null)
[ -n "$WHAT" ] || exit 0

printf '\033[1mBLOCKED (gate-write): %s while this tree'"'"'s `make done` runs.\033[0m\n' "$WHAT" >&2
printf 'A write during the run voids its verdict ("the tree moved while the gate ran") and costs the whole gate again.\n' >&2
printf 'Wait for it: `make verify-wait`, run_in_background - its exit is the notification - then make the change.\n' >&2
printf '(feature 385, plan D13; escape GATE_WRITE_OK="<reason>")\n' >&2
guard_log gate-write blocked "$WHAT" write-during-gate
exit 2
