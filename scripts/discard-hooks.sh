#!/usr/bin/env bash
# discard-hooks.sh - Claude Code harness hook that BLOCKS a git command that would DISCARD
# uncommitted work in a tracked file: `git checkout -- <path>`, `git checkout <path>`,
# `git restore <path>`, `git checkout .`, `git restore .`, `git checkout HEAD -- <path>`.
# (GUARD_EDIT_OK: feature 133 T33 - a new guard, the GM's instruction 2026-08-27)
#
# WHY (GM 2026-08-27, feature 133 T33: "The fabricated shortcut should ideally have some extra
# tooling to block it from happening since it costs time"). On T31 a session typed
# `git checkout -- l7r/diagram/hamletgen/ways.py` into a command as a NOTE - the text after it read
# "(checkout would discard my diff - NOT run)" - and the shell ran it. The working diff of the task
# was gone; five minutes went on recovering it from the transcript, and the task that should have
# taken ten minutes took thirty-nine. The mistake is structural rather than careless: a session
# composes a command as prose and the shell reads it as instructions, so the only safe rule is that
# a command which throws away uncommitted work never runs unannounced.
#
# WHAT IT CHECKS. Only commands that DISCARD: a checkout or restore whose target is a PATH (not a
# branch or a ref), or `.`/`*`. For each named path it asks git whether the file actually has
# uncommitted changes in the tree the command names (`git -C <dir>` or the cwd); a clean file is
# let through - restoring a file you have not touched costs nothing. `--staged`-only restores keep
# the worktree and pass. Branch switches (`git checkout main`) pass; branch CREATION is
# no-branch-hooks.sh's business. `git stash` is left alone here: the clone doctrine already says
# never to stash (it mutates the tree under a review agent), and a stash is recoverable.
#
# ESCAPE HATCH. Put DISCARD_OK in the command, with a note saying why - reverting a file
# deliberately is legitimate and common. It is deliberately visible in the transcript.
#
# Wired from .claude/settings.json alongside the other hooks. Tested by test-discard-hooks.sh.

set -u
MODE="${1:-}"
INPUT=$(cat 2>/dev/null || true)
[ "$MODE" = "pretool" ] || exit 0

CMD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception: print("")' 2>/dev/null || true)
[ -n "$CMD" ] || exit 0

# GUARD_EDIT_OK: feature 168 - this guard RECORDS what it does (GM 2026-08-30). Nothing it refuses or
# permits changes; the escape especially is recorded, because the escape RATE is what this project
# acts on - `discard` was escaped in 5 of 5 firings, which is how its merge-verb narrowing was found.
DG_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$DG_HERE/_guardlog.sh"
# GUARD_EDIT_OK: feature 169 - the escape is an INVOCATION, not a mention (was `case *DISCARD_OK*`).
if [ -n "$(printf '%s' "$INPUT" | "$DG_HERE/_hookmatch.py" escape DISCARD_OK 2>/dev/null)" ]; then
  guard_log discard escaped "$(guard_cmd)" discard-ok; exit 0
fi
case "$CMD" in *"git checkout"*|*"git restore"*|*"git -C"*) ;; *) exit 0 ;; esac

# Parse every git invocation in the command (they may be chained with && ; |) and collect the
# paths a checkout/restore would overwrite in the worktree. Then ask git which of them are dirty.
DIRTY=$(printf '%s' "$CMD" | DISCARD_CWD="$PWD" python3 -c '
import os, re, shlex, subprocess, sys
cmd = sys.stdin.read()
targets = []  # (repo_dir, path)
for piece in re.split(r"&&|\|\||;|\|", cmd):
    try:
        toks = shlex.split(piece, comments=True)
    except ValueError:
        toks = piece.split()
    if "git" not in toks:
        continue
    g = toks.index("git")
    rest = toks[g + 1 :]
    repo = os.environ.get("DISCARD_CWD", ".")
    while rest and rest[0] in ("-C", "-c") and len(rest) >= 2:
        if rest[0] == "-C":
            repo = rest[1]
        rest = rest[2:]
    if not rest:
        continue
    sub, args = rest[0], rest[1:]
    if sub not in ("checkout", "restore"):
        continue
    if sub == "checkout" and any(a in ("-b", "-B", "--branch", "--orphan") for a in args):
        continue  # branch creation: no-branch-hooks.sh
    if sub == "restore" and "--staged" in args and "--worktree" not in args and "-W" not in args:
        continue  # index only; the worktree keeps its changes
    # GUARD_EDIT_OK: feature 165 - A MERGE OWN CONFLICT-RESOLUTION VERB IS NOT A DISCARD. The GM
    # ruled on this (2026-08-30) on measured evidence: of this guard five recorded firings, ONE was
    # a `git checkout --ours` mid-merge. While `MERGE_HEAD` exists, `--ours` / `--theirs` picks a
    # SIDE of a conflict, which is the normal way to resolve one - and the "uncommitted work" this
    # guard protects is a session own edits, which a conflicted file content is not. Outside a merge
    # those flags mean something else entirely and are refused exactly as before, as is a plain
    # `git checkout -- <path>` on a dirty file INSIDE one. The wider option - trusting the flags
    # without the merge test - was never on the table.
    #
    # `git checkout --ours .` (whole-tree) is permitted here too, and safely: git skips every
    # non-conflicted path with "does not have our version", so nothing uncommitted can be lost that
    # way. Written down here because spec-fidelity asked for it at the point of change.
    #
    # NOTE FOR THE NEXT EDITOR: this whole parser lives inside a shell single-quoted string, so an
    # APOSTROPHE here ends the program and the hook dies with a syntax error. That has now cost two
    # separate features a debugging cycle each.
    if any(a in ("--ours", "--theirs") for a in args):
        gitdir = subprocess.run(
            ["git", "-C", repo, "rev-parse", "--git-dir"], capture_output=True, text=True
        ).stdout.strip()
        if gitdir and os.path.exists(os.path.join(repo, gitdir) if not os.path.isabs(gitdir) else gitdir):
            head = os.path.join(repo, gitdir, "MERGE_HEAD") if not os.path.isabs(gitdir) else os.path.join(gitdir, "MERGE_HEAD")
            if os.path.exists(head):
                continue  # a merge is in progress: this is resolution, not a discard
    paths = []
    seen_dashdash = False
    for a in args:
        if a == "--":
            seen_dashdash = True
            continue
        if not seen_dashdash and a.startswith("-"):
            continue
        paths.append(a)
    if sub == "checkout" and not seen_dashdash:
        # `git checkout X`: a branch or ref switch is fine; a PATH discards. The first token is a
        # ref when git says it is one and no file of that name is dirty.
        if len(paths) == 1 and "/" not in paths[0] and "." not in paths[0] and paths[0] not in (".", "*"):
            continue
        if paths and paths[0] in ("HEAD",) or (paths and re.fullmatch(r"[0-9a-f]{7,40}", paths[0])):
            paths = paths[1:]  # `git checkout HEAD -- path` without the dashes
    for p in paths:
        targets.append((repo, p))
dirty = []
for repo, p in targets:
    try:
        out = subprocess.run(["git", "-C", repo, "status", "--porcelain", "--", p], capture_output=True, text=True, timeout=5).stdout
    except Exception:
        out = ""
    changed = [ln[3:] for ln in out.splitlines() if ln[:2].strip() and ln[:2] != "??"]
    dirty.extend(changed)
print("\n".join(dict.fromkeys(dirty)))
' 2>/dev/null || true)
[ -n "$DIRTY" ] || exit 0

echo "BLOCKED (discard): this command would throw away UNCOMMITTED work in:
$(printf '%s\n' "$DIRTY" | sed 's/^/  /')

A checkout or restore of a modified file cannot be undone - git keeps no copy of what it
overwrites. On 2026-08-27 (feature 133 T31) a session lost its whole working diff to a
\`git checkout -- ways.py\` typed into a command as a NOTE, and spent five minutes recovering it from
the transcript; the ten-minute task took thirty-nine.

If you mean it: commit first (mid-task commits inside your clone are always fine), or put
DISCARD_OK in the command with a note saying why. If you did not mean it, the command was carrying
text the shell read as an instruction - rewrite it without the checkout.
(scripts/discard-hooks.sh; feature 133 T33)" >&2
guard_log discard blocked "$(guard_cmd)" would-discard-dirty   # GUARD_EDIT_OK: feature 168
exit 2
