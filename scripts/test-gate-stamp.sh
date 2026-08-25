#!/usr/bin/env bash
# Tests for gate-stamp.py - the push-time "a green gate saw exactly this code" guard.
# Run: scripts/test-gate-stamp.sh   (exit 0 = all green). Runs under `make hooks-test`.
#
# THE CASE THAT MOTIVATED THIS FILE (2026-08-25): a session ran `make hooks-test` (RED), then
# `git commit; sync-with-main.sh done` chained with ';', and the push LANDED - the only code that
# had changed was under scripts/, which the stamp did not cover. A guard-script change must now
# carry a green `make hooks-test` stamp exactly as engine Python must carry a green `make done`.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="$HERE/gate-stamp.py"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
FAILED=0
check() { # label expected-rc actual-rc
  if [ "$2" = "$3" ]; then printf 'ok    %s (rc=%s)\n' "$1" "$3"; else printf 'FAIL  %s (expected rc=%s, got rc=%s)\n      out: %s\n' "$1" "$2" "$3" "${OUT:-}"; FAILED=1; fi
}

python3 "$STAMP" --selftest; check "selftest: the hash still bites" 0 $?

# ---- fixture: a repo with a remote main, a clone, and one commit per area -----------------------
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
MAIN=$TMP/main; git init -q -b main "$MAIN"
mkdir -p "$MAIN/scripts" "$MAIN/.claude/skills/diagram"
echo 'echo guard' > "$MAIN/scripts/x-hooks.sh"; echo 'x = 1' > "$MAIN/.claude/skills/diagram/m.py"; echo doc > "$MAIN/README.md"
git -C "$MAIN" add -A; git -C "$MAIN" commit -qm base
W=$TMP/clone; git clone -q "$MAIN" "$W"

# a docs-only change needs no stamp
echo more >> "$W/README.md"; git -C "$W" commit -qam docs
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "docs-only change: no stamp needed" 0 $?

# a tests-only change needs no stamp either (feature 132 FR-024, the GM's ruling): tests/ is outside the diagram area
mkdir -p "$W/.claude/skills/diagram/tests"; echo 'def test_x(): pass' > "$W/.claude/skills/diagram/tests/test_x.py"; git -C "$W" add -A; git -C "$W" commit -qm tests
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "tests-only change: no stamp needed (FR-024)" 0 $?
mkdir -p "$W/.claude/skills/diagram/l7r/diagram/ci"; echo 'x = 1' > "$W/.claude/skills/diagram/l7r/diagram/ci/decision.py"; git -C "$W" add -A; git -C "$W" commit -qm ci
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "ci-only change: no stamp needed (FR-025)" 0 $?

# a guard-script change with NO hooks stamp is refused - THE motivating case
echo 'echo changed' > "$W/scripts/x-hooks.sh"; git -C "$W" commit -qam guard
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "scripts/ change, no hooks stamp -> refused" 1 $?
case $OUT in *"hooks: no green gate"*"make hooks-test"*) : ;; *) echo "FAIL  refusal must name the hooks area and make hooks-test: $OUT"; FAILED=1 ;; esac

# a hooks stamp written against the code being pushed admits it...
( cd "$W" && python3 "$STAMP" --write hooks )
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "scripts/ change, matching hooks stamp -> allowed" 0 $?
# ...and a stale one (the guard edited again after the green run) does not
echo 'echo edited again' > "$W/scripts/x-hooks.sh"; git -C "$W" commit -qam guard2
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "scripts/ edited after the stamp -> refused" 1 $?
case $OUT in *"DIFFERENT code"*) : ;; *) echo "FAIL  stale-stamp refusal must say the code differs: $OUT"; FAILED=1 ;; esac

# the hooks stamp does not vouch for engine Python, and vice versa
( cd "$W" && python3 "$STAMP" --write hooks )
echo 'x = 2' > "$W/.claude/skills/diagram/m.py"; git -C "$W" commit -qam engine
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "engine Python change, only a hooks stamp -> refused" 1 $?
case $OUT in *"diagram: no green gate"*) : ;; *) echo "FAIL  refusal must name the diagram area: $OUT"; FAILED=1 ;; esac
( cd "$W" && python3 "$STAMP" --write diagram )
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "both areas stamped -> allowed" 0 $?

# a .py under scripts/ is a hooks-area file too (gate-stamp.py, _hookmatch.py live there)
echo 'y = 1' > "$W/scripts/_helper.py"; git -C "$W" add -A; git -C "$W" commit -qm helper
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "new scripts/*.py, stamp predates it -> refused" 1 $?

echo -----
if [ "$FAILED" -eq 0 ]; then echo "all gate-stamp tests passed"; exit 0; else echo "SOME TESTS FAILED"; exit 1; fi
