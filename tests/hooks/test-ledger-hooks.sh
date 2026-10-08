#!/usr/bin/env bash
# Tests for ledger-hooks.sh (feature 294). Run: tests/hooks/test-ledger-hooks.sh   (exit 0 = all green)
# (GUARD_EDIT_OK: the companion of a NEW guard, feature 294.) Every case drives the REAL hook with a REAL payload over a
# REAL git tree.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../../scripts/hooks/ledger-hooks.sh"
PASS=0; FAIL=0
LOGROOT=$(mktemp -d); export GUARD_LOG_DIR="$LOGROOT"
FIX=$(mktemp -d)
trap 'rm -rf "$LOGROOT" "$FIX"' EXIT
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

git -C "$FIX" init -q 2>/dev/null
git -C "$FIX" config user.email t@t >/dev/null 2>&1
git -C "$FIX" config user.name t >/dev/null 2>&1
mkdir -p "$FIX/dev" "$FIX/scripts"
cp "$HERE/../../scripts/reviews/ledger_lint.py" "$FIX/scripts/"
HEAD_TXT='# Ledger

## Review checks, measured (feature 294 on)

| date | check | subject | verdict | finding | class | author missed? | acted on | wall | tokens |
|---|---|---|---|---|---|---|---|---|---|
'
printf '%s' "$HEAD_TXT" > "$FIX/dev/review-ledger.md"
printf 'x\n' > "$FIX/other.md"
git -C "$FIX" add -A >/dev/null 2>&1
git -C "$FIX" commit -qm base >/dev/null 2>&1

run() {  # run <command> -> output, rc in RC
  OUT=$(python3 -c 'import json,sys; print(json.dumps({"session_id":"t","tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$1" \
        | ( cd "$FIX" && "$HOOK" pretool 2>&1 )); RC=$?
}

GOOD='| 2026-10-02 | glyph-check | privy | PASS | reads | nothing | - | - | 412 s | 3100k in (2900k cached) / 4.2k out |'
SHORT='| 2026-10-02 | glyph-check | privy | PASS | reads | nothing | - | - | ~7 min | lots |'

echo "1. it fires on a staged ledger with a short row, and names the line"
printf '%s%s\n' "$HEAD_TXT" "$SHORT" > "$FIX/dev/review-ledger.md"; git -C "$FIX" add dev/review-ledger.md
run "git commit -m rows"
[ "$RC" -eq 2 ] && ok "a short row blocks the commit" || no "not blocked" "(rc=$RC)"
printf '%s' "$OUT" | grep -q "line 7" && ok "...naming the row by line" || no "no line named" "$OUT"
printf '%s' "$OUT" | grep -q "make review-cost" && ok "...and the command that fills the cost" || no "no command named"
run "git -C $FIX commit -m rows"
[ "$RC" -eq 2 ] && ok "a commit through git -C is read the same" || no "git -C missed" "(rc=$RC)"
git -C "$FIX" reset -q
run "git commit -am rows"
[ "$RC" -eq 2 ] && ok "commit -am counts the modified ledger as staged" || no "-am missed" "(rc=$RC)"
grep -rq "ledger-row-short" "$LOGROOT" && ok "...recorded under its rule" || no "not recorded"

echo "2. it stays quiet on correct work"
printf '%s%s\n' "$HEAD_TXT" "$GOOD" > "$FIX/dev/review-ledger.md"; git -C "$FIX" add dev/review-ledger.md
run "git commit -m rows"
[ "$RC" -eq 0 ] && ok "a full row commits" || no "a full row was blocked" "(rc=$RC) $OUT"
git -C "$FIX" reset -q; printf '%s%s\n' "$HEAD_TXT" "$SHORT" > "$FIX/dev/review-ledger.md"; printf 'y\n' >> "$FIX/other.md"; git -C "$FIX" add other.md
run "git commit -m other"
[ "$RC" -eq 0 ] && ok "a commit that does not stage the ledger passes" || no "an unstaged ledger blocked" "(rc=$RC)"
run "git status"
[ "$RC" -eq 0 ] && ok "not a commit: passes" || no "git status blocked"
git -C "$FIX" add dev/review-ledger.md   # the short row STAGED: only an invocation may be refused now
run "grep -n 'git commit' dev/review-ledger.md"
[ "$RC" -eq 0 ] && ok "a mention of a commit is not one" || no "a mention blocked"
run "echo 'then git commit -m x'"
[ "$RC" -eq 0 ] && ok "a quoted commit is not one either" || no "a quoted mention blocked"

echo "3. the escape"
git -C "$FIX" add dev/review-ledger.md
run 'LEDGER_LINT_OK="the row predates its transcript" git commit -m rows'
[ "$RC" -eq 0 ] && ok "the escape with a reason commits" || no "escape refused" "(rc=$RC)"
grep -rq "ledger-lint-ok" "$LOGROOT" && ok "...and is recorded" || no "escape not recorded"

echo
echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
