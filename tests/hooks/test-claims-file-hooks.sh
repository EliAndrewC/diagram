#!/usr/bin/env bash
# Tests for claims-file-hooks.sh (feature 376 FR-002): every hand route to the research claims sheet is refused with
# the FR-001 commands; the commands themselves pass. Every case drives the REAL hook with a REAL payload.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../../scripts/hooks/claims-file-hooks.sh"
PASS=0; FAIL=0
LOGROOT=$(mktemp -d); export GUARD_LOG_DIR="$LOGROOT"
trap 'rm -rf "$LOGROOT"' EXIT
SHEET=/diagram/.clones/RESEARCH-CLAIMS.md

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
bash_cmd() { OUT=$(python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$1" | "$HOOK" pretool 2>&1); RC=$?; }
file_tool() { OUT=$(python3 -c 'import json,sys; print(json.dumps({"tool_name":sys.argv[1],"tool_input":{"file_path":sys.argv[2]}}))' "$1" "$2" | "$HOOK" pretool 2>&1); RC=$?; }

echo "1. every hand route to the sheet is refused, naming the tool"
for c in "cat $SHEET" "tail -5 $SHEET" "echo 'x | 376 | Q=0060' >> $SHEET" "sed -i 's/a/b/' $SHEET" \
         "make lines FILE=$SHEET KEY=homesteads" "make append FILE=$SHEET LINE='x | 376 | Q=0060'"; do
  bash_cmd "$c"
  [ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q 'make research-claims Q=' && ok "refused: ${c:0:40}" || no "passed: $c" "(rc=$RC)"
done
for t in Read Edit Write; do
  file_tool "$t" "$SHEET"
  [ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "make research-claim Q=" && ok "refused: the $t tool on the sheet" || no "the $t tool passed" "(rc=$RC)"
done

echo "2. the tool's own commands, and everything else, pass"
for c in 'make research-claims Q="0060 0246"' 'make research-claim Q="0060" FEATURE=376' 'make research-claim Q=0060 FEATURE=376 STATUS=done' "cat /diagram/.clones/other.md" "make lines FILE=handoff.md KEY=0060"; do
  bash_cmd "$c"
  [ "$RC" -eq 0 ] && ok "passes: ${c:0:44}" || no "refused: $c" "(rc=$RC)"
done
file_tool Read /diagram/.clones/diagram-research/CLAUDE.md
[ "$RC" -eq 0 ] && ok "a Read of another file passes" || no "an unrelated Read was refused" "(rc=$RC)"

echo "3. the escape, for a repair of the sheet itself, is recorded"
bash_cmd "CLAIMS_FILE_OK='repair a line written before the tool existed' sed -i 's/a/b/' $SHEET"
[ "$RC" -eq 0 ] && ok "CLAIMS_FILE_OK with a reason passes" || no "the escape did not pass" "(rc=$RC)"
bash_cmd "cat $SHEET"
grep -q '"guard": "claims-file"' "$LOGROOT"/*.json 2>/dev/null && ok "a refusal writes a guard-log entry" || no "no guard-log entry"

echo "4. it fires only through its own check"
SANS=$(mktemp); sed 's#^\[ -n "\$HIT" \] || exit 0#exit 0#' "$HOOK" > "$SANS"; chmod +x "$SANS"
OUT=$(python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "cat $SHEET" | "$SANS" pretool 2>&1); RC=$?
[ "$RC" -eq 0 ] && ok "with its check removed the same command passes - the test sees the guard" || no "the stripped hook still blocked" "(rc=$RC)"
rm -f "$SANS"

echo
echo "claims-file: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
