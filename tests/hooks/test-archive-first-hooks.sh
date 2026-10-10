#!/usr/bin/env bash
# Tests for archive-first-hooks.sh and lib/hm_archive_first.py (feature 376 plan D6): the first WebFetch of a page the
# archive holds is refused with the archived text's path; the same actor's second fetch passes; a page the archive does
# not hold, another tool, and another actor each behave as they should. Real hook, real payload, a fixture archive.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../../scripts/hooks/archive-first-hooks.sh"
PASS=0; FAIL=0
LOGROOT=$(mktemp -d); export GUARD_LOG_DIR="$LOGROOT"
FIX=$(mktemp -d); export L7R_ARCHIVE_FIRST_STATE="$FIX/state" L7R_ARCHIVE_STORE="$FIX/store"
trap 'rm -rf "$LOGROOT" "$FIX"' EXIT
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

mkdir -p "$FIX/repo/.git"
URL="https://ja.wikipedia.org/wiki/民家"
python3 - "$FIX" "$URL" <<'PY'
import hashlib, json, pathlib, sys
fix, url = pathlib.Path(sys.argv[1]), sys.argv[2]
uid = hashlib.sha256(url.encode()).hexdigest()[:12]
row = fix / "repo" / "research" / "archive" / uid[:2] / f"{uid}.json"
row.parent.mkdir(parents=True)
row.write_text(json.dumps({"url": url, "path": f"{uid[:2]}/{uid}/20261002T120000Z", "captured": "2026-10-02T12:00:00+00:00"}))
cap = fix / "store" / uid[:2] / uid / "20261002T120000Z"
cap.mkdir(parents=True)
(cap / "text.txt").write_text("民家 text.\n")
PY

fetch() {  # fetch <url> <agent_id> [tool]
  OUT=$(python3 -c 'import json,sys; print(json.dumps({"session_id":"s1","agent_id":sys.argv[2],"tool_name":sys.argv[3],"tool_input":{"url":sys.argv[1],"prompt":"read"}}))' "$1" "$2" "${3:-WebFetch}" \
        | ( cd "$FIX/repo" && "$HOOK" pretool 2>&1 )); RC=$?
}

echo "1. the first fetch of a held page is refused with the archived text's path"
fetch "$URL" agent-a
[ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -q "captured 2026-10-02" && printf '%s' "$OUT" | grep -q "20261002T120000Z/text.txt" && ok "refused, naming the text and its capture date" || no "the held page was fetched" "(rc=$RC) $OUT"
printf '%s' "$OUT" | grep -q "fetch the same URL again" && ok "...and saying how to get the live page" || no "the second-fetch route is not named"
fetch "$URL" agent-a
[ "$RC" -eq 0 ] && ok "the same agent's second fetch passes - it wants the live page" || no "the second fetch was refused" "(rc=$RC)"
fetch "$URL" agent-b
[ "$RC" -eq 2 ] && ok "another agent's first fetch is refused for itself" || no "another actor rode on the first's second fetch" "(rc=$RC)"

echo "2. what the archive does not hold, and other tools, pass"
fetch "https://example.org/not-kept" agent-a
[ "$RC" -eq 0 ] && ok "a page the archive does not hold is fetched" || no "an unheld page was refused" "(rc=$RC)"
fetch "$URL" agent-c WebSearch
[ "$RC" -eq 0 ] && ok "a WebSearch is not this guard's" || no "a WebSearch was refused" "(rc=$RC)"
ls "$LOGROOT"/*.json >/dev/null 2>&1 && grep -q '"guard": "archive-first"' "$LOGROOT"/*.json && ok "a refusal writes a guard-log entry" || no "no guard-log entry"

echo "3. it fires only through its decider"
SANS=$(mktemp); sed 's#^\[ -n "\$GOT" \] || exit 0#exit 0#' "$HOOK" > "$SANS"; chmod +x "$SANS"
OUT=$(python3 -c 'import json,sys; print(json.dumps({"session_id":"s2","tool_name":"WebFetch","tool_input":{"url":sys.argv[1]}}))' "$URL" | ( cd "$FIX/repo" && "$SANS" pretool 2>&1 )); RC=$?
[ "$RC" -eq 0 ] && ok "with its check removed the same fetch passes - the test sees the guard" || no "the stripped hook still blocked" "(rc=$RC)"
rm -f "$SANS"

echo
echo "archive-first: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
