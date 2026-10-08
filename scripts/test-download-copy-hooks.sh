#!/usr/bin/env bash
# Tests for download-copy-hooks.sh (feature 313, SC-004).
# Run: scripts/test-download-copy-hooks.sh   (exit 0 = all green)
#
# TWO DIRECTIONS: every way of writing the GM's copy is refused, and reading it, grepping it, the make targets and the
# canonical list in the repository all pass.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
HOOK_ERR=$(mktemp)
trap 'rm -rf "$GUARD_LOG_ROOT" "$HOOK_ERR"' EXIT
HOOK="$HERE/download-copy-hooks.sh"
PASS=0; FAIL=0
COPY=/host-l7r-repo/academic-sources/TO-DOWNLOAD.md

tool_ev() { python3 -c 'import json,sys; print(json.dumps({"tool_name":sys.argv[1],"tool_input":{"file_path":sys.argv[2]}}))' "$1" "$2"; }
bash_ev() { python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$1"; }

check() { # label expected payload
  local rc; printf '%s' "$3" | "$HOOK" pretool >/dev/null 2>"$HOOK_ERR"; rc=$?
  if { [ "$2" = ok ] && [ "$rc" -eq 0 ]; } || { [ "$2" = blocked ] && [ "$rc" -ne 0 ]; }; then
    echo "  ok      $1"; PASS=$((PASS+1))
  else echo "  FAIL    $1 (expected $2, rc=$rc)"; FAIL=$((FAIL+1)); fi
}

echo "1. IT FIRES on any attempt to WRITE the GM's copy"
check "Edit tool"                  blocked "$(tool_ev Edit $COPY)"
check "Write tool"                 blocked "$(tool_ev Write $COPY)"
check "append redirect"            blocked "$(bash_ev "cat draft.md >> $COPY")"
check "redirect, quoted"           blocked "$(bash_ev "printf x > '$COPY'")"
check "tee -a"                     blocked "$(bash_ev "echo x | tee -a $COPY")"
check "sed -i"                     blocked "$(bash_ev "sed -i s/a/b/ $COPY")"
check "cp onto it"                 blocked "$(bash_ev "cp list.md $COPY")"
check "mv onto it"                 blocked "$(bash_ev "mv -f list.md $COPY")"
check "python write_text"          blocked "$(bash_ev "python3 -c \"import pathlib; pathlib.Path('$COPY').write_text('x')\"")"
check "python open for append"     blocked "$(bash_ev "python3 -c \"open('$COPY', 'a').write('x')\"")"

echo
echo "2. IT STAYS QUIET - reading the copy, the make targets, the canonical list"
check "cat"                        ok "$(bash_ev "cat $COPY")"
check "grep"                       ok "$(bash_ev "grep -n 'Mark:' $COPY")"
check "diff"                       ok "$(bash_ev "diff $COPY research/to-download.md")"
check "copying it out"             ok "$(bash_ev "cp $COPY /tmp/x.md")"
check "make downloads-sync"        ok "$(bash_ev 'make downloads-sync')"
check "make download-add"          ok "$(bash_ev 'make download-add FILE=draft.md')"
check "editing the canonical list" ok "$(tool_ev Edit /repo/research/to-download.md)"
check "a commit message naming it" ok "$(bash_ev "git -C . commit -qm 'the GM copy TO-DOWNLOAD.md left alone'")"

echo
echo "3. THE REFUSAL NAMES THE COMMANDS"
printf '%s' "$(tool_ev Write $COPY)" | "$HOOK" pretool >/dev/null 2>"$HOOK_ERR" || true
if grep -q "make download-add FILE=<draft.md>" "$HOOK_ERR" && grep -q "make downloads-sync" "$HOOK_ERR"; then
  echo "  ok      names make download-add and make downloads-sync"; PASS=$((PASS+1))
else echo "  FAIL    the refusal does not name the commands"; FAIL=$((FAIL+1)); fi

echo
echo "4. THE ESCAPE: DOWNLOAD_COPY_OK with a reason permits, a bare token does not"
check "with a reason"              ok "$(bash_ev "sed -i s/a/b/ $COPY  # DOWNLOAD_COPY_OK: the GM asked for this repair on 2026-10-03")"
check "bare"                       blocked "$(bash_ev "sed -i s/a/b/ $COPY  # DOWNLOAD_COPY_OK")"

echo
echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
