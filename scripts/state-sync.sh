#!/usr/bin/env bash
# TOOL_RECORD: every run appends one line to <common .git>/tooling-state.log (utc, action, outcome, seconds, bytes, what a restore brought) - dev/audits/tooling-state.md's falsifier reads it
# state-sync.sh push [--detach] | restore [--if-fresh] [<clone name>] - THE PER-CLONE TOOLING STATE, KEPT OFF THE CONTAINER
# (feature 451 T258; the GM 2026-11-25: "I created https://github.com/EliAndrewC/diagram-tooling-state for the tooling state").
#
# WHAT. A clone's check answers (<common .git>/record-checks, 2,837 small files that churn) and its event logs (<common .git>/l7r-events,
# append-only, 122 MB) live only in that clone's .git, so a lost container lost every check answer and every measurement. `push`
# commits both into a bare mirror at <common .git>/tooling-state.git and pushes the branch named for the clone (a worktree's is its
# clone's); `restore` fetches that branch (or another clone's, by name) and MERGES it in: an answer by its record's utc, the newer
# kept with every fingerprint either answered (`l7r-gate record merge-answers`, the answer store's one other writer), a log by the
# lines the local one lacks, appended (its readers sort by `t`). Nothing local is overwritten by something older, nothing is removed.
#
# THE REPOSITORY IS PRIVATE: never link or copy what it holds anywhere public.
#
# WHY A GIT MIRROR, NOT TAR SNAPSHOTS (measured 2026-11-25 on diagram-backlog's state, a local bare remote): a tar.gz of both is
# 33.8 MB and 4.7 s EVERY landing; the mirror's first push is one pack of about 28 MB, and a landing after it sends only what changed.
# WHY THE LOGS ARE SEGMENTED (SEGMENT bytes a file, whole lines, `split -C`): a log is append-only but one file, so committed whole
# each landing stored a new 35-38 MB blob (the mirror grew 9 MB a commit, measured), and GitHub refuses a file over 100 MB, which
# 449's log (38.6 MB) would have reached - a push failing for good. Segments of an append-only file never change but the last.
#
# IT REFUSES NO LANDING AND DELAYS NONE: `push` exits 0 whatever happens, a failure is one line and a log line; `push --detach` (what
# `make land` and `make land-tooling` run, after their own push) returns at once, the push running on in its own session, and says
# the last push's failure if it failed. One run at a time (flock): a second push while one runs is skipped, the next landing's carries it.
# Never a force push: a branch another container moved is fetched, merged in as a restore is, and pushed on top.
#
# THE TOKEN is the project's (`l7r-gate github-token`), handed to git through GIT_ASKPASS (git-askpass-token.sh) as sync-with-main.sh
# hands it: never printed, never on a command line, never in a config. Seams (tests/hooks/test-state-sync.sh): STATE_REMOTE (the
# remote; a test's is a local bare fixture), STATE_SEGMENT. With no STATE_REMOTE, a clone whose origin is not GitHub main's does
# nothing - a fixture clone of another suite can never reach the real repository.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACTION=${1:-}; [ $# -gt 0 ] && shift
case "$ACTION" in push) SAY=state-push ;; restore) SAY=state-restore ;; *) echo "usage: state-sync.sh push [--detach] | restore [--if-fresh] [<clone name>]" >&2; exit 2 ;; esac
DETACH=""; FRESH=""; FROM=""
for a in "$@"; do case "$a" in --detach) DETACH=1 ;; --if-fresh) FRESH=1 ;; *) FROM=$a ;; esac; done

C=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || { echo "$SAY: not inside a git checkout" >&2; [ "$ACTION" = push ] && exit 0; exit 1; }
OWNER=$(dirname "$C")            # the clone the common .git belongs to: a worktree's state is its clone's
CLONE=$(basename "$OWNER")
FROM=${FROM:-$CLONE}
M="$C/tooling-state.git"; STAGE="$C/tooling-state.stage"; LOG="$C/tooling-state.log"; LOCK="$C/tooling-state.lock"
# 8 MB a segment: a GUESS knob. Smaller is less re-sent and re-stored per landing (the last segment of each log that grew, about a
# tenth of it once compressed) and more files; anything under GitHub's 100 MB a file works.
SEGMENT=${STATE_SEGMENT:-8m}
GITHUB_MAIN=https://github.com/EliAndrewC/diagram
if [ -z "${STATE_REMOTE:-}" ] && [ "$(git config --get remote.origin.url 2>/dev/null)" != "$GITHUB_MAIN" ]; then
  [ -n "$FRESH" ] || echo "$SAY: skipped - this clone's origin is not $GITHUB_MAIN, and no STATE_REMOTE names a remote"
  exit 0
fi
REMOTE=${STATE_REMOTE:-https://github.com/EliAndrewC/diagram-tooling-state}
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE

# --if-fresh (sync-with-main.sh sync-in, the session-clone setup): a clone with no mirror yet restores once, in the background;
# the mirror is made here, so it is asked once whatever the fetch does (a later push fetches again).
if [ -n "$FRESH" ]; then
  [ -e "$M" ] && exit 0
  git init -q --bare "$M" 2>/dev/null || exit 0
  setsid "$0" restore </dev/null >/dev/null 2>&1 &
  exit 0
fi
if [ -n "$DETACH" ]; then
  last=$(grep '"action": "push"' "$LOG" 2>/dev/null | tail -1)
  case "$last" in *'"outcome": "failed'*) echo "$SAY: the last push FAILED (${last#*\"outcome\": }) - log: $LOG" ;; esac
  setsid "$0" push </dev/null >/dev/null 2>&1 &
  echo "$SAY: started in the background (log: $LOG)"
  exit 0
fi

T0=${EPOCHREALTIME/,/.}
BYTES=0; ANSWERS=0; LINES=0
finish() { # <outcome> [exit]: the run's one line and its log line
  local s; s=$(awk -v a="$T0" -v b="${EPOCHREALTIME/,/.}" 'BEGIN { printf "%.1f", b - a }')
  rm -rf "$STAGE"
  printf '{"utc": "%s", "action": "%s", "clone": "%s", "branch": "%s", "outcome": "%s", "s": %s, "bytes": %s, "answers": %s, "lines": %s}\n' \
    "$(date -u +%FT%TZ)" "$ACTION" "$CLONE" "$FROM" "${1//\"/\'}" "$s" "$BYTES" "$ANSWERS" "$LINES" >> "$LOG"
  case "$1" in
    failed*) echo "$SAY: FAILED - ${1#failed: } (log: $LOG)" ;;
    *) echo "$SAY: $1 (${s} s)" ;;
  esac
  exit "${2:-0}"
}
exec 9>"$LOCK"
if [ "$ACTION" = push ]; then flock -n 9 || { echo "$SAY: another run holds $LOCK - skipped, the next landing's push carries this state"; exit 0; }
else flock 9; fi

case "$REMOTE" in https://*)
  export GIT_ASKPASS="$HERE/git-askpass-token.sh"
  if [ -z "${GITHUB_TOKEN:-}" ]; then GITHUB_TOKEN=$(cd "$HERE/.." && scripts/gates/l7r-gate.sh github-token 2>/dev/null </dev/null || true); fi
  export GITHUB_TOKEN ;;
esac
export GIT_TERMINAL_PROMPT=0
g() { git --git-dir="$M" -c credential.helper= -c user.name=tooling-state -c user.email=tooling-state@localhost -c gc.auto=0 "$@"; }
[ -d "$M" ] || git init -q --bare "$M" || finish "failed: cannot make the mirror $M" 1
ERR=$(mktemp); TMP=""; trap 'rm -rf "$ERR" "$TMP"' EXIT
why() { tr '\n' ' ' < "$ERR" | cut -c1-200; }

fetch() { # <branch>: 0 fetched into refs/remotes/state/<branch>, 1 the remote holds no such branch, 2 the remote was not reached
  local heads
  heads=$(g ls-remote --heads "$REMOTE" "refs/heads/$1" 2>"$ERR") || return 2
  [ -n "$heads" ] || return 1
  g fetch -q "$REMOTE" "+refs/heads/$1:refs/remotes/state/$1" 2>"$ERR" || return 2
}
merge_in() { # <ref>: that commit's answers and logs merged into this clone's, nothing newer overwritten
  local before name target
  TMP=$(mktemp -d); mkdir "$TMP/.git"
  g archive "$1" 2>"$ERR" | tar -x -C "$TMP/.git" || return 1
  before=$(find "$C/record-checks" -name '*.json' 2>/dev/null | wc -l)
  "$HERE/gates/l7r-gate.sh" record merge-answers "$TMP" "$OWNER" 2>"$ERR" || return 1
  ANSWERS=$(( ANSWERS + $(find "$C/record-checks" -name '*.json' 2>/dev/null | wc -l) - before ))
  mkdir -p "$C/l7r-events"
  for seg in "$TMP"/.git/l7r-events/*/; do
    [ -d "$seg" ] || continue
    name=$(basename "$seg"); target="$C/l7r-events/$name"
    cat "$seg"* > "$TMP/log"
    before=$(wc -l < "$target" 2>/dev/null || echo 0)
    if [ -f "$target" ]; then awk 'NR == FNR { has[$0] = 1; next } !($0 in has)' "$target" "$TMP/log" >> "$target"
    else cp "$TMP/log" "$target"; fi
    LINES=$(( LINES + $(wc -l < "$target") - before ))
  done
  rm -rf "$TMP"; TMP=""
}
commit() { # the state as it stands, committed on the clone's branch over its tip and the remote's; 1 when nothing moved
  local tree mine theirs parents="" f name
  rm -rf "$STAGE"; mkdir -p "$STAGE/l7r-events" "$C/record-checks"
  for f in "$C"/l7r-events/*; do
    [ -f "$f" ] || continue
    name=$(basename "$f"); case "$name" in *.tmp) continue ;; esac
    mkdir "$STAGE/l7r-events/$name" && split -C "$SEGMENT" -d -a 4 "$f" "$STAGE/l7r-events/$name/"
  done
  # two work trees, one index: the answers read where they lie (no copy), the logs from their segments
  g --work-tree="$C" add -A -- record-checks ':(exclude)record-checks/*.tmp' 2>"$ERR" || return 2
  g --work-tree="$STAGE" add -A -- l7r-events 2>"$ERR" || return 2
  tree=$(g write-tree 2>"$ERR") || return 2
  mine=$(g rev-parse -q --verify "refs/heads/$CLONE^{commit}"); theirs=$(g rev-parse -q --verify "refs/remotes/state/$CLONE^{commit}")
  [ -n "$mine" ] && parents="-p $mine"
  if [ -n "$theirs" ] && { [ -z "$mine" ] || ! g merge-base --is-ancestor "$theirs" "$mine"; }; then parents="$parents -p $theirs"; fi
  if [ -n "$mine" ] && [ "$parents" = "-p $mine" ] && [ "$(g rev-parse "$mine^{tree}")" = "$tree" ]; then return 1; fi
  # shellcheck disable=SC2086  # parents is a list of -p <sha>
  mine=$(g commit-tree "$tree" $parents -m "$CLONE: the tooling state at $(date -u +%FT%TZ)" 2>"$ERR") || return 2
  g update-ref "refs/heads/$CLONE" "$mine"
}

if [ "$ACTION" = restore ]; then
  fetch "$FROM"; rc=$?
  [ "$rc" = 2 ] && finish "failed: $REMOTE was not reached: $(why)" 1
  [ "$rc" = 1 ] && finish "the repository holds no branch $FROM - nothing to restore"
  merge_in "refs/remotes/state/$FROM" || finish "failed: the merge of $FROM stopped: $(why)" 1
  finish "restored $FROM: $ANSWERS answers new here, $LINES log lines new here; every answer both hold keeps the newer record"
fi

# push. A mirror that has never seen its branch (a fresh clone, a replacement container) takes the remote's state in first, so its
# first commit removes nothing the branch holds.
if ! g rev-parse -q --verify "refs/remotes/state/$CLONE" >/dev/null; then
  fetch "$CLONE"; rc=$?
  [ "$rc" = 2 ] && finish "failed: $REMOTE was not reached: $(why)"
  if [ "$rc" = 0 ]; then merge_in "refs/remotes/state/$CLONE" || finish "failed: the merge of the remote's $CLONE stopped: $(why)"; fi
fi
commit; rc=$?
[ "$rc" = 2 ] && finish "failed: the commit into $M stopped: $(why)"
if [ "$rc" = 1 ] && [ "$(g rev-parse -q --verify "refs/remotes/state/$CLONE")" = "$(g rev-parse -q --verify "refs/heads/$CLONE")" ]; then finish "unchanged - nothing to push"; fi
send() {
  local theirs; theirs=$(g rev-parse -q --verify "refs/remotes/state/$CLONE")
  # the bytes a push sends, for the log: the thin pack over what the remote holds, built once more (about 2 s of a detached run); a
  # branch's first push, the whole state, is not packed twice - its size is the mirror's pack, read below
  FIRST=""; if [ -n "$theirs" ]; then BYTES=$(printf '%s\n' "refs/heads/$CLONE" "^$theirs" | g pack-objects --thin --revs --stdout -q 2>/dev/null | wc -c); else FIRST=1; fi
  g push -q "$REMOTE" "refs/heads/$CLONE:refs/heads/$CLONE" 2>"$ERR" && g update-ref "refs/remotes/state/$CLONE" "refs/heads/$CLONE"
}
if ! send; then
  # refused or unreached: if the branch moved under us (another container on this clone's name), take its state in and push on top
  first=$(why); before=$(g rev-parse -q --verify "refs/remotes/state/$CLONE")
  fetch "$CLONE" || finish "failed: the push to $REMOTE: $first"
  [ "$(g rev-parse -q --verify "refs/remotes/state/$CLONE")" != "$before" ] || finish "failed: the push to $REMOTE: $first"
  merge_in "refs/remotes/state/$CLONE" || finish "failed: the merge of the remote's $CLONE stopped: $(why)"
  commit; [ $? = 2 ] && finish "failed: the commit into $M stopped: $(why)"
  send || finish "failed: the push to $REMOTE, after merging the branch's new state: $(why)"
fi
# the mirror kept small: each commit's loose blobs (the logs' last segments) packed against what it holds, off the landing's path
g repack -adq 2>/dev/null || :
[ -z "$FIRST" ] || BYTES=$(du -sb "$M/objects/pack" 2>/dev/null | cut -f1)
finish "pushed $CLONE ($BYTES bytes sent)"
