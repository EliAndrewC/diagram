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
# GUARD_EDIT_OK: feature 178 FR-001 INVERTS this case, and only this half of the GM's FR-025 ruling.
# FR-025 (GM 2026-08-25) answered TWO questions at once - does a ci-only change owe a paid BUILD, and
# does it owe a local GATE - and said no to both. The paid half STANDS: `delta.is_engine` still
# excludes `ci/`, so a ci-only delta still routes DIRECT and still starts no build. The local half is
# superseded, because since 2026-09-02 the coverage floor MEASURES `l7r/diagram/ci/` (174's derived
# `source = ["l7r"]`), and feature 177 found `make done` answering "already verified" on a delta that
# rewrote four ci modules. A surface that owes 100% coverage must be able to re-open the gate that
# enforces it. GM 2026-09-03: *"I think a short-circuit for 'measured but engine' is best."*
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "ci-only change NOW needs a stamp (178 FR-001 supersedes FR-025's local half)" 1 $?
# ...and then REMOVE it, restoring the fixture exactly as the cases below found it. Under FR-001 the
# ci file is diagram-area content, so leaving it behind (as this case did while ci/ was excluded)
# hands every later case an unstamped diagram change and they fail on that instead of on what they
# test. Stamping instead of reverting is NOT equivalent: it leaves a stamp, and the "refusal must name
# the diagram area" case asserts the exact refusal, which changes from "no green gate recorded at all"
# to "ran against DIFFERENT code".
rm -f "$W/.claude/skills/diagram/l7r/diagram/ci/decision.py"; git -C "$W" add -A; git -C "$W" commit -qm un-ci

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

# THE PAGE AREA (feature 188): an asset edit owes `make page-check`, and nothing else - not the full gate.
mkdir -p "$W/.claude/skills/diagram/l7r/diagram/interactive/assets"
echo 'a.q { color: red; }' > "$W/.claude/skills/diagram/l7r/diagram/interactive/assets/page.css"; git -C "$W" add -A; git -C "$W" commit -qm css
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "asset edit, no page stamp -> refused" 1 $?
case $OUT in *"page: no green gate"*"make page-check"*) : ;; *) echo "FAIL  refusal must name the page area and make page-check: $OUT"; FAILED=1 ;; esac
case $OUT in *"diagram:"*) echo "FAIL  an asset edit must NOT demand a diagram (full gate) stamp: $OUT"; FAILED=1 ;; *) : ;; esac
# the short-circuit exit of make done writes `diagram` and not `page` - so re-stamping diagram does not admit the asset
( cd "$W" && python3 "$STAMP" --write diagram )
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "asset edit + a diagram stamp (the short-circuit's) -> still refused" 1 $?
( cd "$W" && python3 "$STAMP" --write page )
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "asset edit, matching page stamp -> allowed" 0 $?
echo 'a.q { color: blue; }' > "$W/.claude/skills/diagram/l7r/diagram/interactive/assets/page.css"; git -C "$W" commit -qam css2
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "asset edited after the page stamp -> refused" 1 $?
case $OUT in *"page: the last green gate ran against DIFFERENT code"*) : ;; *) echo "FAIL  stale page stamp must say the code differs: $OUT"; FAILED=1 ;; esac
( cd "$W" && python3 "$STAMP" --write page )

# a comment or docstring added AFTER the green run is not "different code" (GM 2026-08-26): the stamp
# hashes the docstring-stripped AST of each .py, so only a token that runs re-opens the gate
printf '"""why this is 2"""\n# see research/water.md\nx = 2  # unchanged\n' > "$W/.claude/skills/diagram/m.py"; git -C "$W" commit -qam why
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "comment/docstring edit after the stamp -> still allowed" 0 $?
echo 'x = 3' > "$W/.claude/skills/diagram/m.py"; git -C "$W" commit -qam engine3
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "code edit after the stamp -> refused" 1 $?
( cd "$W" && python3 "$STAMP" --write diagram )

# --fresh: the stamp matches the current guard scripts -> 0 (make done skips hooks-test); an edit -> 1
( cd "$W" && python3 "$STAMP" --write hooks )
( cd "$W" && python3 "$STAMP" --fresh hooks ); check "--fresh hooks right after the stamp -> 0" 0 $?
echo 'echo edited once more' > "$W/scripts/x-hooks.sh"
( cd "$W" && python3 "$STAMP" --fresh hooks ); check "--fresh hooks after a guard edit -> 1" 1 $?
echo 'x = 4' > "$W/.claude/skills/diagram/m.py"
( cd "$W" && python3 "$STAMP" --fresh diagram ); check "--fresh diagram after an engine edit -> 1" 1 $?
git -C "$W" commit -qam guard3

# a .py under scripts/ is a hooks-area file too (gate-stamp.py, _hookmatch.py live there)
echo 'y = 1' > "$W/scripts/_helper.py"; git -C "$W" add -A; git -C "$W" commit -qm helper
OUT=$(cd "$W" && python3 "$STAMP" --check origin/main 2>&1); check "new scripts/*.py, stamp predates it -> refused" 1 $?

# A GIT WORKTREE: `.git` is a FILE there, not a directory (feature 161, 2026-08-30). This is not a
# curiosity - constitution Principle XIII MANDATES a detached worktree for the regression baseline,
# so `make done` in the tree the procedure tells you to create used to crash write_stamp with
# `NotADirectoryError: .../.git/gate-green-hooks`, once per area. The gate ran and passed; only the
# recording failed, noisily but non-fatally, which is the shape that gets scrolled past.
WT="$W-worktree"
rm -rf "$WT"
git -C "$W" worktree add --detach -q "$WT" HEAD
[ -f "$WT/.git" ] || { echo "FAIL  a worktree's .git should be a FILE - the fixture no longer reproduces the trap"; FAILED=1; }
COMMON=$(git -C "$WT" rev-parse --git-common-dir)
case $COMMON in /*) : ;; *) COMMON="$WT/$COMMON" ;; esac
# DELETE any stamp an earlier case left behind, or the "it landed" assertion below passes on the
# unfixed script by finding someone else's file - a check that cannot fail is not a check.
rm -f "$COMMON/gate-green-hooks"
( cd "$WT" && python3 "$STAMP" --write hooks ); check "--write inside a worktree (.git is a FILE) -> 0, no crash" 0 $?
[ -f "$COMMON/gate-green-hooks" ]; check "the worktree's stamp lands in the shared git dir" 0 $?
( cd "$WT" && python3 "$STAMP" --fresh hooks ); check "--fresh inside a worktree reads the stamp it just wrote" 0 $?
git -C "$W" worktree remove --force "$WT"

echo -----
if [ "$FAILED" -eq 0 ]; then echo "all gate-stamp tests passed"; exit 0; else echo "SOME TESTS FAILED"; exit 1; fi
