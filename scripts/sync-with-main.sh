#!/usr/bin/env bash
# sync-with-main.sh - keep a session clone and main in sync: pull main's tip into the clone
# (sync-in), push the clone's committed work back (push), and refresh main's diagram renders
# (render-sync). Encodes the stop-work procedure from CLAUDE.md as a script. (Renamed from its original name,
# GM 2026-07-21: name the purpose, not the culture. "Procedure", never "ritual", GM 2026-08-28: a
# ritual has religious meaning and the setting has real ones; this is a real-world process.)
#
# WHY (GM 2026-07-21): "if you're having to just remember to run the right commands in the right
# order then that seems error prone" - it was. Incidents that shaped this script, all from sessions
# hand-typing the procedure: a push raced another session because the flock was skipped; a render
# rsync ran from the wrong cwd and copied nothing; a cp with 2>/dev/null swallowed its own failure
# and the GM saw stale maps; a Mode A generator run from the skill dir wrote its cwd-relative
# outputs to the wrong path, which then got committed. The DOCTRINE lives in CLAUDE.md ("Session
# clones" / "Stop-work procedure") - this script is that doctrine made mechanical; if the two ever
# disagree, CLAUDE.md wins and this script has a bug.
#
# RENDER MODEL (GM 2026-07-22): renders no longer flow clone -> main by copy. render-sync
# REGENERATES main's diagram renders in place from main's own committed tip (via l7r/diagram/pipeline/render_cache.py),
# so a render in main is a pure function of main's code and can never be a stale copy. A content
# hash stamped into each derived svg makes the regen a cheap no-op when nothing a map depends on
# changed. This retired the whole copy machinery: no clone-side pre-render, no rsync, no tip-guard,
# no byte-verify, and sync-in no longer pulls renders into the clone.
#
# Run from anywhere INSIDE a session clone. Subcommands:
#   sync-in         start-of-work pull from main (near-free; almost always a fast-forward)
#   push            stop-work: refuse dirty tree, locked pull+push, overlap advisory (exit 3 =
#                   the pull merged other sessions' edits into files your commits touched -
#                   rerun the relevant gate NOW and fix forward)
#   render-sync     locked, cache-short-circuited regen of main's diagram renders IN PLACE from
#                   main's tip (DIAGRAM_ALLOW_MAIN=1 for that one sanctioned regen-in-main)
#   done            push, then render-sync (the common full stop-work)
set -euo pipefail

die() { echo "sync-with-main: $*" >&2; exit 1; }

# THE ROOT IS DERIVED, NOT HARDCODED (feature 131, 2026-08-25). A session clone lives at
# <main>/.clones/<name>, so main is the clone's grandparent - /diagram here, wherever it is mounted,
# with no per-repo edit (GUARD_EDIT_OK: comment only - gm-assistant's split-era copy has since
# diverged). CLONE_MAIN stays as the test
# seam. Before this the script hardcoded /gm-assistant, which is the kind of reference the split
# had to sweep; deriving it means the NEXT move is free.
ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || die "not inside a git checkout"
if [ -n "${CLONE_MAIN:-}" ]; then MAIN=$CLONE_MAIN
elif [ "$(basename "$(dirname "$ROOT")")" = ".clones" ]; then MAIN=$(dirname "$(dirname "$ROOT")")
else MAIN=$ROOT; fi
LOCK=$MAIN/.clones/.sync.lock   # keep this NAME: it is the cross-session lock convention in CLAUDE.md - renaming it stops serializing against sessions still on the old name (renamed ONCE, 2026-08-28, from the "ritual" name the GM retired; a clone syncs in every turn, so the window was minutes)
# THE PROMPT HOOK WAITS A BOUNDED TIME AND RENDERS IN THE BACKGROUND (2026-10-02; GUARD_EDIT_OK: the hook's own path
# gains a wait ceiling and a detached render, nothing refused is loosened). The hook runs sync-in on every message under
# a 60 s timeout, and render-sync held the lock 17-28 s per run (four sheets re-ran every time), so three sessions
# queued behind one another past 60 s and Claude Code killed the hook. `--background-render` (the hook's flag) waits at
# most SYNC_LOCK_WAIT seconds for the lock - busy past that, the mirror is skipped this turn and the clone still merges
# from GitHub - and hands render-sync to one detached runner that re-renders until main's tip holds still.
SYNC_LOCK_WAIT=${SYNC_LOCK_WAIT:-30}
RENDER_RUNNING=$MAIN/.clones/.render-sync.running   # the runner's own lock: one background render-sync at a time
RENDER_LOG=$MAIN/.clones/.render-sync.log
RENDER_STATUS=$MAIN/.clones/.render-sync.status     # "ok <when> at <tip>" or "FAILED <when> exit <rc> at <tip>"
POOL=pool
# The FROZEN tree is checked alongside it: render-sync must never rewrite an exhibit, and the
# dirty-pool warning below is what would say so (feature 161).
LEGACY_POOL=legacy-hand-authored-pool
RENDER_CACHE_MOD=l7r.diagram.pipeline.render_cache   # run as a MODULE from the root: it imports its package siblings relatively

case "$ROOT" in
  "$MAIN") die "this is MAIN, not a clone - the procedure runs from a session clone (CLAUDE.md 'Session clones')" ;;
  "$MAIN"/.clones/*) ;;
  *) die "$ROOT is not a session clone under $MAIN/.clones/" ;;
esac
# The repository's OWN NAME is a FORBIDDEN clone name (GM 2026-07-22, generalized 2026-08-25): it is
# the repository, not a session, and being the old unnamed-default is what let two sessions collide
# in one working tree. 'gm-assistant' stays forbidden everywhere for the same reason. The procedure
# refuses to run from such a clone so no work can be pushed out of it - rename the session distinctly.
case "$(basename "$ROOT")" in
  gm-assistant|"$(basename "$MAIN")") die "'.clones/$(basename "$ROOT")' is a FORBIDDEN clone name - it is the repository, not a session. Ask the GM to /rename this session to something distinct, then run the procedure from .clones/<that-name>. (CLAUDE.md 'Session clones')" ;;
esac
cd "$ROOT"

# REPO-LOCAL GIT CONFIG IS ESTABLISHED HERE, NOT BY HAND (GM 2026-08-25: "could they be done
# automatically?"). Two settings used to be one-time manual steps that a fresh checkout silently
# lacked - the split repository's first push was refused for both: main needs
# receive.denyCurrentBranch=updateInstead (the push-to-checkout this script relies on), and a fresh
# clone copies no user.name/user.email, so its first commit fails with "Author identity unknown".
# Neither is a write to main's TREE, so the procedure may set them; the identity is derived from the
# author of main's tip commit, which in this project is always the GM. Idempotent, and it says what
# it set so a surprising identity is visible rather than silent.
ensure_git_config() {
  if [ "$(git -C "$MAIN" config --get receive.denyCurrentBranch || true)" != updateInstead ]; then
    git -C "$MAIN" config receive.denyCurrentBranch updateInstead
    echo "sync-with-main: set receive.denyCurrentBranch=updateInstead on $MAIN (one-time, now automatic)"
  fi
  # THE IDENTITY COMES FROM THE GM'S SHARED ~/.claude/gitconfig (GM 2026-08-27, feature 133 T51),
  # included from ~/.gitconfig - written here as a backstop so a container that never re-ran
  # setup-dev-env.sh still picks it up on its next sync-in. Deriving it from main's tip author was
  # a loop: whatever address the last commit carried became the next commit's, forever. The tip
  # author is now only the fallback for a container with no shared identity at all.
  if [ -f "$HOME/.claude/gitconfig" ] && ! grep -qs 'claude/gitconfig' "$HOME/.gitconfig" 2>/dev/null; then
    printf '[include]\n\tpath = ~/.claude/gitconfig\n' >> "$HOME/.gitconfig"
    echo "sync-with-main: ~/.gitconfig now includes ~/.claude/gitconfig (the GM's shared identity)"
  fi
  local tree name email gname gemail
  # read the shared file itself: `git config --global --get` reads ~/.gitconfig alone and does not follow its include
  gname=$(git config --file "$HOME/.claude/gitconfig" --get user.name 2>/dev/null || true); gemail=$(git config --file "$HOME/.claude/gitconfig" --get user.email 2>/dev/null || true)
  for tree in "$MAIN" "$ROOT"; do
    if [ -n "$gemail" ]; then
      if [ "$(git -C "$tree" config --get user.email || true)" != "$gemail" ] || [ "$(git -C "$tree" config --get user.name || true)" != "$gname" ]; then
        git -C "$tree" config user.name "$gname" && git -C "$tree" config user.email "$gemail"
        echo "sync-with-main: set committer identity on $tree to '$gname <$gemail>' (from ~/.claude/gitconfig)"
      fi
    elif [ -z "$(git -C "$tree" config --get user.email || true)" ]; then
      name=$(git -C "$MAIN" log -1 --format=%an) && email=$(git -C "$MAIN" log -1 --format=%ae)
      [ -n "$email" ] || die "cannot derive a committer identity: $MAIN has no commits"
      git -C "$tree" config user.name "$name" && git -C "$tree" config user.email "$email"
      echo "sync-with-main: set committer identity on $tree to '$name <$email>' (from main's tip author - no ~/.claude/gitconfig found)"
    fi
  done
}
ensure_git_config

# GITHUB MAIN IS MAIN (feature 130, FR-001, research R7). The clone's `origin` is
# GitHub over HTTPS - the container has no SSH key, and the public repository needs no credential
# to READ; a push presents the PAT through GIT_ASKPASS (scripts/git-askpass-token.sh) from
# development-secrets.ini, never on a command line. A remote still pointing at the local mirror or
# at the SSH URL is re-pointed here, once, and said so. CLONE_GITHUB stays as the test seam.
# THE MIRROR'S `origin` IS THE GM'S, NOT OURS (GUARD_EDIT_OK: the GM asked for this, 2026-10-03). It used to be re-pointed to HTTPS too, which
# undid the GM's SSH remote on every sync, so a plain `git push`/`git pull` on the laptop asked for a
# username. The mirror is now refreshed from $GITHUB_URL by URL (mirror_refresh), straight into
# refs/remotes/origin/main, which the guards here and in clone-sync-hooks.sh read - its remote's URL
# is never touched.
GITHUB_URL=${CLONE_GITHUB:-https://github.com/EliAndrewC/diagram}
ensure_github_origin() {
  local tree url
  for tree in "$ROOT"; do
    url=$(git -C "$tree" remote get-url origin 2>/dev/null || true)
    if [ "$url" != "$GITHUB_URL" ]; then
      git -C "$tree" remote set-url origin "$GITHUB_URL" 2>/dev/null || git -C "$tree" remote add origin "$GITHUB_URL"
      echo "sync-with-main: origin of $tree -> $GITHUB_URL (was '${url:-none}'; GitHub main is the integration point since feature 130)"
    fi
  done
  export GIT_ASKPASS="$ROOT/scripts/git-askpass-token.sh" GIT_TERMINAL_PROMPT=0
  if [ -z "${GITHUB_TOKEN:-}" ] && [ -f "$ROOT/l7r/diagram/ci/config.py" ]; then
    GITHUB_TOKEN=$(cd "$ROOT" && python3 -c "import sys; from pathlib import Path; from l7r.diagram.ci.config import load_secrets; print(load_secrets(Path(sys.argv[1])).github_pat)" "$ROOT" 2>/dev/null || true)
    export GITHUB_TOKEN
  fi
}
ensure_github_origin

# THE MIRROR IS REFRESHED FROM GITHUB MAIN, UNDER THE LOCK, FAST-FORWARD ONLY (FR-030). It is
# nobody's workspace, so a refusal here means someone committed in main by hand - the procedure stops
# and says so rather than merging in the mirror. Render-sync follows, cache-short-circuited.
mirror_refresh() { # [wait-seconds]: with one, returns 75 when the lock stays busy that long (the prompt hook's path)
  local rc=0
  # By URL, not by remote name: the mirror's `origin` is the GM's (see ensure_github_origin).
  local refresh='git -C "$M" fetch -q "$U" +refs/heads/main:refs/remotes/origin/main && git -C "$M" merge -q --ff-only refs/remotes/origin/main'
  if [ -n "${1:-}" ]; then flock -E 75 -w "$1" "$LOCK" env M="$MAIN" U="$GITHUB_URL" sh -c "$refresh" || rc=$?
  else flock "$LOCK" env M="$MAIN" U="$GITHUB_URL" sh -c "$refresh" || rc=$?; fi
  [ "$rc" = 75 ] && [ -n "${1:-}" ] && return 75
  # The mirror's own artifacts follow the project to the root after the fast-forward that moved it (feature 329,
  # FR-008): render-sync's renders, the pool index, the built record site. Idempotent and quiet when nothing is left.
  [ "$rc" = 0 ] && "$(dirname "${BASH_SOURCE[0]}")/reviews/layout_carry.sh" "$MAIN"
  [ "$rc" = 0 ] \
    || die "mirror $MAIN cannot fast-forward to GitHub main - someone committed there by hand (main is a MIRROR, nobody's workspace). Inspect 'git -C $MAIN log origin/main..HEAD' and move that work into a clone."
  # GUARD_EDIT_OK: feature 169 - `--ff-only` DOES NOT CATCH THE COMMON CASE, and the documentation
  # said it did. It fails on DIVERGENCE; a mirror that is merely AHEAD of GitHub - one stray commit
  # on top of main's tip, nothing new to pull - satisfies it and prints "Already up to date". So on
  # 2026-08-30, twice, a session committed into the mirror and every later `sync-in` reported
  # `clone synced with GitHub main` while the mirror carried a commit GitHub did not have and every
  # clean clone in the container was refused as stale. `CLAUDE.md` has always described this as
  # stopping the next sync-in; this is the check that makes that true.
  if git -C "$MAIN" rev-parse --verify -q origin/main >/dev/null 2>&1 \
     && ! git -C "$MAIN" merge-base --is-ancestor HEAD origin/main 2>/dev/null; then
    die "mirror $MAIN is AHEAD of GitHub main - it carries $(git -C "$MAIN" log -1 --format='%h %s') which GitHub does not have, so nothing was merged into this clone.
Main is a MIRROR and nobody's workspace: this is a commit made in main's tree, almost always a bare 'cd $MAIN' that leaked into the next command (docs/session-clones.md, 'Name the tree in the command'; GUARD_EDIT_OK: message pointer retargeted 2026-09-15, no rule changed). It blocks EVERY clean clone, not just this one.
It belongs to whoever made it - do NOT reset it unless it is yours, because the mirror's working tree may be the only copy. Recovery: format-patch or copy the content into THAT session's clone and commit it there, check 'git -C $MAIN status --porcelain' for untracked files a reset would destroy, then 'git -C $MAIN reset --hard origin/main'."
  fi
}

# SYNC-IN IS THE WHOLE FLOW (feature 130, FR-030, plan design note 8): fetch GitHub main -> mirror
# fast-forward -> render-sync in the mirror -> [clean clone only] merge into the clone. The prompt
# hook runs the mirror half on EVERY turn, dirty clone or not - mid-task work is sacred, the mirror
# is not anyone's work - and the clone half only when the clone is clean.
# A NEW CLONE BORROWS A SIBLING'S ROLL CACHE (feature 167, GM 2026-08-30).
#
# A clone that has never rolled pays about two minutes re-rolling maps another clone on this machine
# has already rolled from identical source: 30 s for the reference settlement and 122 s for the
# map-rolling gate tests, against 1 s and 21 s warm. Feature 167 made the cache portable (its
# dependency records are root-relative now), so the remaining piece is getting one.
#
# FROM A SIBLING, NOT FROM MAIN, and that is forced rather than preferred: main has no `.gencache` and
# cannot build one, because building one means running the tests and main is never a workspace.
#
# It cannot make a clone wrong. Every seeded entry faces exactly the same key check as one the clone
# built itself - engine module hashes, the recorded functions' sources, the interpreter, the renderer,
# the dependency state - so a seed at the wrong commit, or from a tree that differs by one function,
# simply misses and re-rolls. That is why the sibling's HEAD is checked but nothing is trusted.
seed_roll_cache() {
  local cache="$ROOT/.gencache"
  [ -d "$cache" ] && return 0                      # already has one: the common case, costs one test
  local head sib_head sib
  head="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)" || return 0
  for sib in "$(dirname "$ROOT")"/*/; do
    [ "${sib%/}" = "$ROOT" ] && continue
    [ -d "$sib/.gencache" ] || continue
    sib_head="$(git -C "$sib" rev-parse HEAD 2>/dev/null)" || continue
    [ "$sib_head" = "$head" ] || continue
    mkdir -p "$(dirname "$cache")" 2>/dev/null || return 0   # the skill dir exists in any real clone; a fixture may not have it
    cp -a "$sib/.gencache" "$cache" 2>/dev/null || return 0
    echo "sync-with-main: seeded the roll cache from $(basename "${sib%/}") (same commit) - a cold clone pays ~2 min re-rolling maps"
    return 0
  done
}

# A CLONE WHOSE HISTORY SHARES NO COMMIT WITH MAIN'S IS REFUSED (feature 301 FR-019; GUARD_EDIT_OK: a new refusal of a
# state that cannot occur until a history rewrite, nothing loosened). The scrub of 2026-10 rewrote main's history to drop
# the built record pages; a clone still on the old history would MERGE the two unrelated histories on its next pull and
# bring every dropped file back. The refusal names the re-clone that moves its work across.
refuse_unrelated_history() {
  git rev-parse -q --verify HEAD >/dev/null && git rev-parse -q --verify origin/main >/dev/null || return 0
  git merge-base HEAD origin/main >/dev/null 2>&1 && return 0
  die "this clone's history shares no commit with main's - main's history was rewritten (feature 301's scrub, dev/history-rewrite-301.md). A pull would merge the old history back in. Re-clone it: git clone $MAIN $ROOT.new, cherry-pick any unpushed commits (git log --oneline HEAD --not --remotes), then replace $ROOT"
}

sync_in() { # [--mirror-only] [--background-render]
  # BOUNDED AND BACKGROUND, AND NO LOCK AT ALL WHEN THE MIRROR IS AT THE TIP (feature 442): a sync-in run by hand took the mirror
  # lock unbounded and rendered in the foreground, and after a landing it waited ~3 min behind that landing's own render-sync
  # (trial 441) - though the push had already brought the mirror to GitHub's tip. A foreground render by hand is `render-sync`.
  local mirror_only="" a
  for a in "$@"; do case "$a" in --mirror-only) mirror_only=1 ;; --background-render) : ;; esac; done
  git fetch -q origin || die "cannot fetch GitHub main from $GITHUB_URL"
  refuse_unrelated_history
  if [ "$(git -C "$MAIN" rev-parse -q --verify HEAD 2>/dev/null)" = "$(git rev-parse -q --verify origin/main)" ]; then
    render_sync_background  # the mirror already holds GitHub main: no refresh, no lock to wait on; the render runner (never blocking)
    # is still started, so a render an earlier pass FAILED is retried and its failure reported
  elif mirror_refresh "$SYNC_LOCK_WAIT"; then
    render_sync_background
  else
    echo "sync-with-main: NOTE - the mirror lock stayed busy for ${SYNC_LOCK_WAIT}s (a push or a render-sync holds it), so the mirror was not refreshed this turn; the next message retries"
  fi
  seed_roll_cache
  if [ -n "$mirror_only" ]; then clone_index_refresh; echo "sync-with-main: mirror refreshed from GitHub main (clone left alone - mid-task)"; return 0; fi
  # merge.directoryRenames: a file a clone added under a directory main renamed follows the rename instead of
  # stopping the merge (feature 329 moved the whole project; research.md R5 measured both outcomes). The global git
  # config sets it too, for the clones whose own copy of this script predates the move.
  git -c merge.directoryRenames=true pull --no-rebase origin main
  "$(dirname "${BASH_SOURCE[0]}")/reviews/layout_carry.sh" "$ROOT"   # this clone's artifacts follow the move (FR-008)
  clone_index_refresh
  clone_page_refresh
  # No render pull-in anymore (GM 2026-07-22): its old rationale was that a clone's stale renders
  # would flow back into main via render-sync's copy - but render-sync no longer copies anything,
  # it REGENERATES main in place, so nothing flows clone -> main and the clone never needs main's
  # renders. A clone regenerates whatever map it iterates on; the GM browses renders in main.
  date > "$(git -C "$ROOT" rev-parse --absolute-git-dir)/sync-with-main.stamp"
  echo "sync-with-main: clone synced with GitHub main (git)"
}

# THE CLONE GETS ITS OWN POOL INDEX (GM 2026-08-27). pool/index.html is derived and gitignored, and
# render-sync writes only main's - so a clone had none, and the GM could not use it as an index of
# that clone's work in progress. Refreshed on BOTH sync-in branches (a dirty, mid-task clone is
# exactly where a WIP index matters) through the skill's `pool-index-if-stale`, whose `find -newer`
# check makes a no-change turn cost milliseconds. Never fatal: a broken index must not stop a sync.
clone_index_refresh() {
  [ -f "$ROOT/Makefile" ] || return 0
  ( cd "$ROOT" && make --no-print-directory pool-index-if-stale ) \
    || echo "sync-with-main: WARNING - pool index refresh failed in the clone (run: make pool-index)" >&2
}

# THE CLONE'S PLACEMENT PAGE FOLLOWS THE CLASS REGISTRY (feature 278, FR-013; GUARD_EDIT_OK: a new operation, nothing
# loosened). The page is gitignored and re-plated at landing, on main, so a clone that merged a new class kept its old
# page and went red on `test_every_clickable_class_is_named_somewhere_on_the_committed_page` until someone re-plated
# by hand. After a merge only (a mid-task clone merged nothing), and only when the page's class stamp differs - the
# common sync costs one hash. Never fatal: a failed re-plate must not stop a sync, and the test still says what is wrong.
clone_page_refresh() {
  [ -f "$ROOT/Makefile" ] || return 0
  ( cd "$ROOT" && make --no-print-directory placement-stages-if-classes ) \
    || echo "sync-with-main: WARNING - placement page re-plate failed in the clone (run: make placement-stages)" >&2
}

push_cmd() {
  [ -z "$(git status --porcelain)" ] || die "uncommitted changes - commit first (the procedure never writes your commit for you)"
  git fetch -q origin 2>/dev/null && refuse_unrelated_history
  # GUARD_EDIT_OK: feature 385 T72 (plan D92) - the plan reviews' ledger rows, which their agents' `make plan-verdict` recorded, are
  # written and committed here as a record (as the cohort's and the gate's are); every other owed pass still refuses at the checks
  python3 "$ROOT/scripts/reviews/ledger_owed.py" --write-plan-reviews --ledger "$ROOT/dev/review-ledger.md" >&2 || :
  if git -C "$ROOT" rev-parse -q --verify HEAD >/dev/null && [ -n "$(git -C "$ROOT" status --porcelain -- dev/review-ledger.md 2>/dev/null)" ]; then  # T72: a fresh repo has no HEAD to diff
    git -C "$ROOT" commit -q -m "the plan reviews' ledger rows, written at landing (feature 385 T72)" -- dev/review-ledger.md || die "the plan reviews' ledger rows could not be committed"
  fi
  # THE CHEAP QUESTIONS FIRST (feature 405 T34, D6; landing-analysis.md): what holds the landing and the review gate's
  # occasions answer in under a second, and T12's landing met them only after push_checks.py and the claims gate had run.
  # So the fetch, the delta, the holding rule, the review gate and the plan gate come first; nothing else moved.
  # files OUR unpushed commits touch, captured BEFORE the pull so the overlap test is honest.
  # INCOMING files = what the pull moves HEAD across - NOT a diff against post-push origin/main,
  # which contains our own commits and false-flags every push (the script's own first dogfood run
  # caught exactly that bug: a no-op pull reported our just-pushed files as overlap).
  local base before ours theirs overlap
  git fetch -q origin || die "cannot fetch GitHub main from $GITHUB_URL"   # the delta and the route are judged against the LATEST main
  base=$(git rev-parse origin/main)
  before=$(git rev-parse HEAD)
  ours=$(git diff --name-only "$base"...HEAD | sort -u)
  # A FEATURE IN PROGRESS LANDS NOTHING - ON EITHER ROUTE (feature 133, GM 2026-08-25: *"even though
  # we are literally working on a feature and that feature is not yet done, you still pushed back to
  # main anyway. And that is the kind of thing that I am trying to prevent with this tooling."*).
  # The active feature is DERIVED, not declared, so it cannot be evaded by not setting the pointer:
  # any specs/NNN-*/tasks.md with an open box that (a) our delta touches, or (b) .specify/feature.json
  # names, is a feature in progress. While one exists the push is refused - DIRECT or GATED, no flag -
  # with ONE mechanical exception the GM kept: a delta consisting solely of that feature's own
  # specs/NNN-*/ directory (the spec-number claim for concurrent sessions). Nothing else rides along.
  local active="" pointer="" f
  # GUARD_EDIT_OK: feature 383 FR-006 - the Python calls from here on stay out of push_checks.py, each for one reason: it runs
  # after the fetch (the checks above precede it) and its answer is a VALUE the shell's own branches read - the feature
  # pointer, which features are in progress, the performance flag, the remote merge's route -
  # not a pass or refusal of its own. The escape reads (`hm_escape.py reason-ok`) run only when an escape is set.
  pointer=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("feature_directory","").rstrip("/"))' "$ROOT/.specify/feature.json" 2>/dev/null || true)
  for f in $(printf '%s\n' "$ours" | grep -oE '^specs/[^/]+' | sort -u) "$pointer"; do
    # feature 330 (FR-002, GUARD_EDIT_OK; plan review round 4): ANY open box still makes a feature in progress - indented,
    # unread or otherwise, as before - unless its spec's status line CLOSES it (Done, Superseded by, Withdrawn: the
    # words `speckit-todo.py` states once). The exemption fails closed: an error or no answer counts as not closed.
    # GUARD_EDIT_OK: feature 405 T32 (D4; the GM 2026-10-20: "I do not want each landing to owe a lands open line") - only the
    # task being worked holds a landing: `speckit-todo.py --holding` names the clone's active task (`make task-start`) while it
    # is open and `L7R_LAND_TICKS` (set by `make land`) does not name it; a task nobody has started holds nothing.
    if [ -n "$f" ] && [ -f "$ROOT/$f/tasks.md" ] && [ -n "$(python3 "$ROOT/scripts/speckit-todo.py" --holding "$ROOT/$f" 2>/dev/null || echo fail-closed)" ]; then
      [ "$(python3 "$ROOT/scripts/speckit-todo.py" --closed-by-status "$ROOT/$f" 2>/dev/null)" = yes ] || active="$active $f"
    fi
  done
  active=$(printf '%s\n' $active | sort -u | tr '\n' ' ' | sed 's/ *$//')
  # (the closing check - a touched feature that reads closed carries its report - runs in push_checks.py, above; feature 383)
  if [ -n "$active" ]; then
    local outside
    outside=$(printf '%s\n' "$ours" | grep -vE "^(${active// /|})/" || true)
    if [ -n "$outside" ] || [ "$(printf '%s\n' $active | wc -l)" -gt 1 ]; then
      printf '\n\033[1mREFUSED: feature %s has a task IN PROGRESS - its work lands with the task.\033[0m\n' "$active" >&2
      for f in $active; do python3 "$ROOT/scripts/speckit-todo.py" --holding "$ROOT/$f" 2>/dev/null | sed "s|^|  $f holds: |" >&2; done  # GUARD_EDIT_OK: feature 375 D18 - name the boxes that hold it
      printf 'Neither route lands a feature in progress, and there is no flag. The one exception is a push of\n' >&2
      printf 'that feature'"'"'s own specs/ directory ALONE (the spec-number claim); this delta also touches:\n' >&2
      printf '%s\n' "$outside" | sed 's/^/  /' >&2
      printf 'Land the task with `make land F=<n> T=<id>` (it checks the task'"'"'s tick, runs what the landing owes, pushes\nand ticks it), or move the unrelated change to another clone. The work stays here - mid-task work is sacred.\n\n' >&2
      exit 1
    fi
    echo "sync-with-main: feature $active is in progress - this push is its specs/ directory alone (the claim), allowed"
  fi
  # pull+push as ONE locked unit: no other session can slip a push into the gap (CLAUDE.md step 2).
  # HEAD:main, NOT main (GM 2026-07-27): `git push origin main` pushes the local REF NAMED main and
  # ignores what is checked out, so a session on any other branch silently pushed a stale ref and
  # got "! [rejected] main -> main (non-fast-forward)" while `git rev-list --count origin/main..HEAD`
  # reported it 4 ahead and 0 behind - every diagnostic says fast-forward and the error names a ref
  # you never touched. `HEAD:main` pushes what you actually committed.
  # THE MANDATED REVIEWS ARE CHECKED BEFORE THE PUSH, not after (feature 127 audit, 2026-08-24).
  # A spec ships with a fidelity verdict; a re-rolled Mode B map ships with its review logged. Both
  # were constitutional and unenforced, and both had already been skipped in practice. Checked here
  # because this is the moment work becomes everyone else's problem.
  "$(dirname "$0")/gates/review-gate.sh" || exit 1
  # GUARD_EDIT_OK: feature 243 - AND A PLAN'S DECISIONS ARE REVIEWED BEFORE ITS TASKS ARE TICKED. review-gate
  # holds the spec; a plan is written after that verdict and nothing read it, so a narrowing reached ticked
  # tasks and main unchecked (specs/243-*/research.md R1). `make tick` asks the same question, but a box can
  # be ticked by hand, so the push is where it holds.
  "$(dirname "$0")/gates/plan-gate.sh" || exit 1
  # GUARD_EDIT_OK: feature 383 FR-006 (the GM 2026-10-12: "Although I agree that the combining all the different checks into
  # one is lower impact, it does still seem worth doing") - THE PUSH'S PYTHON CHECKS RUN IN ONE PROCESS, in the order this
  # block ran them, each as it runs alone and each refusing with the line it refused with here: scripts/gates/push_checks.py
  # holds the table (duplicate defs, file scale, stale dirs, the function cap, the ledger, entry headings, research pointers,
  # partial citations, the download list, the record and glossary builds, spec-lint, the Affects line, conflict markers, the
  # green-gate stamp), every guard with its self-test first - run once per version of its code (FR-007). Why each runs HERE as
  # well as at the gate stands at its row there: a docs-, tests- or record-only delta takes the DIRECT route and runs no gate.
  # Every check the old block ran is in the table; nothing is loosened. The two escapes stay here, logged as before.
  local skip=()
  # shellcheck source=/dev/null
  . "$ROOT/scripts/hooks/lib/guardlog.sh" 2>/dev/null || guard_log() { :; }
  if [ -n "${LEDGER_ROWS_OK:-}" ]; then
    if ! python3 "$ROOT/scripts/hooks/lib/hm_escape.py" reason-ok <<<"$LEDGER_ROWS_OK" >/dev/null; then
      guard_log sync-with-main blocked "$LEDGER_ROWS_OK" LEDGER_ROWS_OK-no-reason
      die "LEDGER_ROWS_OK needs a REASON: two words and eight characters, saying why these passes land without their rows"
    fi
    guard_log sync-with-main escaped "$LEDGER_ROWS_OK" ledger-rows-ok
    echo "sync-with-main: ledger-row guard BYPASSED - $LEDGER_ROWS_OK" >&2
    skip+=(--skip ledger-owed)
  fi
  # GUARD_EDIT_OK: feature 170 - the green-gate guard's escape records its firing and needs a reason (an environment
  # variable's VALUE is its reason, GM 2026-08-30); an escape nobody can audit is indistinguishable from the rule not existing.
  if [ -n "${GATE_STAMP_OK:-}" ]; then
    if ! python3 "$ROOT/scripts/hooks/lib/hm_escape.py" reason-ok <<<"$GATE_STAMP_OK" >/dev/null; then
      guard_log sync-with-main blocked "$GATE_STAMP_OK" GATE_STAMP_OK-no-reason
      die "GATE_STAMP_OK needs a REASON, not just a value: two words and eight characters, e.g. GATE_STAMP_OK=\"the gate is green on this content, the stamp predates a docs-only commit\". An escape nobody can audit is indistinguishable from the rule not existing (GM 2026-08-30, feature 170)."
    fi
    guard_log sync-with-main escaped "$GATE_STAMP_OK" gate-stamp-ok
    echo "sync-with-main: green-gate guard BYPASSED - $GATE_STAMP_OK" >&2
    skip+=(--skip "gate-stamp selftest" --skip gate-stamp)
  fi
  # GUARD_EDIT_OK: feature 375 FR-009/FR-014, moved into the runner by feature 383 (its plan review: a pass or refusal with an
  # escape, as the two above) - a touched feature that reads closed carries its report and the measurements other specs
  # carried to it; a genuinely exempt case passes CLOSE_OK="<reason>", recorded
  if [ -n "${CLOSE_OK:-}" ] && python3 "$ROOT/scripts/hooks/lib/hm_escape.py" reason-ok <<<"$CLOSE_OK" >/dev/null 2>&1; then
    guard_log sync-with-main escaped "$CLOSE_OK" close-ok
    skip+=(--skip closing)
  fi
  python3 "$ROOT/scripts/gates/push_checks.py" "$ROOT" "${skip[@]}" || exit 1
  # THE SEAMS AND THE ROUTE, DECIDED BEFORE THE GATES (feature 430 T04): the cohort gate is the gated route's, and the gates the
  # route owes run side by side below. The seams and the routes are explained where the route is printed, further down.
  local seams=""; [ -f "$ROOT/Makefile" ] || seams=1
  local route
  if [ -n "$seams" ] && [ -n "${CI_ROUTE:-}" ]; then route=$CI_ROUTE
  elif [ -f "$ROOT/Makefile" ]; then
    route=$( { cd "$ROOT" && make --no-print-directory ci-status ROUTE=1; } 2>/dev/null | tail -1 || true)
    # AN UNDECIDED ROUTE IS NOT A DIRECT ROUTE. If the dispatcher could not answer, engine code
    # could be sitting in the delta; falling through to the free push would land it ungated.
    case "$route" in DIRECT|GATED|GATED-LOCAL) ;; *) die "could not decide the route ('make ci-status ROUTE=1' said '${route:-nothing}') - not pushing. Run it by hand to see why." ;; esac
  else route=DIRECT; fi   # a tree with no diagram skill (a fixture) has nothing to gate
  # the record gate and the claims gate are shell scripts with their own refusals, not Python checks (features 311, 316), and
  # the landing cohort's gate on the gated route (feature 386: a DIRECT delta changes no map). SIDE BY SIDE, EVERY REFUSAL
  # REPORTED (feature 430 T04, D4; the GM 2026-10-26, item 4): one after another they cost their sum - 5.7 s, 2.3 s and 8.8 s
  # measured 2026-10-26 (each timed alone, `specs/430-faster-landings/request.md`) - and the first refusal hid the rest
  local gates=(entry-gate claims-gate) gdir g failed=()
  { [ "$route" = GATED ] || [ "$route" = GATED-LOCAL ]; } && gates+=(cohort-gate)
  gdir=$(mktemp -d)
  for g in "${gates[@]}"; do ( "$ROOT/scripts/gates/$g.sh" > "$gdir/$g.log" 2>&1; echo $? > "$gdir/$g.rc" ) & done
  wait
  for g in "${gates[@]}"; do
    cat "$gdir/$g.log"
    [ "$(cat "$gdir/$g.rc" 2>/dev/null)" = 0 ] || failed+=("$g")
  done
  rm -rf "$gdir"
  [ "${#failed[@]}" = 0 ] || { printf 'sync-with-main: refused by %s - each refusal is above; nothing pushed\n' "${failed[*]}" >&2; exit 1; }
  # THE CALL COUNTS ARE WATCHED HERE, THE TIMINGS ONLY PRINTED (feature 427 T03, D3; the GM 2026-10-26: "keep recording the
  # timings, but completely stop using timings as a gate on anything ... the call counts themselves are the thing that we are
  # gating on"). `make perf-review` prints each pair's timing band for information and its call counts; it exits 1 when the
  # counts rose over the line, or cannot be compared, with no round-arbiter accept, and names the `make arbiter-ask` that asks.
  # It replaced the timing band's FLAG of feature 375 amendment 5. CI_PERF_REVIEW is the test seam (a fixture has no skill).
  # THE TEST SEAMS ARE HONORED ONLY IN A FIXTURE (feature 132, Principle XIV - the fidelity
  # reviewer's aside): a tree with no diagram skill Makefile is the only tree the tests build, and
  # on a real clone `CI_ROUTE=DIRECT` would have skipped the gated route entirely. So the seams
  # (CI_PERF_REVIEW, CI_ROUTE, CI_MERGE) are read only when that Makefile is absent.
  if [ -n "$seams" ] && [ -n "${CI_PERF_REVIEW:-}" ]; then bash -c "$CI_PERF_REVIEW"; elif [ -f "$ROOT/Makefile" ]; then ( cd "$ROOT" && make --no-print-directory perf-review ); else true; fi \
    || die "make perf-review refused (or failed to run) - the call counts above owe the round arbiter's accept, named with its command; a timing refuses nothing (feature 427 T03)"
  # THE WORK BUDGET'S RATCHET (feature 443 FR-006, plan D7): an ACCEPTED stage's counted operations may not grow past its accepted
  # figure or its budget; nothing to hold while no stage is accepted, or on a push with no engine code. No round-arbiter accept
  # clears it - the GM's words through `make budget-change` do. CI_WORK_BUDGET_REVIEW is its fixture seam, as CI_PERF_REVIEW is.
  if [ -n "$seams" ] && [ -n "${CI_WORK_BUDGET_REVIEW:-}" ]; then bash -c "$CI_WORK_BUDGET_REVIEW"; elif [ -f "$ROOT/Makefile" ]; then ( cd "$ROOT" && make --no-print-directory work-budget-review ROUTE="$route" ); else true; fi \
    || die "make work-budget-review refused (or failed to run) - an accepted stage's work above grew past its figure; only the GM's words through make budget-change raise it (feature 443)"
  # TWO ROUTES TO MAIN, CHOSEN BY THE DELTA, NEVER BY THE SESSION (feature 130, FR-002). The delta
  # is inspected against the LATEST GitHub main (fetched above). DIRECT: no diagram engine code in
  # our own commits - today's locked pull+push, free. GATED: engine code - `make ci-merge` runs the
  # dispatch conditions, and on DISPATCH a CodeBuild build merges the latest main into the work,
  # runs the gate and fast-forward-pushes the result to GitHub main itself; the clone then
  # fast-forwards to what landed. On SKIP-VERIFIED (a build already verified this exact tree) the
  # clone pushes directly. There is no local override of the gated route (FR-018): a gated delta
  # that cannot be dispatched stays in the clone. CI_ROUTE / CI_MERGE are the test seams.
  # THREE ROUTES since feature 132: GATED-LOCAL is the gated route with remote OFF (dev/switches.json)
  # - `make ci-merge` then dispatches nothing and answers SKIP-VERIFIED only when a green local
  # `make done` vouches for the merged engine content; otherwise the work stays in the clone.
  # (the route itself is decided above, before the gates - feature 430 T04)
  case "$route" in
    GATED-LOCAL) echo "sync-with-main: route GATED (local - remote off): engine code in our delta, nothing dispatches; a green local make done on the merged engine content pushes, otherwise the work stays here" ;;
    *)           echo "sync-with-main: route $route (diagram engine code in our delta -> GATED, CodeBuild; otherwise DIRECT)" ;;
  esac
  if [ "$route" = GATED ] || [ "$route" = GATED-LOCAL ]; then
    # GUARD_EDIT_OK: feature 386 - THE LANDING COHORT: engine work lands with 48 seeds rolled on its engine, none regressed
    # against main, and a fresh block whose rate is printed (the GM 2026-10-17). Its gate runs with the others above, on a
    # gated route only (feature 430 T04): a DIRECT delta changes no map.
    if [ -n "$seams" ] && [ -n "${CI_MERGE:-}" ]; then bash -c "$CI_MERGE"; else ( cd "$ROOT" && make --no-print-directory ci-merge ${FULL:+FULL=1} ); fi \
      || die "gated route: nothing landed (the conditions or the build refused - see above; the work stays in this clone)"
    case "$(cat "$ROOT/.git/ci-verdict" 2>/dev/null)" in
      SKIP-VERIFIED) flock "$LOCK" sh -c 'git pull --no-rebase origin main && git push origin HEAD:main' ;;
      *)             flock "$LOCK" git pull -q --ff-only origin main || die "the build landed the merge on GitHub main but this clone cannot fast-forward to it - inspect 'git log origin/main..HEAD'" ;;
    esac
  else
    flock "$LOCK" sh -c 'git pull --no-rebase origin main && git push origin HEAD:main'
  fi
  mirror_refresh
  theirs=$(git diff --name-only "$before"..HEAD | sort -u)
  date > "$(git -C "$ROOT" rev-parse --absolute-git-dir)/sync-with-main.stamp"  # post-push the clone is at main's tip = synced by definition
  # GUARD_EDIT_OK: feature 375 amendment 9, D55 - the work has landed: review-gate.sh's landing mark (glyph units due at once) ends
  rm -f "$(git -C "$ROOT" rev-parse --absolute-git-dir)/glyph-landing"
  overlap=$(comm -12 <(printf '%s\n' "$ours") <(printf '%s\n' "$theirs"))
  if [ -n "$overlap" ]; then
    echo "sync-with-main: PUSHED, but the pull auto-merged other sessions' edits into files your commits touched:" >&2
    printf '  %s\n' $overlap >&2
    echo "sync-with-main: rerun the relevant gate NOW and fix forward (CLAUDE.md stop-work step 3)" >&2
    # ...AND SAY THAT MAIN'S PICTURES ARE NOW STALE. `done` is push-then-render-sync, so this exit
    # skips render-sync and main keeps whatever renders it had - silently. The GM browses renders in
    # main, and on 2026-08-12 that cost a round trip: two syncs in a row hit this branch, so a map
    # whose connector had been re-routed right across the sheet still showed the old route, and the
    # GM reported the change had not happened. Regenerating from a tip whose gate has not been
    # re-run would be the wrong cure, so the exit stays - but the tip belongs in the message rather
    # than in a doc nobody re-reads (project rule: tips live in error output).
    echo "sync-with-main: NOTE - render-sync did NOT run, so main's diagram renders are now STALE." >&2
    echo "sync-with-main: once the gate is green again, run:  scripts/sync-with-main.sh render-sync" >&2
    exit 3
  fi
  echo "sync-with-main: pushed clean (no overlap with incoming changes)"
}

render_sync() {
  # NO MAKEFILE, NO RENDER-SYNC (feature 131): a leftover of the split, when gm-assistant ran this same
  # script without the diagram skill (GUARD_EDIT_OK: comment only - the two copies have since diverged).
  if [ ! -f "$MAIN/Makefile" ]; then echo "sync-with-main: no Makefile in $MAIN - render-sync skipped"; return 0; fi
  # REGENERATE main's diagram renders IN PLACE from main's own tip (GM 2026-07-22, replacing the
  # old build-in-clone-then-rsync-copy machinery). Renders now become a pure function of main's
  # committed code - nothing is copied, so nothing can be copied stale (the fragility that copy
  # approach had: whether a clone had touched a given render was situational, so a stale copy
  # could linger in main). l7r/diagram/pipeline/render_cache.py runs each generator FROM ITS OWN DIRECTORY (the Mode A
  # cwd trap) and short-circuits on a content hash stamped into each derived svg: an unconditional
  # post-push regen is therefore cheap - only maps whose source actually changed re-run, so a push
  # that touched no map's inputs costs little while still self-healing every render from tip. (It said ~0.3s; measured
  # 17-28 s on 2026-10-02 because the hand-drawn sheets were never cached - they are now, beside their tracked svg.)
  # GUARD_EDIT_OK: comment correction only
  #
  # Under the procedure LOCK for the whole regen: main is a push-to-checkout target (updateInstead),
  # so another session's push mid-regen would rewrite the engine under us and mix tips across maps.
  # DIAGRAM_ALLOW_MAIN=1 stands the engine's main-tree guard down for this ONE sanctioned
  # regen-in-main. No tip-guard is needed - regenerating whatever tip main currently holds is
  # correct, and a second runner finds every stamp fresh and skips (the cache makes redundant
  # regens ~free, which is what retires the old TIP-GUARD/last-writer-wins hazard entirely).
  # THROUGH THE MAKE TARGET, not a bare interpreter (feature 127, FR-009). This was the last
  # operation in the repo invoked outside make, and it was exempted in an early draft of the spec on
  # the grounds that render-sync is a LEGITIMATE caller. The fidelity review rejected that: legitimate
  # WORK does not imply a legitimate INVOCATION ROUTE, and compliance cost exactly this line.
  (cd "$MAIN" && flock "$LOCK" env DIAGRAM_ALLOW_MAIN=1 make --no-print-directory render-sync ARGS="--skill-dir $MAIN --main-repo $MAIN")
  # --skill-dir, not --pool: since feature 161 the pool is TWO trees under the skill dir
  # (pool/ live, legacy-hand-authored-pool/ frozen), and render_cache walks both from that one
  # root - it warns about a frozen exhibit whose render is missing, and that job followed the
  # exhibits out of pool/.
  # A generator writes its TRACKED .json (and a Mode A its tracked .svg) alongside the gitignored
  # renders; a deterministic gen reproduces those byte-identically, so main stays clean. If any
  # tracked pool file is left dirty, a generator is nondeterministic - surface it loudly (it would
  # also block the next session's updateInstead push), but do not auto-revert: the GM decides.
  local dirty
  dirty=$(git -C "$MAIN" status --porcelain -- "$POOL" "$LEGACY_POOL" | grep -E '^[ MARC]M ' || true)
  if [ -n "$dirty" ]; then
    echo "sync-with-main: WARNING - regen left tracked pool files dirty in main (a generator is nondeterministic):" >&2
    printf '%s\n' "$dirty" >&2
    echo "sync-with-main: investigate before the next push - main must be clean for updateInstead" >&2
  fi
}

# THE BACKGROUND RENDER (the prompt hook's path; see SYNC_LOCK_WAIT above). Detached from the hook - its own session,
# no inherited stdout - so the hook's `$(...)` returns at once and a killed hook cannot take the render down with it.
render_sync_background() {
  if [ ! -f "$MAIN/Makefile" ]; then echo "sync-with-main: no Makefile in $MAIN - render-sync skipped"; return 0; fi
  if grep -q '^FAILED' "$RENDER_STATUS" 2>/dev/null; then
    echo "sync-with-main: WARNING - the last background render-sync FAILED ($(cat "$RENDER_STATUS")), so main's renders may be stale; see $RENDER_LOG"
  fi
  setsid "$0" render-sync-runner </dev/null >>"$RENDER_LOG" 2>&1 &
  echo "sync-with-main: render-sync started in the background (log: $RENDER_LOG)"
}

# ONE RUNNER AT A TIME, AND IT CHASES THE TIP: a second start while one runs exits at once, so the running one re-checks
# main's tip after each pass and goes again if a later sync moved it. The one gap - a tip moved after that last check
# and before the runner lets go - is closed by the next message of any session.
render_sync_runner() {
  exec 9>"$RENDER_RUNNING"
  flock -n 9 || exit 0
  [ "$(stat -c %s "$RENDER_LOG" 2>/dev/null || echo 0)" -gt 1000000 ] && : > "$RENDER_LOG"
  local tip rc
  while :; do
    tip=$(git -C "$MAIN" rev-parse --short HEAD)
    echo "== $(date -Is) render-sync at $tip"
    rc=0; render_sync || rc=$?
    if [ "$rc" != 0 ]; then echo "FAILED $(date -Is) exit $rc at $tip" > "$RENDER_STATUS"; exit "$rc"; fi
    [ "$(git -C "$MAIN" rev-parse --short HEAD)" = "$tip" ] && break
  done
  echo "ok $(date -Is) at $tip" > "$RENDER_STATUS"
}

# UNLANDED WORK IS BACKED UP TO GITHUB AT EVERY STOP (feature 321, GM 2026-10-04; GUARD_EDIT_OK: a new step after the
# push, nothing refused is loosened). Until it lands, a clone's work existed only on the host's disk - a feature with
# open tasks cannot land, and on 2026-10-04 feature 319 held 34 commits nowhere else. So every stop (`done` or `push`,
# landed or refused) pushes HEAD to the remote-only branch backup/<clone-name>, and a branch whose tip main already
# holds is deleted: the GM's *"deleted after their contents have been merged into main, just to keep the branches that
# are visible manageable"*. At the stop only, never at sync-in: *"we shouldn't take the time to do a GitHub push like
# literally every time that we save a change"*.
#
# AN EXIT TRAP, NOT `( push_cmd ) || rc=$?`: bash ignores `set -e` inside a `||` context, so push_cmd's failed
# `flock ... git push` would fall through silently. The trap runs on every exit push_cmd takes and hands the code on
# unchanged. NOTHING HERE IS FATAL OR FORCED: a failure is one line, the backup push is fast-forward only, and a delete
# is a compare-and-delete (`--force-with-lease=<ref>:<tip judged contained>` - git's only conditional delete; it
# overwrites nothing) so a backup pushed between the fetch and the delete is kept.
backup_last() { # git's reason in one line: what the remote said and the rejection, without the boilerplate around them
  printf '%s\n' "$1" | grep -v -e '^\s*$' -e '^To ' -e 'failed to push some refs' -e '^hint:' \
    | sed -e 's/^\(error\|fatal\|remote\): *//' -e 's/^ *! *//' | paste -sd ';' | sed 's/;/; /g'
}

backup_delete() { # <branch> <tip judged contained in origin/main>
  local out
  # The lease here is a compare-and-DELETE, not a force: it only adds the condition "the remote still holds the tip
  # judged contained in main". Never copy it to a push that writes a tip - repo-safety-hooks.sh refuses that, rightly.
  if out=$(git push -q --force-with-lease="refs/heads/$1:$2" origin ":refs/heads/$1" 2>&1); then
    echo "sync-with-main: deleted $1 on GitHub - its work is on main"
  else
    echo "sync-with-main: $1 NOT deleted: $(backup_last "$out")" >&2
  fi
}

backup_step() {
  local name br tip head out b t
  # land-tooling's worktree (SYNC_BACKUP=off): its work is the clone's own commits, backed up at the clone's stop
  [ "${SYNC_BACKUP:-}" = off ] && return 0
  name=$(basename "$ROOT"); br=backup/$name
  if ! out=$(git fetch -q --prune origin 2>&1); then
    echo "sync-with-main: backup NOT checked - cannot reach origin: $(backup_last "$out")" >&2; return 0
  fi
  git rev-parse -q --verify refs/remotes/origin/main >/dev/null || { echo "sync-with-main: backup NOT checked - origin has no main" >&2; return 0; }
  head=$(git rev-parse HEAD) || return 0
  tip=$(git rev-parse -q --verify "refs/remotes/origin/$br" || true)
  if git merge-base --is-ancestor HEAD refs/remotes/origin/main; then
    if [ -n "$tip" ] && git merge-base --is-ancestor "$tip" refs/remotes/origin/main; then backup_delete "$br" "$tip"
    elif [ -n "$tip" ]; then echo "sync-with-main: $br on GitHub holds commits main lacks - kept (only a branch main contains is deleted)" >&2
    fi
  elif [ "$tip" = "$head" ]; then :
  elif [ -n "$tip" ] && ! git merge-base --is-ancestor "$tip" HEAD; then
    echo "sync-with-main: this clone's HEAD is NOT backed up - $br on GitHub holds commits HEAD lacks (a clone rebuilt under this name?); nothing was forced. The command below merges that backup's commits into this clone's HEAD, so they land on main with this clone's work - it is the GM's decision, never run by a session unasked:" >&2
    echo "  git -C $ROOT fetch origin refs/heads/$br && git -C $ROOT merge --no-edit FETCH_HEAD && git -C $ROOT push origin HEAD:refs/heads/$br" >&2
  elif out=$(git push -q --no-follow-tags origin "HEAD:refs/heads/$br" 2>&1); then
    echo "sync-with-main: backed up HEAD $(git rev-parse --short HEAD) to $br on GitHub (deleted once it lands on main)"
  else
    echo "sync-with-main: backup NOT pushed to $br: $(backup_last "$out")" >&2
  fi
  # THE SWEEP (FR-009): every other backup/* whose tip main holds - a clone abandoned after its work landed.
  while read -r b t; do
    b=${b#refs/remotes/origin/}
    [ "$b" = "$br" ] && continue
    git merge-base --is-ancestor "$t" refs/remotes/origin/main 2>/dev/null && backup_delete "$b" "$t"
  done < <(git for-each-ref --format='%(refname) %(objectname)' refs/remotes/origin/backup/)
  return 0
}

backup_on_exit() { # <the exit code the stop was leaving with>
  trap - EXIT; set +e
  backup_step
  exit "$1"
}

# `done FULL=1` / `push FULL=1`: the full sweep on CodeBuild, its prompt answered locally first
for arg in "$@"; do case "$arg" in FULL=1) export FULL=1 ;; esac; done
case "${1:-}" in
  sync-in)     shift; sync_in "$@" ;;
  push)        trap 'backup_on_exit $?' EXIT; push_cmd ;;
  render-sync) render_sync ;;
  render-sync-runner) render_sync_runner ;;
  # GUARD_EDIT_OK: feature 405 T35 (D7) - the landing returns once its work is on main; main's renders refresh behind it
  # (render_sync_background: the prompt hook's lock and log). A hand `render-sync` stays in the foreground.
  done)        trap 'backup_on_exit $?' EXIT; push_cmd; render_sync_background ;;
  *)           die "usage: sync-with-main.sh sync-in [--mirror-only] [--background-render] | push | render-sync | done" ;;
esac
