#!/bin/bash
# Tests for new-file-hooks.sh - a new glossary file or registry entry takes a reserved prefix (feature 265 FR-010).
# Run: scripts/test-new-file-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 265 FR-010 - a NEW guard's companion suite.
#
# Every case drives the REAL hook with a REAL payload against a fixture mirror with a clone under .clones/.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# NEW_FILE_HOOK lets the proof-of-firing run this suite against a mutated copy of the guard.
HOOK="${NEW_FILE_HOOK:-$HERE/new-file-hooks.sh}"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

M="$T/mirror"; C="$M/.clones/q"
G="$C/.claude/skills/diagram/l7r/diagram/interactive/assets/glossary"; R="$C/.claude/skills/diagram/research/sources/010-works-cited"
mkdir -p "$G" "$R" "$M/.specify"; git -C "$C" init -q 2>/dev/null
echo '{}' > "$G/0100-old.json"; : > "$R/0100-old-key.html"
python3 "$HERE/reserve-prefix.py" registry reserved-key --root "$C" --mirror "$M" >/dev/null
call() { # call <tool> <json tool_input> -> rc in $T/rc
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t-new-file","cwd":sys.argv[3],"tool_name":sys.argv[1],"tool_input":json.loads(sys.argv[2])}))' "$1" "$2" "$C" \
    | "$HOOK" pretool 2>"$T/err"; echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }

echo "1. a new prefixed file with no reservation is refused, with the command"
call Write "{\"file_path\":\"$G/0200-hitoyado.json\",\"content\":\"{}\"}"
[ "$(rc)" -eq 2 ] && ok "a Write creating an unreserved glossary file" || no "allowed" "(rc=$(rc))"
grep -q 'make reserve KIND=glossary KEY="hitoyado"' "$T/err" && ok "...the message names make reserve for it" || no "no command" "$(cat "$T/err")"
call Write "{\"file_path\":\"$R/0200-suzhou-enwiki.html\",\"content\":\"x\"}"
[ "$(rc)" -eq 2 ] && grep -q 'KIND=registry KEY="suzhou-enwiki"' "$T/err" && ok "a Write creating an unreserved registry entry" || no "allowed" "(rc=$(rc))"
call Bash '{"command":"G=.claude/skills/diagram/l7r/diagram/interactive/assets/glossary && cat > \"$G/0300-wakato.json\" <<EOF\n{}\nEOF"}'
[ "$(rc)" -eq 2 ] && ok "a heredoc redirect into a new glossary file through a shell variable" || no "allowed" "(rc=$(rc))"

echo "2. what passes"
call Write "{\"file_path\":\"$G/0100-old.json\",\"content\":\"{}\"}"
[ "$(rc)" -eq 0 ] && ok "rewriting a file that already exists" || no "refused" "(rc=$(rc))"
f=$(ls "$R" | grep reserved-key)
call Write "{\"file_path\":\"$R/$f\",\"content\":\"x\"}"
[ "$(rc)" -eq 0 ] && ok "writing the stub make reserve created" || no "refused" "(rc=$(rc))"
rm -f "$R/$f"
call Write "{\"file_path\":\"$R/$f\",\"content\":\"x\"}"
[ "$(rc)" -eq 0 ] && ok "a reserved prefix whose stub was removed (the ledger holds it)" || no "refused" "(rc=$(rc))"
# GUARD_EDIT_OK: feature 265 FR-010 - the plan review's collision: another key on a reserved prefix is refused
pfx=${f%%-*}
call Write "{\"file_path\":\"$R/$pfx-a-different-key.html\",\"content\":\"x\"}"
[ "$(rc)" -eq 2 ] && ok "a DIFFERENT key on a reserved prefix is refused (a number taken by hand that collides)" || no "the colliding key was allowed" "(rc=$(rc))"
call Write "{\"file_path\":\"$C/.claude/skills/diagram/research/fields/0300-q.html\",\"content\":\"x\"}"
[ "$(rc)" -eq 0 ] && ok "a file outside the two directories" || no "refused" "(rc=$(rc))"
# GUARD_EDIT_OK: feature 265 FR-010 - plan review round 2: a known path outside the two directories is not guessed
call Bash '{"command":"echo {} > .claude/skills/diagram/research/fields/0600-probe.json; echo x > /tmp/0600-foo.html"}'
[ "$(rc)" -eq 0 ] && ok "a redirect to a known prefixed path outside the two directories" || no "refused" "(rc=$(rc))"
call Bash '{"command":"echo done > /tmp/out.txt; ls 0400-x.json"}'
[ "$(rc)" -eq 0 ] && ok "a command that only mentions a prefixed name" || no "refused" "(rc=$(rc))"

echo "3. the escape, and the record"
call Bash '{"command":"cat > \"$G/0500-x.json\" <<EOF\n{}\nEOF\n# RESERVE_OK: restoring a file deleted in a merge"}'
[ "$(rc)" -eq 0 ] && ok "RESERVE_OK with a reason passes" || no "the escape was refused" "(rc=$(rc))"
grep -rlq 'unreserved' "$GUARD_LOG_ROOT" 2>/dev/null && ok "refusals are recorded" || no "no unreserved entry recorded"

echo "-----"
if [ "$FAIL" -eq 0 ]; then echo "all new-file-hook tests passed ($PASS)"; exit 0; fi
echo "SOME TESTS FAILED ($FAIL of $((PASS+FAIL)))"; exit 1
