#!/bin/bash
# new-file-hooks.sh - a new glossary file or registry entry takes a RESERVED prefix (feature 265 FR-010).
# GUARD_EDIT_OK: feature 265 FR-010 - a NEW guard, the GM's request of 2026-09-27 that page queues run in parallel.
#
# THE FAILURE IT PREVENTS. A glossary file (`assets/glossary/NNNN-<term>.json`) and a registry entry
# (`research/sources/010-works-cited/NNNN-<key>.html`) each take "the highest + 10" as their prefix. Two queues doing
# that at once take the same number; feature 250 met the collision twice across one merge. `make reserve` allocates
# under a host-wide lock and writes the file's stub; this makes it the only way a NEW such file appears.
#
# WHAT IS REFUSED. A Write that CREATES a file in either directory, or a shell redirect (`>`, `tee`) naming a
# `NNNN-<name>.json|.html` file that does not exist yet, whose prefix the reservation ledger does not hold. Editing an
# existing file, and a file `make reserve` stubbed, pass. The decision is `scripts/_hm_new_file.py`'s.
#
# ESCAPE: RESERVE_OK="<reason>" in the command.
#
# Modes:
#   pretool (PreToolUse, Write|Bash)   refuse / pass, recorded
set -uo pipefail

MODE=${1:-}
NF_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$NF_HERE/_guardlog.sh"

pretool() {
  local verdict kind key
  INPUT="$(cat)"
  verdict="$(printf '%s' "$INPUT" | python3 "$NF_HERE/_hm_new_file.py" 2>/dev/null)" || exit 0
  [ -n "$verdict" ] || exit 0
  escape_or_refuse new-file RESERVE_OK unreserved "$NF_HERE" && exit 0
  kind=${verdict%%$'\t'*}; key=${verdict#*$'\t'}
  guard_log new-file blocked "$(guard_cmd)" unreserved
  printf 'BLOCKED: a new %s file takes a RESERVED prefix, so parallel queues never collide:\n    make reserve KIND=%s KEY="%s"   (in .claude/skills/diagram) - it writes the stub; then fill that file\n' "$kind" "$kind" "$key" >&2
  exit 2
}

case "$MODE" in
  pretool) pretool ;;
  *) echo "new-file-hooks: unknown mode '$MODE' (want: pretool)" >&2; exit 1 ;;
esac
