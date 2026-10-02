#!/bin/bash
# Tests for blocked-fetch-hooks.sh - a blocked domain is refused at every fetch route outside Python, and every other
# fetch is recorded as an attempt with its earlier attempts shown (feature 312, FR-002, FR-017, FR-018).
# Run: scripts/test-blocked-fetch-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 312 FR-002 - a NEW guard's companion suite.
#
# Every case drives the REAL hook with a REAL payload against the REAL blocked list (Grokipedia). The attempts log is
# written under a scratch tree (`L7R_ATTEMPTS_ROOT`), and the clone the payload names is a scratch `.clones/<name>`.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# BF_HOOK lets the proof-of-firing run this suite against a mutated copy of the guard and watch it go red.
HOOK="${BF_HOOK:-$HERE/blocked-fetch-hooks.sh}"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT
export L7R_ATTEMPTS_ROOT="$T/attempts" L7R_SOURCES_HOME="$T/home"
mkdir -p "$T/.clones/c/.git" "$T/mirror/.git"
LOG="$L7R_ATTEMPTS_ROOT/.claude/skills/diagram/research/source-attempts.jsonl"
PASS=0; FAIL=0
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
call() { # call <tool> <json tool_input> [cwd] -> rc in $T/rc, stdout in $T/out
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t-bf","tool_name":sys.argv[1],"cwd":sys.argv[3],"tool_input":json.loads(sys.argv[2])}))' "$1" "$2" "${3:-$T/.clones/c}" \
    | "$HOOK" pretool >"$T/out" 2>"$T/err"; echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }
lines() { [ -f "$LOG" ] && wc -l < "$LOG" | tr -d ' ' || echo 0; }

echo "1. a blocked domain is refused at every route the hook sees"
call WebFetch '{"url":"https://grokipedia.com/page/Kaifeng","prompt":"the walls"}'
[ "$(rc)" -eq 2 ] && ok "a WebFetch" || no "allowed" "(rc=$(rc))"
grep -q 'blocked-domains.json: grokipedia.com' "$T/err" && ok "...the message names the list and the entry" || no "no list in the message"
call WebFetch '{"url":"https://www.grokipedia.com/page/X","prompt":"x"}'
[ "$(rc)" -eq 2 ] && ok "a subdomain" || no "allowed" "(rc=$(rc))"
call Bash '{"command":"curl -sL https://grokipedia.com/page/X | head"}'
[ "$(rc)" -eq 2 ] && ok "curl" || no "allowed" "(rc=$(rc))"
call Bash '{"command":"wget -qO- grokipedia.com/page/X"}'
[ "$(rc)" -eq 2 ] && ok "wget with no scheme" || no "allowed" "(rc=$(rc))"
call Bash '{"command":"cd .claude/skills/diagram && make source-pages OUT=/tmp/x URL=https://grokipedia.com/page/X QUESTION=0012 SOUGHT=y"}'
[ "$(rc)" -eq 2 ] && ok "a make fetch target" || no "allowed" "(rc=$(rc))"
[ "$(lines)" -eq 0 ] && ok "...and nothing blocked was recorded" || no "a blocked fetch was recorded"

echo "2. what is not a fetch of a blocked domain passes"
call Bash '{"command":"grep -rn grokipedia.com docs/research-doctrine.md"}'
[ "$(rc)" -eq 0 ] && ok "a grep for the domain (a mention)" || no "a mention was refused"
call Bash '{"command":"curl -sL https://notgrokipedia.com/x"}'
[ "$(rc)" -eq 0 ] && ok "a domain that merely ends with the same letters" || no "refused" "(rc=$(rc))"
call Bash '{"command":"ls -la"}'
[ "$(rc)" -eq 0 ] && ok "an ordinary command" || no "refused"

echo "3. every other fetch is an attempt, and its earlier attempts come back as context"
start=$(lines)
call WebFetch '{"url":"https://example.org/a","prompt":"the dike width"}'
[ "$(rc)" -eq 0 ] && [ "$(lines)" -eq $((start + 1)) ] && ok "a WebFetch is recorded" || no "not recorded" "(rc=$(rc), lines=$(lines))"
grep -q '"sought": "the dike width"' "$LOG" && grep -q '"route": "webfetch"' "$LOG" && ok "...its prompt as what was sought" || no "wrong line"
[ -s "$T/out" ] && no "context printed for a first read" || ok "...no context for a first read"
call WebFetch '{"url":"https://example.org/a","prompt":"the pond depth"}'
grep -q 'additionalContext' "$T/out" && grep -q 'the dike width' "$T/out" && ok "a second read is told the first" || no "no context"
call Bash '{"command":"curl -sL http://example.net/p"}'
grep -q '"route": "bash"' "$LOG" && grep -q 'curl -sL http://example.net/p' "$LOG" && ok "a curl is recorded with its command" || no "curl not recorded"
before=$(lines)
call Bash '{"command":"cd .claude/skills/diagram && make source-pages OUT=/tmp/x URL=https://example.org/b QUESTION=0012 SOUGHT=y"}'
[ "$(lines)" -eq "$before" ] && ok "a make route records itself, not twice" || no "the hook recorded a make route"
call WebFetch '{"url":"https://example.org/c","prompt":"x"}' "$T/mirror"
[ "$(lines)" -eq "$before" ] && ok "nothing is written from outside a clone (the mirror)" || no "written from the mirror"

echo
echo "blocked-fetch-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
