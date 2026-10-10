#!/usr/bin/env bash
# claims-file-hooks.sh - the research claims sign-up sheet is claimed and asked through `make research-claim` /
# `make research-claims`, never opened by hand. (GUARD_EDIT_OK: feature 376 FR-002 - a NEW guard, the GM 2026-10-10.)
#
# WHY (the GM, 2026-10-10, specs/376-research-group-fixed-costs/request.md): "any time we have a process that requires
# editing a potentially large file, then we should use tooling to edit the file. And this is basically the same
# sensibility that is why we have a make target for doing a task tick". The sheet (/diagram/.clones/RESEARCH-CLAIMS.md)
# had grown to 1,138 lines, and a check by page name returned a median of 4,147 characters, carried on every later turn.
#
# WHAT IS REFUSED: a Read, Edit or Write of the sheet, and a Bash command that ACTS on it - its path as an operand of a
# command that reads or writes it (`cat`, `>>`, `sed`, `make lines`, `make append`, ...). A command that only MENTIONS
# it - a grep over the docs for its name, a git commit whose message names it - passes: guards match invocations, not
# mentions (the plan review of 376). The two make targets never name it on their command line, so they pass.
#
# ESCAPE: none (GUARD_EDIT_OK: the plan review of 376 - FR-002 refuses these routes with no carve-out, and no repair
# needs one: the tool only appends, reads every old line, its lock releases with its process, and a wrong claim is
# released through it).
#
# Wired from .claude/settings.json on Bash|Read|Edit|Write|NotebookEdit. Tested by test-claims-file-hooks.sh.

set -u
MODE="${1:-}"
INPUT=$(cat 2>/dev/null || true)
[ "$MODE" = "pretool" ] || exit 0
case "$INPUT" in *RESEARCH-CLAIMS*) ;; *) exit 0 ;; esac

CF_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$CF_HERE/lib/guardlog.sh"

HIT=$(printf '%s' "$INPUT" | python3 -c '
import json, re, sys
try:
    p = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti, tool = p.get("tool_input") or {}, p.get("tool_name") or ""
if tool in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit"):
    if "RESEARCH-CLAIMS" in str(ti.get("file_path") or ti.get("notebook_path") or ""):
        print(tool)
elif tool == "Bash":
    cmd = str(ti.get("command") or "")
    # the sheet as a FILE operand: its name with .md, alone or at the end of a path
    path = re.compile(r"(?:^|[\s\x27\x22=<>])(?:\S*/)?RESEARCH-CLAIMS\.md(?![\w.-])")
    verb = re.compile(r"(?:^|[\s;&|(])(?:cat|head|tail|less|more|sed|awk|grep|egrep|rg|tee|cp|mv|rm|wc|vi|vim|nano|python3?|perl|truncate|touch)\b|>|<|make\s+(?:lines|append)\b")
    for piece in re.split(r"&&|\|\||;|\n", cmd):
        # GUARD_EDIT_OK: plan review round 2 - a grep or rg searching FOR the name names it as its PATTERN, not a file:
        # its first non-option argument is dropped before the sheet is looked for
        words = piece.split()
        if words and words[0] in ("grep", "egrep", "rg"):
            rest = [w for w in words[1:] if not w.startswith("-")]
            if rest:
                piece = piece.replace(rest[0], " ", 1)
        if path.search(piece) and not re.match(r"\s*git\b", piece) and verb.search(path.sub(" ", piece)):
            print("Bash")
            break
' 2>/dev/null || true)
[ -n "$HIT" ] || exit 0

{
  printf '\n\033[1mBLOCKED: the research claims sheet is not opened by hand (%s).\033[0m\n' "$HIT"
  printf '\nAsk and claim through the tool - it prints only the claims on your questions, and records under a lock:\n'
  printf '  make research-claims Q="0060 0246"                        who holds these questions now\n'
  printf '  make research-claim Q="0060 0246" FEATURE=<n>             claim them (refused if another session holds one)\n'
  printf '  make research-claim Q="0060 0246" FEATURE=<n> STATUS=done  release them when the work is done\n'
  printf '  make research-claim Q=0060 FEATURE=<n> RELEASE=<owner> WHY="<why it is stale>"   free a stale claim\n'
  printf '\nThe GM, 2026-10-10: any time a process requires editing a potentially large file, it uses tooling to edit it.\n'
  printf 'There is no escape variable: the tool reads every old line and releases any claim, so nothing needs the file.\n\n'
} >&2
guard_log claims-file blocked "$HIT" hand-edit-of-claims-sheet
exit 2
