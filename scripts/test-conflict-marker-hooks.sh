#!/usr/bin/env bash
# Tests for conflict-marker-hooks.sh and its shared detector (feature 241).
# Run: scripts/test-conflict-marker-hooks.sh   (exit 0 = all green)
#
# Every case drives the REAL hook with a REAL payload over a REAL git tree, because a grep proves a call
# site exists and not that it fires - the rule tests/tooling/test_guard_firing_log.py enforces.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/conflict-marker-hooks.sh"
DETECT="$HERE/_hm_conflict.py"
PASS=0; FAIL=0
LOGROOT=$(mktemp -d); export GUARD_LOG_DIR="$LOGROOT"
trap 'rm -rf "$LOGROOT" "$FIX"' EXIT

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

# the three markers, BUILT - so this suite does not carry a triple of its own
O=$(printf '<%.0s' {1..7}); M=$(printf '=%.0s' {1..7}); X=$(printf '>%.0s' {1..7})

FIX=$(mktemp -d)
git -C "$FIX" init -q 2>/dev/null
git -C "$FIX" config user.email t@t >/dev/null 2>&1
git -C "$FIX" config user.name t >/dev/null 2>&1
printf 'base\n' > "$FIX/tracked.md"
printf 'clean\n' > "$FIX/clean.md"
git -C "$FIX" add -A >/dev/null 2>&1
git -C "$FIX" commit -qm base >/dev/null 2>&1

run() {  # run <command> -> stderr+stdout, rc in RC
  OUT=$(python3 -c 'import json,sys; print(json.dumps({"session_id":"t","tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$1" \
        | ( cd "$FIX" && "$HOOK" pretool 2>&1 )); RC=$?
}

echo "1. it fires on what would be staged, and names the files"
printf 'base\n%s HEAD\nmine\n%s\ntheirs\n%s other\n' "$O" "$M" "$X" > "$FIX/tracked.md"
printf '%s HEAD\na\n%s\nb\n%s other\n' "$O" "$M" "$X" > "$FIX/untracked.md"
printf 'changed\n' >> "$FIX/clean.md"
run "git add -A"
[ "$RC" -eq 2 ] && ok "git add -A with two conflicted files is blocked" || no "add -A not blocked" "(rc=$RC)"
printf '%s' "$OUT" | grep -q "tracked.md" && printf '%s' "$OUT" | grep -q "untracked.md" && ok "...naming the tracked one AND the untracked one" || no "the files are not named"
run "git commit -am wip"
[ "$RC" -eq 2 ] && ok "git commit -am is blocked too" || no "commit -am not blocked" "(rc=$RC)"
run "git add clean.md"
[ "$RC" -eq 0 ] && ok "...but naming only a CLEAN path passes - it judges what would be staged" || no "a clean path was blocked" "(rc=$RC)"

echo "2. THE CASE A STATE-BASED RULE WOULD GET WRONG: the resolved merge's own add -A"
printf 'resolved\n' > "$FIX/tracked.md"
printf 'resolved\n' > "$FIX/untracked.md"
: > "$FIX/.git/MERGE_HEAD"   # a merge IS in progress, and everything is resolved
run "git add -A"
[ "$RC" -eq 0 ] && ok "a resolved merge stages cleanly, MERGE_HEAD and all" || no "the correct end of a merge was refused" "(rc=$RC)"
rm -f "$FIX/.git/MERGE_HEAD"

echo "3. prose about a marker is not a marker - by COLUMN 0, not by a fence"
printf 'A doc about merges. Inline: `%s` then `%s` then `%s`.\n' "$O" "$M" "$X" > "$FIX/about.md"
printf 'Indented, as prose shows it:\n\n    %s HEAD\n    %s\n    %s other\n' "$O" "$M" "$X" >> "$FIX/about.md"
run "git add -A"
[ "$RC" -eq 0 ] && ok "inline and indented examples pass - neither starts a line with a marker" || no "prose was treated as a conflict" "(rc=$RC)"
printf 'A heading\n%s\n\ntext\n' "$M" > "$FIX/heading.md"
run "git add -A"
[ "$RC" -eq 0 ] && ok "a seven-character Markdown underline is not a conflict" || no "an underline fired the guard" "(rc=$RC)"
# AND THE CASE A FENCE EXEMPTION WOULD HIDE: git writes its markers at column 0 wherever the conflict
# falls, including inside a fenced block in a Markdown file - 7 of the 23 files of the 2026-09-13 incident
# were Markdown or HTML. So a fenced triple IS flagged, and a file that must show one says so.
printf 'Docs.\n\n```\n%s HEAD\nmine\n%s\ntheirs\n%s other\n```\n' "$O" "$M" "$X" > "$FIX/fenced.md"
run "git add -A"
[ "$RC" -eq 2 ] && ok "a triple at column 0 INSIDE a fence is still flagged (no fence exemption)" || no "a fenced triple passed - the exemption is back" "(rc=$RC)"
printf 'CONFLICT_MARKERS_OK: this doc must SHOW a conflict to explain one\n\n```\n%s HEAD\nmine\n%s\ntheirs\n%s other\n```\n' "$O" "$M" "$X" > "$FIX/fenced.md"
run "git add -A"
[ "$RC" -eq 0 ] && ok "...and the file-level exemption with a reason lets that doc through" || no "the file-level exemption did not work" "(rc=$RC)"
printf 'CONFLICT_MARKERS_OK: x\n\n%s HEAD\nmine\n%s\ntheirs\n%s other\n' "$O" "$M" "$X" > "$FIX/fenced.md"
run "git add -A"
[ "$RC" -eq 2 ] && ok "...but a one-word reason is not a reason" || no "a bare file-level exemption was honored" "(rc=$RC)"
rm -f "$FIX/fenced.md"

echo "3b. THE COMMAND SHAPES, asked of git rather than enumerated"
printf 'base\n%s HEAD\na\n%s\nb\n%s o\n' "$O" "$M" "$X" > "$FIX/tracked.md"
mkdir -p "$FIX/sub"; printf 'clean\n' > "$FIX/sub/ok.md"
OUT=$(python3 -c 'import json,sys; print(json.dumps({"session_id":"t","tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "CL=$FIX; git -C \$CL add -A" | ( cd /tmp && "$HOOK" pretool 2>&1 )); RC=$?
[ "$RC" -eq 2 ] && ok "THE INCIDENT'S OWN SHAPE: CL=...; git -C \$CL add -A is blocked" || no "the incident's command shape walked through" "(rc=$RC)"
OUT=$(python3 -c 'import json,sys; print(json.dumps({"session_id":"t","tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "cd $FIX && git add -A" | ( cd /tmp && "$HOOK" pretool 2>&1 )); RC=$?
[ "$RC" -eq 2 ] && ok "a cd into the tree is followed too" || no "cd was not followed" "(rc=$RC)"
OUT=$(python3 -c 'import json,sys; print(json.dumps({"session_id":"t","tool_name":"Bash","tool_input":{"command":"git add ."}}))' | ( cd "$FIX/sub" && "$HOOK" pretool 2>&1 )); RC=$?
[ "$RC" -eq 0 ] && ok "CORRECT WORK: git add . in a clean subdirectory passes while a marker sits elsewhere" || no "git add . fired on correct work - the failure the whole design avoids" "(rc=$RC)"
run "git add sub/"
[ "$RC" -eq 0 ] && ok "a clean DIRECTORY pathspec passes" || no "a clean directory was blocked" "(rc=$RC)"
run "git add ."
[ "$RC" -eq 2 ] && ok "...and a directory pathspec that CONTAINS the conflict is blocked, not skipped" || no "a directory pathspec skipped the conflict" "(rc=$RC)"
run "git add -u"
[ "$RC" -eq 2 ] && ok "git add -u is judged" || no "add -u walked through" "(rc=$RC)"
run 'git commit -m "a message mentioning tracked.md is not a pathspec"'
[ "$RC" -eq 0 ] && ok "a -m message naming a file is not a pathspec" || no "a commit message was read as a path" "(rc=$RC)"

echo "4. the escape"
printf 'base\n%s HEAD\nmine\n%s\ntheirs\n%s other\n' "$O" "$M" "$X" > "$FIX/tracked.md"
run 'git add -A CONFLICT_MARKERS_OK="a fixture carries the markers on purpose"'
[ "$RC" -eq 0 ] && ok "the escape with a reason permits" || no "the escape did not permit" "(rc=$RC)"
grep -rlq "conflict-markers-ok" "$LOGROOT" && ok "...and is recorded with its own rule" || no "the escape was not recorded"
run 'git add -A CONFLICT_MARKERS_OK'
[ "$RC" -ne 0 ] && ok "a BARE escape is refused - the reason is the point" || no "a bare escape permitted" "(rc=$RC)"
run 'grep -rn CONFLICT_MARKERS_OK scripts/'
[ "$RC" -eq 0 ] && ok "a MENTION in a grep is not an invocation (it stages nothing, so nothing to block)" || no "a grep was blocked" "(rc=$RC)"

echo "5. it keeps out of everything else"
run "ls -la"
[ "$RC" -eq 0 ] && ok "a non-git command is ignored" || no "a non-git command was judged" "(rc=$RC)"
run "git status --porcelain"
[ "$RC" -eq 0 ] && ok "a read-only git command is ignored" || no "git status was judged" "(rc=$RC)"
run "git log --oneline -1"
[ "$RC" -eq 0 ] && ok "git log is ignored" || no "git log was judged" "(rc=$RC)"

echo "6. the BACKSTOP over tracked files"
git -C "$FIX" add -A >/dev/null 2>&1   # stage it the way the incident did
git -C "$FIX" commit -qm "the incident: a conflict committed" >/dev/null 2>&1
python3 "$DETECT" --tracked "$FIX" >/dev/null 2>&1
[ "$?" -eq 1 ] && ok "a COMMITTED conflict fails the backstop" || no "the backstop missed a committed conflict"
# captured rather than piped: the detector exits 1 BY DESIGN when it finds one, and `pipefail` would
# report that as the pipeline's status even when grep matched - which is what this line did at first
BOUT=$(python3 "$DETECT" --tracked "$FIX" 2>&1 || true)
printf '%s' "$BOUT" | grep -q "tracked.md" && ok "...naming the file" || no "the backstop does not name the file"
printf 'resolved\n' > "$FIX/tracked.md"; git -C "$FIX" add -A >/dev/null 2>&1
git -C "$FIX" commit -qm resolved >/dev/null 2>&1
python3 "$DETECT" --tracked "$FIX" >/dev/null 2>&1 && ok "and a clean tree passes it" || no "the backstop fired on a clean tree"
python3 "$DETECT" --tracked "$HERE/.." >/dev/null 2>&1 && ok "...including this repository, whose own spec and suite discuss markers" || no "the backstop fires on this repository"

echo
echo "conflict-marker-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
