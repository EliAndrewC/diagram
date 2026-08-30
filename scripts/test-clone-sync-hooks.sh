#!/usr/bin/env bash
# test-clone-sync-hooks.sh - exercise the pretool guards in clone-sync-hooks.sh and the
# gm-assistant refusal in sync-with-main.sh. These hooks govern EVERY session (all sessions run
# main's copy of clone-sync-hooks.sh via the absolute path in .claude/settings.json), so a bug
# here can block all editing - this suite is the regression guard. Run it from anywhere:
#   scripts/test-clone-sync-hooks.sh
# It builds throwaway git repos, fake session-json files, and real/killed processes for liveness,
# drives the hooks through the CLONE_MAIN / CLONE_SESSIONS_DIR test seams, and asserts exit codes.
set -uo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
HOOK=$HERE/clone-sync-hooks.sh
SYNC=$HERE/sync-with-main.sh
# GUARD_EDIT_OK: feature 168 - clone-sync-hooks.sh now RECORDS its five refusals, so this suite
# writes into a throwaway log rather than the session's real one; otherwise `make audit`'s census
# counts fixture firings as things that happened to a session.
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
trap 'rm -rf "$GUARD_LOG_ROOT"' EXIT
TMP=$(mktemp -d)
# NB: cleanup is done EXPLICITLY at the end, NOT via a `trap ... EXIT` - an EXIT trap also fires in
# the forked subshells that `&` background jobs and pipelines create, which would rm the fixtures
# mid-run (it did: standalone passed, `... | tail` wiped $TMP). A leaked /tmp dir on early abort is
# harmless.

FAILED=0
check() { # check <label> <expected-rc> <actual-rc>
  if [ "$2" = "$3" ]; then
    printf 'ok    %s (rc=%s)\n' "$1" "$3"
  else
    printf 'FAIL  %s (expected rc=%s, got rc=%s)\n      out: %s\n' "$1" "$2" "$3" "$OUT"
    FAILED=1
  fi
}

# ---- fixtures ---------------------------------------------------------------------------------
FMAIN=$TMP/main
git init -q "$FMAIN"
git -C "$FMAIN" config user.email t@t; git -C "$FMAIN" config user.name t
echo m0 > "$FMAIN/f"; git -C "$FMAIN" add f; git -C "$FMAIN" commit -qm m0
mkdir -p "$FMAIN/.clones/.session-clones"
MAPDIR=$FMAIN/.clones/.session-clones
SESS=$TMP/sessions; mkdir -p "$SESS"

mkclone() { git clone -q "$FMAIN" "$FMAIN/.clones/$1"; }   # a clone at main's current tip
mkclone miscellaneous
mkclone diagram-town
mkclone gm-assistant

# session-json fixtures: <pid>.json carries {id, name, nameSource}
sess() { printf '{"id":"%s","name":"%s"%s}' "$2" "$3" "${4:+,\"nameSource\":\"$4\"}" > "$SESS/$1.json"; }
sess 1001 sid-me miscellaneous            # named "miscellaneous" -> canon .clones/miscellaneous
sess 1002 sid-town "Diagram (town)"       # named -> canon .clones/diagram-town
sess 1003 sid-unnamed "Auto Title" derived  # derived title -> unnamed -> canon .clones/gm-assistant

# a LIVE process whose /proc cmdline names claude (via exec -a), and a DEAD one
bash -c 'exec -a claude-fake-live sleep 300' & LIVE_PID=$!
sess "$LIVE_PID" sid-live-other "Diagram (city)"
bash -c 'exec -a claude-fake-dead sleep 300' & DEAD_PID=$!
sess "$DEAD_PID" sid-dead-other "Diagram (hamlet)"
kill "$DEAD_PID" 2>/dev/null; wait "$DEAD_PID" 2>/dev/null || true

run() { # run <mode> <sid> <clonename> <file-under-clone> ; sets OUT/RC
  local fp="$FMAIN/.clones/$3/$4"
  OUT=$(printf '{"session_id":"%s","tool_input":{"file_path":"%s"}}' "$2" "$fp" \
        | CLONE_MAIN="$FMAIN" CLONE_SESSIONS_DIR="$SESS" "$HOOK" "$1" 2>&1); RC=$?
}

# ---- pretool scenarios ------------------------------------------------------------------------
OUT=$(printf '{"session_id":"sid-me","tool_input":{"file_path":"%s/README.md"}}' "$FMAIN" \
      | CLONE_MAIN="$FMAIN" CLONE_SESSIONS_DIR="$SESS" "$HOOK" pretool 2>&1); check "non-clone path ignored" 0 $?

run pretool sid-me miscellaneous a.txt;        check "canonical clone, clean, at tip, unclaimed" 0 "$RC"

# ---- transcript-first name resolution (GUARD_EDIT_OK: new test cases, GM 2026-08-27) -----------
# /clear mints a new session_id; the sessions json is rewritten asynchronously, the transcript's
# custom-title record is there before the first prompt. So the transcript outranks the json.
TR=$TMP/transcripts; mkdir -p "$TR"
runt() { # runt <mode> <sid> <transcript> <clonename> <file-under-clone> ; run + transcript_path
  local fp="$FMAIN/.clones/$4/$5"
  OUT=$(printf '{"session_id":"%s","transcript_path":"%s","tool_input":{"file_path":"%s"}}' "$2" "$3" "$fp" \
        | CLONE_MAIN="$FMAIN" CLONE_SESSIONS_DIR="$SESS" "$HOOK" "$1" 2>&1); RC=$?
}
title() { printf '{"type":"custom-title","customTitle":"%s","sessionId":"%s"}\n' "$1" "$2"; }
{ title "Diagram (town)" sid-cleared; echo '{"type":"user","message":{"role":"user","content":"hi"}}'; } > "$TR/cleared.jsonl"
runt pretool sid-cleared "$TR/cleared.jsonl" diagram-town a.txt;   check "sid absent from sessions json, transcript names it -> resolves, allowed" 0 "$RC"
runt pretool sid-cleared "$TR/cleared.jsonl" miscellaneous a.txt;  check "sid absent from sessions json, transcript names another clone -> routing block" 2 "$RC"
{ title miscellaneous sid-me; title "Diagram (town)" sid-me; } > "$TR/renamed.jsonl"   # renamed twice; json says miscellaneous
runt pretool sid-me "$TR/renamed.jsonl" diagram-town a.txt;        check "transcript outranks the sessions json; LAST rename wins" 0 "$RC"
runt pretool sid-me "$TR/renamed.jsonl" miscellaneous a.txt;       check "transcript outranks the sessions json (json's own clone now blocked)" 2 "$RC"
echo '{"type":"user","message":{"role":"user","content":"custom-title mentioned in prose only"}}' > "$TR/plain.jsonl"
runt pretool sid-me "$TR/plain.jsonl" miscellaneous a.txt;         check "transcript without a rename record -> sessions json fallback" 0 "$RC"
runt pretool sid-me "$TR/missing.jsonl" miscellaneous a.txt;       check "transcript path that does not exist -> sessions json fallback" 0 "$RC"
rm -f "$MAPDIR/sid-cleared" "$MAPDIR/sid-me"

printf '%s' "$FMAIN/.clones/miscellaneous" > "$MAPDIR/sid-live-other"
run pretool sid-me miscellaneous a.txt;        check "canonical clone claimed by a LIVE other session -> blocked" 2 "$RC"
rm -f "$MAPDIR/sid-live-other"

printf '%s' "$FMAIN/.clones/miscellaneous" > "$MAPDIR/sid-dead-other"
run pretool sid-me miscellaneous a.txt;        check "canonical clone claimed by a DEAD other session -> allowed" 0 "$RC"
rm -f "$MAPDIR/sid-dead-other"

run pretool sid-me diagram-town a.txt;         check "wrong (but valid) clone, clean -> name-routing block" 2 "$RC"

echo dirt > "$FMAIN/.clones/diagram-town/dirt"
run pretool sid-me diagram-town a.txt;         check "wrong clone but DIRTY -> grandfathered" 0 "$RC"
rm -f "$FMAIN/.clones/diagram-town/dirt"

run pretool sid-me gm-assistant a.txt;         check "editing forbidden gm-assistant clone -> blocked" 2 "$RC"
run pretool sid-unnamed miscellaneous a.txt;   check "unnamed session (resolves to gm-assistant) -> blocked" 2 "$RC"
run pretool sid-ghost miscellaneous a.txt;     check "unresolvable sid, clean, at tip, unclaimed -> allowed (fall-through)" 0 "$RC"

echo dirt > "$FMAIN/.clones/miscellaneous/dirt"
run pretool sid-me miscellaneous a.txt;        check "dirty canonical clone -> sacred, allowed" 0 "$RC"
rm -f "$FMAIN/.clones/miscellaneous/dirt"

# stale-base: a dedicated main advanced one commit past its clone
FMAIN2=$TMP/main2; git init -q "$FMAIN2"; git -C "$FMAIN2" config user.email t@t; git -C "$FMAIN2" config user.name t
echo a > "$FMAIN2/f"; git -C "$FMAIN2" add f; git -C "$FMAIN2" commit -qm a
mkdir -p "$FMAIN2/.clones"; git clone -q "$FMAIN2" "$FMAIN2/.clones/miscellaneous"
echo b > "$FMAIN2/f"; git -C "$FMAIN2" commit -qam b   # advance main past the clone
OUT=$(printf '{"session_id":"sid-me","tool_input":{"file_path":"%s/.clones/miscellaneous/a.txt"}}' "$FMAIN2" \
      | CLONE_MAIN="$FMAIN2" CLONE_SESSIONS_DIR="$SESS" "$HOOK" pretool 2>&1); check "canonical clone behind main -> sync-in block" 2 $?

# ...but a clone that is merely AHEAD of main (the normal state right after committing your own
# work, before the push back) must keep working. The equality test this replaced blocked it, which
# deadlocked every multi-commit work unit - GM-reported 2026-07-25, spec-kit's per-step commits.
FMAIN3=$TMP/main3; git init -q "$FMAIN3"; git -C "$FMAIN3" config user.email t@t; git -C "$FMAIN3" config user.name t
echo a > "$FMAIN3/f"; git -C "$FMAIN3" add f; git -C "$FMAIN3" commit -qm a
mkdir -p "$FMAIN3/.clones"; git clone -q "$FMAIN3" "$FMAIN3/.clones/miscellaneous"
git -C "$FMAIN3/.clones/miscellaneous" config user.email t@t; git -C "$FMAIN3/.clones/miscellaneous" config user.name t
echo c > "$FMAIN3/.clones/miscellaneous/f"; git -C "$FMAIN3/.clones/miscellaneous" commit -qam c  # clone ahead, tree clean
OUT=$(printf '{"session_id":"sid-me","tool_input":{"file_path":"%s/.clones/miscellaneous/a.txt"}}' "$FMAIN3" \
      | CLONE_MAIN="$FMAIN3" CLONE_SESSIONS_DIR="$SESS" "$HOOK" pretool 2>&1); check "canonical clone AHEAD of main, clean -> allowed" 0 $?

# a DIVERGED clone (each side has a commit the other lacks) is still stale and must block
git -C "$FMAIN3" commit -q --allow-empty -m d   # main advances too, after the clone's own commit
OUT=$(printf '{"session_id":"sid-me","tool_input":{"file_path":"%s/.clones/miscellaneous/a.txt"}}' "$FMAIN3" \
      | CLONE_MAIN="$FMAIN3" CLONE_SESSIONS_DIR="$SESS" "$HOOK" pretool 2>&1); check "canonical clone diverged from main -> sync-in block" 2 $?

# ---- sync-with-main.sh gm-assistant refusal ---------------------------------------------------
OUT=$(cd "$FMAIN/.clones/gm-assistant" && CLONE_MAIN="$FMAIN" "$SYNC" sync-in 2>&1); RC=$?
check "procedure refuses to run from .clones/gm-assistant" 1 "$RC"
case $OUT in *"FORBIDDEN"*) : ;; *) echo "FAIL  procedure refusal message missing 'FORBIDDEN': $OUT"; FAILED=1 ;; esac

# ---- sync-with-main.sh establishes repo-local git config itself (GUARD_EDIT_OK: new test case) --
# A fresh checkout of main lacks receive.denyCurrentBranch=updateInstead and a fresh clone copies
# no committer identity; both refused the split repository's first push (2026-08-25). The procedure
# now sets them, so a bare fixture must push cleanly and end up configured.
FMAIN5=$TMP/main5
git init -q -b main "$FMAIN5"   # the push-time guards check against origin/main, so the fixture's branch must be main
( export GIT_AUTHOR_NAME=Eli GIT_AUTHOR_EMAIL=eli@t GIT_COMMITTER_NAME=Eli GIT_COMMITTER_EMAIL=eli@t
  echo m0 > "$FMAIN5/f"; git -C "$FMAIN5" add f; git -C "$FMAIN5" commit -qm m0 )
mkdir -p "$FMAIN5/.clones/.session-clones"
git clone -q "$FMAIN5" "$FMAIN5/.clones/bare"
cp -r "$HERE" "$FMAIN5/.clones/bare/scripts"   # the push runs review-gate.sh and check-duplicate-defs.py from the clone
mkdir -p "$FMAIN5/.clones/bare/.claude/skills/x" && echo 'def a(): return 1' > "$FMAIN5/.clones/bare/.claude/skills/x/a.py"   # check-duplicate-defs refuses to scan nothing
( export GIT_AUTHOR_NAME=x GIT_AUTHOR_EMAIL=x@t GIT_COMMITTER_NAME=x GIT_COMMITTER_EMAIL=x@t
  echo c1 > "$FMAIN5/.clones/bare/g"; git -C "$FMAIN5/.clones/bare" add g scripts .claude; git -C "$FMAIN5/.clones/bare" commit -qm c1 )
( cd "$FMAIN5/.clones/bare" && python3 scripts/gate-stamp.py --write hooks )   # the commit changes scripts/, and a scripts/ change pushes only behind a green hooks-test stamp (GUARD_EDIT_OK: fixture follows the new gate)
[ -z "$(git -C "$FMAIN5" config --get receive.denyCurrentBranch || true)" ] || { echo "FAIL  fixture: main5 already had denyCurrentBranch"; FAILED=1; }
OUT=$(cd "$FMAIN5/.clones/bare" && HOME=$TMP CLONE_MAIN="$FMAIN5" CLONE_GITHUB="$FMAIN5" "$SYNC" push 2>&1); RC=$?   # CLONE_GITHUB: the fixture main stands in for GitHub (GUARD_EDIT_OK: feature 130 made origin = GitHub)
check "procedure push from a bare fixture (no updateInstead, no identity) succeeds" 0 "$RC"
[ "$(git -C "$FMAIN5" config --get receive.denyCurrentBranch)" = updateInstead ] || { echo "FAIL  procedure did not set updateInstead on main: $OUT"; FAILED=1; }
[ "$(git -C "$FMAIN5/.clones/bare" config --get user.email)" = eli@t ] || { echo "FAIL  procedure did not set the clone's identity from main's tip author: $OUT"; FAILED=1; }
[ "$(git -C "$FMAIN5" log -1 --format=%s)" = c1 ] || { echo "FAIL  push-to-checkout did not land on main5: $OUT"; FAILED=1; }

# ---- prompt-mode: the .specify/feature.json re-track guard -------------------------------------
# The pointer must stay gitignored. common.sh resolves FEATURE_DIR from it at priority 2, ABOVE the
# SPECIFY_FEATURE env var at priority 3, so a TRACKED copy merges between concurrent sessions and
# silently redirects setup-plan/setup-tasks/implement into a PEER's specs/NNN-*/ while
# CURRENT_BRANCH still reads correctly (measured on features 115/116, 2026-08-16).
FMAIN4=$TMP/main4
git init -q "$FMAIN4"
git -C "$FMAIN4" config user.email t@t; git -C "$FMAIN4" config user.name t
echo m0 > "$FMAIN4/f"; git -C "$FMAIN4" add f; git -C "$FMAIN4" commit -qm m0
mkdir -p "$FMAIN4/.clones/.session-clones"
git clone -q "$FMAIN4" "$FMAIN4/.clones/fjclone"
FJC=$FMAIN4/.clones/fjclone
git -C "$FJC" config user.email t@t; git -C "$FJC" config user.name t
mkdir -p "$FJC/.specify"
echo '{"feature_directory":"specs/999-peer"}' > "$FJC/.specify/feature.json"
git -C "$FJC" add -f .specify/feature.json; git -C "$FJC" commit -qm "track the pointer"
echo scratch > "$FJC/scratch"   # dirty: the hook stops before its sync-in path, which needs no fixture
printf '%s' "$FJC" > "$FMAIN4/.clones/.session-clones/sid-fj"

OUT=$(printf '{"session_id":"sid-fj"}' \
      | CLONE_MAIN="$FMAIN4" CLONE_GITHUB="$FMAIN4" CLONE_SESSIONS_DIR="$SESS" "$HOOK" prompt 2>&1); RC=$?
check "tracked feature.json -> prompt still exits 0 (warn, never block)" 0 "$RC"
case $OUT in *"feature.json is TRACKED"*) printf 'ok    tracked feature.json is named in the warning\n' ;;
             *) printf 'FAIL  tracked feature.json produced no warning\n      out: %s\n' "$OUT"; FAILED=1 ;; esac
case $OUT in *"git rm --cached"*) printf 'ok    warning carries the fix command\n' ;;
             *) printf 'FAIL  warning omits the fix command\n      out: %s\n' "$OUT"; FAILED=1 ;; esac

# once per session - a warning that repeats every prompt is noise the GM learns to skip
OUT=$(printf '{"session_id":"sid-fj"}' \
      | CLONE_MAIN="$FMAIN4" CLONE_GITHUB="$FMAIN4" CLONE_SESSIONS_DIR="$SESS" "$HOOK" prompt 2>&1)
case $OUT in *"feature.json is TRACKED"*) printf 'FAIL  warning repeated (should be once per session)\n'; FAILED=1 ;;
             *) printf 'ok    warning is once per session\n' ;; esac

# and it must stay SILENT once the pointer is properly untracked, or it is a permanent false alarm
git -C "$FJC" rm -q --cached .specify/feature.json; git -C "$FJC" commit -qm untrack
rm -f "$FMAIN4/.clones/.session-clones/sid-fj.feature-json-notice"
OUT=$(printf '{"session_id":"sid-fj"}' \
      | CLONE_MAIN="$FMAIN4" CLONE_GITHUB="$FMAIN4" CLONE_SESSIONS_DIR="$SESS" "$HOOK" prompt 2>&1)
case $OUT in *"feature.json is TRACKED"*) printf 'FAIL  warning fires on an UNTRACKED pointer\n      out: %s\n' "$OUT"; FAILED=1 ;;
             *) printf 'ok    silent when the pointer is untracked\n' ;; esac

[ -n "${LIVE_PID:-}" ] && kill "$LIVE_PID" 2>/dev/null; true
rm -rf "$TMP"
echo "-----"
[ "$FAILED" = 0 ] && echo "all clone-sync-hook tests passed" || { echo "SOME TESTS FAILED"; exit 1; }
