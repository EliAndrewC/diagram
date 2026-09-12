#!/usr/bin/env bash
# Tests for shell-check-hooks.sh. Run: scripts/test-shell-check-hooks.sh   (exit 0 = all green)
#
# TWO DIRECTIONS, always: the guard must FIRE on the four things it exists to catch, and STAY QUIET on
# correct work. The quiet half here is not a list somebody imagined - it is the REPLAY of every Bash
# command the session that motivated this feature actually ran
# (`scripts/fixtures/bash-parse-corpus-2026-09.json`, 238 of them), which the case table drives
# through the hook itself. A check whose false-positive rate is unmeasured is a check nobody can
# trust; this one's is measured on every run.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$HERE/_hm_shell.py" --selftest || exit 1
exec python3 "$HERE/test_hooks_cases.py" "shell-check"
