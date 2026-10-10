#!/usr/bin/env bash
# claims-file-hooks.sh - the research claims sign-up sheet is claimed and asked through `make research-claim` /
# `make research-claims`, never opened by hand. (GUARD_EDIT_OK: feature 376 FR-002 - a NEW guard, the GM 2026-10-10.)
#
# WHY (the GM, 2026-10-10, specs/376-research-group-fixed-costs/request.md): "any time we have a process that requires
# editing a potentially large file, then we should use tooling to edit the file. And this is basically the same
# sensibility that is why we have a make target for doing a task tick". The sheet (/diagram/.clones/RESEARCH-CLAIMS.md)
# had grown to 1,138 lines, and a check by page name returned a median of 4,147 characters, carried on every later turn.
#
# WHAT IS REFUSED: a Read, Edit or Write of the sheet, and any Bash command that names it (`cat`, `>>`, `make lines`,
# `make append`, `sed`, ...). The two make targets never name it on their command line, so they pass.
#
# ESCAPE: CLAIMS_FILE_OK="<reason>" in the command, for a repair of the sheet itself; recorded like every escape.
#
# Wired from .claude/settings.json on Read|Edit|Write and Bash. Tested by test-claims-file-hooks.sh.

set -u
MODE="${1:-}"
INPUT=$(cat 2>/dev/null || true)
[ "$MODE" = "pretool" ] || exit 0
case "$INPUT" in *RESEARCH-CLAIMS*) ;; *) exit 0 ;; esac

CF_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$CF_HERE/lib/guardlog.sh"
if escape_or_refuse claims-file CLAIMS_FILE_OK claims-file-ok "$CF_HERE"; then exit 0; fi

HIT=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: p = json.load(sys.stdin)
except Exception: sys.exit(0)
ti = p.get("tool_input") or {}
tool = p.get("tool_name") or ""
if tool in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit"):
    if "RESEARCH-CLAIMS" in str(ti.get("file_path") or ti.get("notebook_path") or ""): print(tool)
elif tool == "Bash" and "RESEARCH-CLAIMS" in str(ti.get("command") or ""):
    print("Bash")' 2>/dev/null || true)
[ -n "$HIT" ] || exit 0

{
  printf '\n\033[1mBLOCKED: the research claims sheet is not opened by hand (%s).\033[0m\n' "$HIT"
  printf '\nAsk and claim through the tool - it prints only the claims on your questions, and records under a lock:\n'
  printf '  make research-claims Q="0060 0246"                        who holds these questions now\n'
  printf '  make research-claim Q="0060 0246" FEATURE=<n>             claim them (refused if another session holds one)\n'
  printf '  make research-claim Q="0060 0246" FEATURE=<n> STATUS=done  release them when the work is done\n'
  printf '  make research-claim Q=0060 FEATURE=<n> RELEASE=<owner> WHY="<why it is stale>"   free a stale claim\n'
  printf '\nThe GM, 2026-10-10: any time a process requires editing a potentially large file, it uses tooling to edit it.\n'
  printf 'A repair of the sheet itself passes with CLAIMS_FILE_OK="<reason>" in the command.\n\n'
} >&2
guard_log claims-file blocked "$HIT" hand-edit-of-claims-sheet
exit 2
