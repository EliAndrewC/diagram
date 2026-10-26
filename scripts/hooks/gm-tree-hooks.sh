#!/usr/bin/env bash
# gm-tree-hooks.sh - no write lands in gm-assistant's MAIN working tree from a diagram session (feature 429 FR-003).
# (GUARD_EDIT_OK: a NEW guard, feature 429 - the GM 2026-10-26: "our tooling must enforce the correct behavior every time")
#
# THE DEFECT (2026-10-20, diagram#10): a money session left setting-note edits uncommitted in
# /host-l7r-repo/gm-assistant - gm-assistant's own main tree - one of them inside a GM NOTES block. A dirty main tree
# refuses every gm-assistant push, so gm-assistant had to stop and clean up after us. The rule ("edit from a
# gm-assistant clone, or hand the wording over on an issue") lived only in a session memory until 2026-10-26.
#
# WHAT IS JUDGED: the Edit/Write/NotebookEdit file path, and a Bash command's WRITE targets as the main-tree guard's
# interpreter finds them (`lib/hm_tree.py`: redirections, tee, sed -i, the destination of cp/mv, ...), never a mention.
# A gm-assistant clone (`/host-l7r-repo/gm-assistant/.clones/<name>/`) and the rest of /host-l7r-repo are not this
# guard's business; git writes there are `repo-safety-hooks.sh`'s. The decider is `lib/hm_gm_tree.py`.
# Escape (Bash only, for the GM's explicit say-so): GM_TREE_OK: <reason> as a trailing comment. An Edit has no escape:
# the compliant route is a clone. Test: tests/hooks/test-gm-tree-hooks.sh.
set -uo pipefail
[ "${1:-}" = "pretool" ] || exit 0
INPUT=$(cat 2>/dev/null || true)
GT_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "$INPUT" in *gm-assistant*) ;; *) exit 0 ;; esac
. "$GT_HERE/lib/guardlog.sh"

HIT=$(printf '%s' "$INPUT" | python3 "$GT_HERE/lib/hm_gm_tree.py" judge 2>/dev/null) && exit 0
[ -n "$HIT" ] || exit 0
case "$INPUT" in
  *'"tool_name": "Bash"'*|*'"tool_name":"Bash"'*)
    if escape_or_refuse gm-tree GM_TREE_OK gm-tree-ok "$GT_HERE"; then exit 0; fi ;;
esac
printf 'BLOCKED: a write into gm-assistant'"'"'s main working tree (%s).\n' "$HIT" >&2
printf 'A dirty main tree refuses every gm-assistant push. Make the edit in a gm-assistant clone\n' >&2
printf '(git clone /host-l7r-repo/gm-assistant /host-l7r-repo/gm-assistant/.clones/<name>, commit, its scripts/sync-with-main.sh done),\n' >&2
printf 'or hand the wording to gm-assistant on an issue: python3 ~/.claude/hooks/issue_watch.py open EliAndrewC/gm-assistant "<title>" < body.md\n' >&2
guard_log gm-tree blocked "$(guard_cmd)" write-in-gm-tree
exit 2
