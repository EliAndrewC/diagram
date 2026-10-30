#!/bin/bash
# phase-source-hooks.sh - a stage being rebuilt is written from its derivation, never read from its old code (feature 444).
# GUARD_EDIT_OK: feature 444 - a NEW guard, the GM 2026-10-30: "we should definitely add a guard for that ... Please do indeed
# do that."
#
# THE FEAR (the GM, 2026-10-30): "I suspect that if I asked you to do the rewrite in Rust, even with this project guideline,
# then you would just end up re-implementing the same bad algorithms." The budget is derived blind to the code and the landing
# audited against it, but nothing stopped the session that WRITES a stage's Rust from reading the stage's old Python as it wrote.
#
# THE RULE. While a phase task (`phase: <stage>` in its tasks.md block) is started (`make task-start`) and unticked, a read of
# that stage's old modules - a Read, a Grep or Glob on them or their directory, a shell read verb naming them - is refused, with
# the derivation to write from. The decision is `lib/hm_phase_source.py`'s; the held files, `scripts/gates/phase_sources.py`'s.
#
# ESCAPE: PHASE_SOURCE_OK="<reason>" in a shell command; for the Read tool, `make phase-read FILE=<path> WHY="<reason>"` lets
# that file be read for ten minutes (to replace the stage's thin Python function, say). Both reasons are logged.
#
# Modes:
#   pretool (PreToolUse, Bash|Read|Grep|Glob)   refuse / pass, recorded
set -uo pipefail

MODE=${1:-}
PS_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$PS_HERE/lib/guardlog.sh"

pretool() {
  local verdict file phase feature task deriv
  INPUT="$(cat)"
  # NO HOLD, NO PYTHON: almost every call happens with no phase task started (2026-10-30)
  compgen -G "${PHASE_SOURCE_GLOB:-/diagram/.git/phase-sources.json /diagram/.clones/*/.git/phase-sources.json}" > /dev/null || exit 0
  verdict="$(printf '%s' "$INPUT" | python3 "$PS_HERE/lib/hm_phase_source.py" 2>/dev/null)" || exit 0
  case "$verdict" in held\ *) ;; *) exit 0 ;; esac
  read -r _ file phase feature task <<< "$verdict"
  escape_or_refuse phase-source PHASE_SOURCE_OK "$phase" "$PS_HERE" && exit 0
  guard_log phase-source blocked "$(guard_cmd)" "$phase"
  deriv="specs/$feature/phases/${phase}_greenfield.derivation.md"
  {
    printf 'BLOCKED: %s is the old code of `%s`, and %s %s rebuilds that stage from its derivation, not from today'"'"'s code.\n\n' "$file" "$phase" "$feature" "$task"
    printf 'Write it from:  %s  (its Contract and Minimal algorithm)\n\n' "$deriv"
    printf 'The GM, 2026-10-30: "we are not trying to re-implement the same algorithms, because the old algorithms were\n'
    printf 'computationally inefficient." To replace the stage'"'"'s thin Python function or delete the old module, open that one\n'
    printf 'file for ten minutes:  make phase-read FILE=%s WHY="<why>"   (a shell read: PHASE_SOURCE_OK="<why>")\n' "$file"
  } >&2
  exit 2
}

case "$MODE" in
  pretool) pretool ;;
  *) echo "phase-source-hooks: unknown mode '$MODE' (want: pretool)" >&2; exit 1 ;;
esac
