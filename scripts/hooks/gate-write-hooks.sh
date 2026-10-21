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
# WHAT IT LETS THROUGH (GUARD_EDIT_OK: feature 405 T41, plan D15 - the GM, 2026-10-21, proposal E: the gate runs beside the
# claims round): a change the gate does not see - a claim docstring or comment in an engine file (the AST the gate's own key
# hashes is unchanged), or the claims round's records (`preflight.unseen`). So `make claims-checked`, `make claims-triaged` and
# `make append` pass; a `git add`/`git commit` passes when the tree, against the gate's snapshot, holds only such changes; an
# Edit or Write passes when its result would be one. T14's claims round voided a running gate and was refused its records.
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

WHAT=$(printf '%s' "$INPUT" | GW_TOP="$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)" GW_SNAP="$(git rev-parse --absolute-git-dir 2>/dev/null)/gate-tree.json" python3 -c '
import json, os, re, sys
try:
    p = json.load(sys.stdin)
except Exception:
    sys.exit(0)
tool, ti, top = p.get("tool_name", ""), p.get("tool_input") or {}, os.environ["GW_TOP"]
import subprocess, tempfile
pre = [sys.executable, os.path.join(top, "scripts", "gates", "preflight.py"), "--root", top, "--tree-check", os.environ["GW_SNAP"]]
def unseen(cmd):  # the question the gate itself asks (405 T41, D15): exit 0 when the change is one it does not see
    try:
        return subprocess.run(pre + cmd, capture_output=True, timeout=20).returncode == 0
    except Exception:
        return False
if tool in ("Edit", "Write", "NotebookEdit"):
    f = os.path.realpath(str(ti.get("file_path") or ti.get("notebook_path") or ""))
    if f.startswith(os.path.realpath(top) + os.sep):
        rel = os.path.relpath(f, top)
        new = None
        if tool == "Write":
            new = str(ti.get("content") or "")
        elif tool == "Edit":
            try:
                cur = open(f, encoding="utf-8").read()
                o, n = str(ti.get("old_string") or ""), str(ti.get("new_string") or "")
                new = cur.replace(o, n) if ti.get("replace_all") else cur.replace(o, n, 1)
            except OSError:
                new = None
        ok = False
        if new is not None:
            with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf:
                tf.write(new)
            ok = unseen(["--would-write", rel, "--content", tf.name])
            os.unlink(tf.name)
        if not ok:
            print(f"an {tool} of {rel}")
elif tool == "Bash":
    cmd = str(ti.get("command") or "")
    if re.search(r"\bgit\b[^;&|]*\b(commit|add)\b", cmd):
        if not unseen(["--quiet"]):
            print("a git commit or add of a change the gate sees (it moves HEAD, or what the gate compares against it)")
    else:
        m = re.search(r"\bmake\b[^;&|]*?\b(record-checked|tick|accept)\b", cmd)
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
