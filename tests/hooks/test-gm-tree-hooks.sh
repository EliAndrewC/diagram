#!/usr/bin/env bash
# test-gm-tree-hooks.sh - prove gm-tree-hooks.sh refuses a write into gm-assistant's main working tree (the
# 2026-10-20 diagram#10 shape) and leaves its clones, the rest of /host-l7r-repo and every read alone (feature 429).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../../scripts/hooks/gm-tree-hooks.sh"
PASS=0; FAIL=0
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
export GUARD_LOG_DIR="$T/guard-log"
G=/host-l7r-repo/gm-assistant

js() { python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"; }
bash_call() { # bash_call <cwd> <command>
  OUT=$(printf '{"session_id":"t","cwd":"%s","tool_name":"Bash","tool_input":{"command":%s}}' "$1" "$(js "$2")" | "$HOOK" pretool 2>&1); RC=$?
}
file_call() { # file_call <tool> <path>
  OUT=$(printf '{"session_id":"t","cwd":"/tmp","tool_name":"%s","tool_input":{"file_path":%s,"old_string":"a","new_string":"b"}}' "$1" "$(js "$2")" | "$HOOK" pretool 2>&1); RC=$?
}
check() { if [ "$2" = "$3" ]; then printf 'ok    %s (rc=%s)\n' "$1" "$3"; PASS=$((PASS+1));
          else printf 'FAIL  %s (expected rc=%s, got rc=%s)\n      out: %s\n' "$1" "$2" "$3" "$OUT"; FAIL=$((FAIL+1)); fi; }
says() { case "$OUT" in *"$2"*) printf 'ok    %s\n' "$1"; PASS=$((PASS+1));; *) printf 'FAIL  %s - text lacks: %s\n      out: %s\n' "$1" "$2" "$OUT"; FAIL=$((FAIL+1));; esac; }

# The diagram#10 shape: an Edit of a setting note in gm-assistant's main tree.
file_call Edit "$G/setting/economics.md";              check "Edit in the main tree is refused" 2 "$RC"
says "the refusal names the clone route" "gm-assistant clone"
says "the refusal names the issue route" "issue_watch.py open"
file_call Write "$G/docs/l7r-style.md";                check "Write in the main tree is refused" 2 "$RC"
file_call NotebookEdit "$G/x.ipynb";                   check "NotebookEdit in the main tree is refused" 2 "$RC"
file_call Edit "$G/.clones/money/setting/economics.md"; check "Edit in a gm-assistant clone passes" 0 "$RC"
file_call Edit "/host-l7r-repo/academic-sources/TO-DOWNLOAD.md"; check "Edit elsewhere under /host-l7r-repo passes" 0 "$RC"
file_call Edit "/diagram/.clones/x/docs/a.md";         check "Edit in a diagram clone passes" 0 "$RC"

# Bash: the write forms, by invocation.
bash_call /tmp "sed -i 's/a/b/' $G/setting/government.md";   check "sed -i into the main tree is refused" 2 "$RC"
bash_call /tmp "echo x >> $G/setting/village-headsmen.md";   check "an append redirection into the main tree is refused" 2 "$RC"
bash_call /tmp "printf x | tee $G/notes.md";                  check "tee into the main tree is refused" 2 "$RC"
bash_call /tmp "cp /tmp/a.md $G/setting/a.md";                check "cp into the main tree is refused" 2 "$RC"
bash_call "$G" "echo x > setting/a.md";                       check "a relative write standing in the main tree is refused" 2 "$RC"
# Reads and mentions pass.
bash_call /tmp "grep -rn koku $G/setting";                    check "a grep of the tree passes" 0 "$RC"
bash_call /tmp "cat $G/setting/economics.md > /tmp/x.md";      check "a copy OUT of the tree passes" 0 "$RC"
bash_call /tmp "cp $G/setting/a.md /tmp/a.md";                check "cp FROM the tree passes" 0 "$RC"
bash_call /tmp "echo x > $G/.clones/money/a.md";              check "a write into a gm-assistant clone passes" 0 "$RC"
bash_call /tmp "git -C $G status";                            check "a git read passes" 0 "$RC"
bash_call /tmp "echo 'never edit $G/setting' > /tmp/note.md";  check "a quoted mention passes" 0 "$RC"
# The escape, Bash only.
bash_call /tmp "sed -i 's/a/b/' $G/setting/government.md  # GM_TREE_OK: the GM asked for this exact fix in the main tree"
check "GM_TREE_OK with a reason escapes a Bash write" 0 "$RC"
[ -n "$(ls "$GUARD_LOG_DIR" 2>/dev/null)" ] && { echo "ok    firings are recorded"; PASS=$((PASS+1)); } || { echo "FAIL  no guard-log entry"; FAIL=$((FAIL+1)); }

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
