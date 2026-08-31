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
#                   main's tip (GM_ASSISTANT_ALLOW_MAIN=1 for that one sanctioned regen-in-main)
#   done            push, then render-sync (the common full stop-work)
set -euo pipefail

die() { echo "sync-with-main: $*" >&2; exit 1; }

# THE ROOT IS DERIVED, NOT HARDCODED (feature 131, 2026-08-25). A session clone lives at
# <main>/.clones/<name>, so main is the clone's grandparent - true for gm-assistant at /gm-assistant
# and for the diagram repository at /diagram, with no per-repo edit. CLONE_MAIN stays as the test
# seam. Before this the script hardcoded /gm-assistant, which is the kind of reference the split
# had to sweep; deriving it means the NEXT move is free.
ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || die "not inside a git checkout"
if [ -n "${CLONE_MAIN:-}" ]; then MAIN=$CLONE_MAIN
elif [ "$(basename "$(dirname "$ROOT")")" = ".clones" ]; then MAIN=$(dirname "$(dirname "$ROOT")")
else MAIN=$ROOT; fi
LOCK=$MAIN/.clones/.sync.lock   # keep this NAME: it is the cross-session lock convention in CLAUDE.md - renaming it stops serializing against sessions still on the old name (renamed ONCE, 2026-08-28, from the "ritual" name the GM retired; a clone syncs in every turn, so the window was minutes)
POOL=.claude/skills/diagram/pool
# The FROZEN tree is checked alongside it: render-sync must never rewrite an exhibit, and the
# dirty-pool warning below is what would say so (feature 161).
LEGACY_POOL=.claude/skills/diagram/legacy-hand-authored-pool
SKILL_DIR=.claude/skills/diagram
RENDER_CACHE_MOD=l7r.diagram.pipeline.render_cache   # run as a MODULE from SKILL_DIR: it imports its package siblings relatively

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

# GITHUB MAIN IS MAIN (feature 130, FR-001, research R7). The clone's `origin` and the mirror's are
# GitHub over HTTPS - the container has no SSH key, and the public repository needs no credential
# to READ; a push presents the PAT through GIT_ASKPASS (scripts/git-askpass-token.sh) from
# development-secrets.ini, never on a command line. A remote still pointing at the local mirror or
# at the SSH URL is re-pointed here, once, and said so. CLONE_GITHUB stays as the test seam.
GITHUB_URL=${CLONE_GITHUB:-https://github.com/EliAndrewC/diagram}
ensure_github_origin() {
  local tree url
  for tree in "$ROOT" "$MAIN"; do
    url=$(git -C "$tree" remote get-url origin 2>/dev/null || true)
    if [ "$url" != "$GITHUB_URL" ]; then
      git -C "$tree" remote set-url origin "$GITHUB_URL" 2>/dev/null || git -C "$tree" remote add origin "$GITHUB_URL"
      echo "sync-with-main: origin of $tree -> $GITHUB_URL (was '${url:-none}'; GitHub main is the integration point since feature 130)"
    fi
  done
  export GIT_ASKPASS="$ROOT/scripts/git-askpass-token.sh" GIT_TERMINAL_PROMPT=0
  if [ -z "${GITHUB_TOKEN:-}" ] && [ -f "$ROOT/$SKILL_DIR/l7r/diagram/ci/config.py" ]; then
    GITHUB_TOKEN=$(cd "$ROOT/$SKILL_DIR" && python3 -c "import sys; from pathlib import Path; from l7r.diagram.ci.config import load_secrets; print(load_secrets(Path(sys.argv[1])).github_pat)" "$ROOT" 2>/dev/null || true)
    export GITHUB_TOKEN
  fi
}
ensure_github_origin

# THE MIRROR IS REFRESHED FROM GITHUB MAIN, UNDER THE LOCK, FAST-FORWARD ONLY (FR-030). It is
# nobody's workspace, so a refusal here means someone committed in main by hand - the procedure stops
# and says so rather than merging in the mirror. Render-sync follows, cache-short-circuited.
mirror_refresh() {
  flock "$LOCK" git -C "$MAIN" pull -q --ff-only origin main \
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
Main is a MIRROR and nobody's workspace: this is a commit made in main's tree, almost always a bare 'cd $MAIN' that leaked into the next command (CLAUDE.md, 'NAME THE TREE IN THE COMMAND'). It blocks EVERY clean clone, not just this one.
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
  local cache="$ROOT/.claude/skills/diagram/.gencache"
  [ -d "$cache" ] && return 0                      # already has one: the common case, costs one test
  local head sib_head sib
  head="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)" || return 0
  for sib in "$(dirname "$ROOT")"/*/; do
    [ "${sib%/}" = "$ROOT" ] && continue
    [ -d "$sib/.claude/skills/diagram/.gencache" ] || continue
    sib_head="$(git -C "$sib" rev-parse HEAD 2>/dev/null)" || continue
    [ "$sib_head" = "$head" ] || continue
    mkdir -p "$(dirname "$cache")" 2>/dev/null || return 0   # the skill dir exists in any real clone; a fixture may not have it
    cp -a "$sib/.claude/skills/diagram/.gencache" "$cache" 2>/dev/null || return 0
    echo "sync-with-main: seeded the roll cache from $(basename "${sib%/}") (same commit) - a cold clone pays ~2 min re-rolling maps"
    return 0
  done
}

sync_in() {
  git fetch -q origin || die "cannot fetch GitHub main from $GITHUB_URL"
  mirror_refresh
  render_sync
  seed_roll_cache
  if [ "${1:-}" = "--mirror-only" ]; then clone_index_refresh; echo "sync-with-main: mirror refreshed from GitHub main (clone left alone - mid-task)"; return 0; fi
  git pull --no-rebase origin main
  clone_index_refresh
  # No render pull-in anymore (GM 2026-07-22): its old rationale was that a clone's stale renders
  # would flow back into main via render-sync's copy - but render-sync no longer copies anything,
  # it REGENERATES main in place, so nothing flows clone -> main and the clone never needs main's
  # renders. A clone regenerates whatever map it iterates on; the GM browses renders in main.
  date > "$ROOT/.git/sync-with-main.stamp"
  echo "sync-with-main: clone synced with GitHub main (git)"
}

# THE CLONE GETS ITS OWN POOL INDEX (GM 2026-08-27). pool/index.html is derived and gitignored, and
# render-sync writes only main's - so a clone had none, and the GM could not use it as an index of
# that clone's work in progress. Refreshed on BOTH sync-in branches (a dirty, mid-task clone is
# exactly where a WIP index matters) through the skill's `pool-index-if-stale`, whose `find -newer`
# check makes a no-change turn cost milliseconds. Never fatal: a broken index must not stop a sync.
clone_index_refresh() {
  [ -f "$ROOT/$SKILL_DIR/Makefile" ] || return 0
  ( cd "$ROOT/$SKILL_DIR" && make --no-print-directory pool-index-if-stale ) \
    || echo "sync-with-main: WARNING - pool index refresh failed in the clone (run: make pool-index in $SKILL_DIR)" >&2
}

push_cmd() {
  [ -z "$(git status --porcelain)" ] || die "uncommitted changes - commit first (the procedure never writes your commit for you)"
  # DUPLICATE-DEF GUARD (GM 2026-07-24): a cross-session merge gave test_settlement.py two
  # _city() helpers - the later silently shadowed the earlier and broke a seeded test - and ruff
  # F811 cannot see this class (pyflakes only flags UNUSED redefinitions; an early helper is
  # always used before the shadow). Screened HERE so every push is covered, merges and
  # docs-only pushes included - the gates do not necessarily run for those. The selftest runs
  # first: a checker that cannot prove it still bites is the failure mode that motivated it.
  python3 "$ROOT/scripts/check-duplicate-defs.py" --selftest >/dev/null || die "check-duplicate-defs selftest failed - the guard itself is broken; fix scripts/check-duplicate-defs.py before pushing"
  python3 "$ROOT/scripts/check-duplicate-defs.py" "$ROOT" || die "duplicate top-level definitions (above) - a later def silently shadows the earlier; fix before pushing"
  # GUARD_EDIT_OK: feature 173 - the ~1,000-line bar (constitution Principle X clause 13), held on
  # BOTH routes. The gate holds it too (the skill Makefile's `lint`), but a docs- or tests-only delta
  # takes the DIRECT route and runs no gate at all - and a file crosses the bar one edit at a time,
  # which is precisely why the clause says the line must be CHECKED rather than felt. Selftest first,
  # same reason check-duplicate-defs does it.
  python3 "$ROOT/scripts/check-file-scale.py" --selftest >/dev/null || die "check-file-scale selftest failed - the guard itself is broken; fix scripts/check-file-scale.py before pushing"
  python3 "$ROOT/scripts/check-file-scale.py" "$ROOT" || die "a Python file is past the ~1,000-line bar (above) - constitution Principle X clause 13, gated since feature 173"
  # GREEN-GATE GUARD (constitution Principle XIII, GM 2026-08-17). The principle's enforcement
  # clause says this procedure "does not run to completion on a red or regressed state" - which was
  # ASPIRATIONAL until now: nothing here knew whether a gate had run, so compliance was a session
  # remembering to comply, the very shape the principle abolishes. Python-only and per-area, so a
  # docs-only push still skips the gate (CLAUDE.md) and a webapp change is not blocked by the
  # diagram gate. Selftest FIRST, same reason check-duplicate-defs does it: a checker that cannot
  # prove it still bites is the failure mode that motivated it.
  # GUARD_EDIT_OK: feature 170 - THE THIRD SILENT PERMIT, and the worst of them. This bypasses the
  # rule that nothing lands which a green gate did not see, and it recorded NOTHING: this file has no
  # `guard_log` call anywhere and never sourced `_guardlog.sh`, so `make audit` could not show that
  # the push guard had ever been worked around. Found by the round-2 review of this feature, which
  # derived the census from the tree rather than reading the session's list. The reason must also
  # clear the floor now - an environment variable's VALUE is its reason (GM 2026-08-30).
  if [ -n "${GATE_STAMP_OK:-}" ]; then
    # shellcheck source=/dev/null
    . "$ROOT/scripts/_guardlog.sh"
    if ! python3 "$ROOT/scripts/_hm_escape.py" reason-ok <<<"$GATE_STAMP_OK" >/dev/null; then
      guard_log sync-with-main blocked "$GATE_STAMP_OK" GATE_STAMP_OK-no-reason
      die "GATE_STAMP_OK needs a REASON, not just a value: two words and eight characters, e.g. GATE_STAMP_OK=\"the gate is green on this content, the stamp predates a docs-only commit\". An escape nobody can audit is indistinguishable from the rule not existing (GM 2026-08-30, feature 170)."
    fi
    guard_log sync-with-main escaped "$GATE_STAMP_OK" gate-stamp-ok
    echo "sync-with-main: green-gate guard BYPASSED - $GATE_STAMP_OK" >&2
  else
    python3 "$ROOT/scripts/gate-stamp.py" --selftest >/dev/null || die "gate-stamp selftest failed - the guard itself is broken; fix scripts/gate-stamp.py before pushing"
    python3 "$ROOT/scripts/gate-stamp.py" --check origin/main || die "push refused by the green-gate guard (above)"
  fi
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
  pointer=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("feature_directory","").rstrip("/"))' "$ROOT/.specify/feature.json" 2>/dev/null || true)
  for f in $(printf '%s\n' "$ours" | grep -oE '^specs/[^/]+' | sort -u) "$pointer"; do
    [ -n "$f" ] && [ -f "$ROOT/$f/tasks.md" ] && grep -qE '^\s*- \[ \]' "$ROOT/$f/tasks.md" && active="$active $f"
  done
  active=$(printf '%s\n' $active | sort -u | tr '\n' ' ' | sed 's/ *$//')
  if [ -n "$active" ]; then
    local outside
    outside=$(printf '%s\n' "$ours" | grep -vE "^(${active// /|})/" || true)
    if [ -n "$outside" ] || [ "$(printf '%s\n' $active | wc -l)" -gt 1 ]; then
      printf '\n\033[1mREFUSED: feature %s is IN PROGRESS (open tasks) - nothing lands on main until it is complete.\033[0m\n' "$active" >&2
      printf 'Neither route lands a feature in progress, and there is no flag. The one exception is a push of\n' >&2
      printf 'that feature'"'"'s own specs/ directory ALONE (the spec-number claim); this delta also touches:\n' >&2
      printf '%s\n' "$outside" | sed 's/^/  /' >&2
      printf 'Finish the feature (every task ticked, including the GM'"'"'s acceptance where the spec has one), or move the\nunrelated change to another clone. The work stays here - mid-task work is sacred.\n\n' >&2
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
  "$(dirname "$0")/review-gate.sh" || exit 1
  # THE PERFORMANCE BANDS ARE ENFORCED HERE (feature 129, FR-001/FR-002/FR-009): the GM's words for
  # band 3 are "before it is committed back to main", so the push - not the gate - is where a
  # missing explanation, confirmation, audit or sign-off stops the work. `make perf-review` names
  # exactly which record is owed. CI_PERF_REVIEW is the test seam (a fixture has no skill).
  # THE TEST SEAMS ARE HONORED ONLY IN A FIXTURE (feature 132, Principle XIV - the fidelity
  # reviewer's aside): a tree with no diagram skill Makefile is the only tree the tests build, and
  # on a real clone `CI_ROUTE=DIRECT` would have skipped the gated route entirely. So the seams
  # (CI_PERF_REVIEW, CI_ROUTE, CI_MERGE) are read only when that Makefile is absent.
  local seams=""; [ -f "$ROOT/$SKILL_DIR/Makefile" ] || seams=1
  if [ -n "$seams" ] && [ -n "${CI_PERF_REVIEW:-}" ]; then bash -c "$CI_PERF_REVIEW"; elif [ -f "$ROOT/$SKILL_DIR/Makefile" ]; then ( cd "$ROOT/$SKILL_DIR" && make --no-print-directory perf-review ); else true; fi \
    || die "the performance bands owe a record (above) - the work stays in this clone until it exists (feature 129)"
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
  local route
  if [ -n "$seams" ] && [ -n "${CI_ROUTE:-}" ]; then route=$CI_ROUTE
  elif [ -f "$ROOT/$SKILL_DIR/Makefile" ]; then
    route=$( { cd "$ROOT/$SKILL_DIR" && make --no-print-directory ci-status ROUTE=1; } 2>/dev/null | tail -1 || true)
    # AN UNDECIDED ROUTE IS NOT A DIRECT ROUTE. If the dispatcher could not answer, engine code
    # could be sitting in the delta; falling through to the free push would land it ungated.
    case "$route" in DIRECT|GATED|GATED-LOCAL) ;; *) die "could not decide the route ('make ci-status ROUTE=1' said '${route:-nothing}') - not pushing. Run it by hand in $SKILL_DIR to see why." ;; esac
  else route=DIRECT; fi   # a tree with no diagram skill (a fixture) has nothing to gate
  case "$route" in
    GATED-LOCAL) echo "sync-with-main: route GATED (local - remote off): engine code in our delta, nothing dispatches; a green local make done on the merged engine content pushes, otherwise the work stays here" ;;
    *)           echo "sync-with-main: route $route (diagram engine code in our delta -> GATED, CodeBuild; otherwise DIRECT)" ;;
  esac
  if [ "$route" = GATED ] || [ "$route" = GATED-LOCAL ]; then
    if [ -n "$seams" ] && [ -n "${CI_MERGE:-}" ]; then bash -c "$CI_MERGE"; else ( cd "$ROOT/$SKILL_DIR" && make --no-print-directory ci-merge ${FULL:+FULL=1} ); fi \
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
  date > "$ROOT/.git/sync-with-main.stamp"  # post-push the clone is at main's tip = synced by definition
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
  # NO DIAGRAM SKILL, NO RENDER-SYNC (feature 131): gm-assistant no longer holds the skill, and the
  # diagram repository holds nothing else - one script serves both because this step is conditional.
  if [ ! -f "$MAIN/$SKILL_DIR/Makefile" ]; then echo "sync-with-main: no $SKILL_DIR/Makefile in $MAIN - render-sync skipped"; return 0; fi
  # REGENERATE main's diagram renders IN PLACE from main's own tip (GM 2026-07-22, replacing the
  # old build-in-clone-then-rsync-copy machinery). Renders now become a pure function of main's
  # committed code - nothing is copied, so nothing can be copied stale (the fragility that copy
  # approach had: whether a clone had touched a given render was situational, so a stale copy
  # could linger in main). l7r/diagram/pipeline/render_cache.py runs each generator FROM ITS OWN DIRECTORY (the Mode A
  # cwd trap) and short-circuits on a content hash stamped into each derived svg: an unconditional
  # post-push regen is therefore cheap - only maps whose source actually changed re-run, so a push
  # that touched no map's inputs costs ~0.3s while still self-healing every render from tip.
  #
  # Under the procedure LOCK for the whole regen: main is a push-to-checkout target (updateInstead),
  # so another session's push mid-regen would rewrite the engine under us and mix tips across maps.
  # GM_ASSISTANT_ALLOW_MAIN=1 stands the engine's main-tree guard down for this ONE sanctioned
  # regen-in-main. No tip-guard is needed - regenerating whatever tip main currently holds is
  # correct, and a second runner finds every stamp fresh and skips (the cache makes redundant
  # regens ~free, which is what retires the old TIP-GUARD/last-writer-wins hazard entirely).
  # THROUGH THE MAKE TARGET, not a bare interpreter (feature 127, FR-009). This was the last
  # operation in the repo invoked outside make, and it was exempted in an early draft of the spec on
  # the grounds that render-sync is a LEGITIMATE caller. The fidelity review rejected that: legitimate
  # WORK does not imply a legitimate INVOCATION ROUTE, and compliance cost exactly this line.
  (cd "$MAIN/$SKILL_DIR" && flock "$LOCK" env GM_ASSISTANT_ALLOW_MAIN=1 make --no-print-directory render-sync ARGS="--skill-dir $MAIN/$SKILL_DIR --main-repo $MAIN")
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

# `done FULL=1` / `push FULL=1`: the full sweep on CodeBuild, its prompt answered locally first
for arg in "$@"; do case "$arg" in FULL=1) export FULL=1 ;; esac; done
case "${1:-}" in
  sync-in)     sync_in "${2:-}" ;;
  push)        push_cmd ;;
  render-sync) render_sync ;;
  done)        push_cmd; render_sync ;;
  *)           die "usage: sync-with-main.sh sync-in | push | render-sync | done" ;;
esac
