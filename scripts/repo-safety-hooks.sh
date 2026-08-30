#!/usr/bin/env bash
# repo-safety-hooks.sh - the two git operations this project says must never happen.
#
# Both were documented and neither was enforced (audit, 2026-08-24).
#
# 1. FORCE PUSH. CLAUDE.md: "Never `git push --force` - it is the one thing that overwrites other
#    sessions' work." The GM runs several sessions at once, each in its own clone, all pushing to one
#    main. A force push does not lose YOUR work, it loses SOMEBODY ELSE'S, silently, and the person
#    who finds out is not the person who did it. There is no legitimate force push in this workflow:
#    sync-with-main.sh does a locked pull-then-push, and a conflict is resolved by merging.
#
# 2. GIT WRITES TO /host-l7r-repo. That is the GM's own `EliAndrewC/l7r` repo, bind-mounted from
#    their laptop, and CLAUDE.md is explicit: "From inside the container, never run `git commit` or
#    `git push` against the mount." The GM does their own git there. A commit made here would show up
#    on their machine as work they did not do, in a repo this project does not own.
#
#    FILE EDITS TO THAT MOUNT ARE FINE and are deliberately NOT blocked - the Note Intake Workflow's
#    whole job is appending to setting/l7r.md. It is the git verbs that are forbidden, not the
#    writing. A guard that blocked editing would break the documented workflow, which is the
#    false-positive shape this project has paid for repeatedly.
#
# NO ESCAPE HATCH on the force push: "never" is the rule and an escape is how never becomes sometimes.
# The mount guard takes HOST_GIT_OK with a reason, because a read-only operation misdetected as a
# write should not strand a session (`git log` and `git diff` there are explicitly allowed).
set -uo pipefail

MODE="${1:-pretool}"
[ "$MODE" = pretool ] || exit 0
INPUT=$(cat)

VERDICT=$(printf '%s' "$INPUT" | python3 -c '
import json, re, sys
try:
    cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
except Exception:
    cmd = ""
if not cmd:
    print("ok"); raise SystemExit
# heredoc bodies are payload, not commands - the mention-versus-invocation rule this repo has now
# learned six times over
c = re.sub(r"<<-?\s*[\x27\x22]?(\w+)[\x27\x22]?\n.*?\n\s*\1\b", " <<BODY ", cmd, flags=re.S)
# QUOTED STRINGS ARE PAYLOAD TOO. `git commit -m "never git push --force"` is a commit message ABOUT
# the rule, not a violation of it - and the first cut blocked exactly that. Seventh time this repo
# has confused a name with the thing it names, so it is stripped for the same reason heredocs are.
c = re.sub(r"\x27[^\x27]*\x27|\x22[^\x22]*\x22", " QUOTED ", c)
POS = r"(?:^|[\n;|]|&&|\|\|)\s*(?:timeout\s+\S+\s+|env\s+|[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*"

if re.search(POS + r"git\b[^\n;|&]*\bpush\b[^\n;|&]*(?:--force(?:-with-lease)?|(?<![\w-])-f(?![\w-]))", c):
    print("force-push"); raise SystemExit
if re.search(POS + r"git\b[^\n;|&]*(?:--force(?:-with-lease)?)[^\n;|&]*\bpush\b", c):
    print("force-push"); raise SystemExit
# HISTORY IS NEVER REWRITTEN (GM 2026-08-25, constitution VI - GUARD_EDIT_OK: adding the rule). No
# rebase, no squash merge, no amend: every landing is a real merge commit, because the verified-tree
# records, the review records and the perf bookends are keyed by the commits and content that were
# actually tested, and a rewrite silently throws a paid verification away.
# `git rebase` the SUBCOMMAND, and `--rebase` the FLAG - never `--no-rebase`, which is what the
# pull in the procedure says (the first cut blocked it: the eighth mention-versus-invocation slip in
# this repo). NO APOSTROPHES IN THESE COMMENTS: this Python sits inside a single-quoted bash string.
# (GUARD_EDIT_OK: the pattern refuses only the rewrite, not the flag that forbids it)
if re.search(POS + r"git\b(?:\s+-C\s+\S+|\s+-\S+)*\s+rebase\b", c) or re.search(POS + r"git\b[^\n;|&]*\bpull\b[^\n;|&]*(?<![\w-])--rebase\b", c):
    print("history-rewrite"); raise SystemExit
if re.search(POS + r"git\b[^\n;|&]*\bmerge\b[^\n;|&]*--squash", c) or re.search(POS + r"git\b[^\n;|&]*\bcommit\b[^\n;|&]*--amend", c):
    print("history-rewrite"); raise SystemExit

if "HOST_GIT_OK" not in cmd:
    # a git WRITE aimed at the GM own repo, by -C or by a cd into it
    host = r"/host-l7r-repo"
    writes = r"\b(?:commit|push|add|rm|mv|reset|revert|checkout|switch|restore|merge|rebase|cherry-pick|clean|stash|tag|am|apply)\b"
    if re.search(POS + rf"git\b[^\n;|&]*-C\s+{host}\S*[^\n;|&]*{writes}", c):
        print("host-git-write"); raise SystemExit
    if re.search(rf"cd\s+{host}\S*[^\n]*?\bgit\b[^\n;|&]*{writes}", c, re.S):
        print("host-git-write"); raise SystemExit
print("ok")
')

# GUARD_EDIT_OK: feature 168 - every refusal is recorded, and the RULE is the verdict that produced it
# (`force-push`, `history-rewrite`, `host-git-write`). This guard has three rules and had no record at
# all, so "repo-safety fired" could not say which. Nothing it refuses changes, and the two rules with
# no escape still have none.
RS_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$RS_HERE/_guardlog.sh"
case "$VERDICT" in ok) ;; *) guard_log repo-safety blocked "$(guard_cmd)" "$VERDICT" ;; esac
case "$VERDICT" in
  force-push)
    cat >&2 <<'TAIL'
BLOCKED: git push --force.

CLAUDE.md calls this "the one thing that overwrites other sessions' work", and that is literal. The
GM runs several sessions at once, each in its own clone, all pushing to one main. A force push does
not lose YOUR work - it loses SOMEBODY ELSE'S, silently, and the person who discovers it is not the
person who did it.

There is no legitimate force push in this workflow. What you want instead:

  scripts/sync-with-main.sh done     locked pull-then-push, then render-sync
  git pull origin main               if the push was rejected, MERGE and push again

If a push is being refused and merging looks wrong, that is worth raising with the GM rather than
overwriting. There is deliberately no escape hatch here: "never" stops meaning never the moment one
exists.

(scripts/repo-safety-hooks.sh; CLAUDE.md session-clone workflow)
TAIL
    exit 2 ;;
  history-rewrite)
    cat >&2 <<'TAIL'
BLOCKED: a history rewrite (rebase, pull --rebase, merge --squash, or commit --amend).

This project never rewrites history (GM 2026-08-25, constitution VI): every landing is a real merge
commit with its parents intact. The history is the record of decisions, and the verified-tree
records, the perf-review records and the performance bookends are keyed by the commits and content
that were actually tested - a rewrite would throw a paid verification away without saying so.

What to do instead:
  - to bring main in:   scripts/sync-with-main.sh sync-in   (a merge, never a rebase)
  - to fix a commit:    make another commit that fixes it
  - to combine work:    a merge commit (git merge --no-edit <ref>)

No escape hatch: "never" stops meaning never the moment one exists. (GUARD_EDIT_OK: new guard)
TAIL
    exit 2 ;;
  host-git-write)
    cat >&2 <<'TAIL'
BLOCKED: a git write against /host-l7r-repo.

That is the GM's own repo, bind-mounted from their laptop. CLAUDE.md: "From inside the container,
never run `git commit` or `git push` against the mount." They do their own git there - a commit made
from here appears on their machine as work they did not do.

What IS allowed, and is not blocked:

  - EDITING files there. The Note Intake Workflow exists to append to setting/l7r.md.
  - READ-ONLY git: `git -C /host-l7r-repo log`, `diff`, `show`, `status`.

If a read-only command was misread as a write, put HOST_GIT_OK in it with a note - and say what it
false-positived on, because that is a bug in this hook.

(scripts/repo-safety-hooks.sh; CLAUDE.md "Canonical Source")
TAIL
    exit 2 ;;
esac
exit 0
