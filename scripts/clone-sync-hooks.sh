#!/usr/bin/env bash
# clone-sync-hooks.sh - Claude Code harness hooks enforcing the session-clone discipline.
#
# WHY (GM 2026-07-21): sync-in at the start of each work unit "has been getting skipped a lot and
# I'm not sure how to enforce it" - memory-dependent steps do get skipped, so the harness enforces
# them instead. Wired from .claude/settings.json (project settings, committed):
#
#   UserPromptSubmit -> `prompt` mode: every time the GM sends a message, this session's known
#     clone is auto-synced with main (git pull via sync-with-main.sh sync-in) - but ONLY when its
#     tree is clean; a dirty tree means mid-task, and yanking main's tip into half-done work would
#     be sabotage. Stdout is injected into the model's context, so the model also SEES the sync
#     happen (or why it was skipped).
#
#   PreToolUse (Edit|Write|NotebookEdit) -> `pretool` mode: at a CLEAN work-unit boundary it
#     enforces, in order: (0) FORBIDDEN NAME - '.clones/gm-assistant' is banned (it is the repo,
#     not a session), so a session that resolves or routes to it is stopped and the GM is asked to
#     name it; (1) NAME-ROUTING - a session may only edit in .clones/<its-own-name>, resolved from
#     its transcript's last /rename record, else ~/.claude/sessions/*.json; (2) CLAIM BACKSTOP - that clone must not be one
#     another LIVE session already occupies; (3) STALE-BASE - the clone's HEAD must equal main's. A
#     DIRTY tree is mid-task work and is sacred: never blocked (would strand in-flight work), only
#     its clone->session claim is recorded so the prompt hook can find it.
#
# WHY name-routing (GM 2026-07-22): the 2026-07-22 incident - TWO named sessions ("miscellaneous"
# and "Diagram (town)") both ignored their own names and defaulted to .clones/gm-assistant, sharing
# one working tree, which interleaved their uncommitted work and contaminated a gate. The fix is to
# ROUTE each session to .clones/<its-own-name> (deterministic from session_id -> sessions json ->
# name) and block edits anywhere else. The GM keeps unique session names, so the claim backstop is
# only a safety net for an accidental concurrent duplicate name; it uses DETERMINISTIC liveness
# (session_id -> PID = the sessions-json filename -> /proc) so a PREVIOUS same-named session's stale
# claim (e.g. the GM reuses "miscellaneous" across sessions) never blocks a legitimate new one - only
# a genuinely LIVE concurrent claimant does. HEAD equality, not timestamps, is the freshness test:
# needs no clock and cannot rot. Renders are no longer synced into the clone at all - render-sync
# REGENERATES main's renders in place from main's tip, so nothing flows clone -> main.
set -euo pipefail

SESSIONS_DIR=${CLONE_SESSIONS_DIR:-${HOME:-/home/agent}/.claude/sessions}  # CLONE_SESSIONS_DIR: test seam only
MODE=${1:-}
INPUT=$(cat 2>/dev/null || true)

field() { # field <dotted.path> - pull a string field out of the hook's stdin JSON
  printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    for k in '$1'.split('.'):
        d = d.get(k, {}) if isinstance(d, dict) else {}
    print(d if isinstance(d, str) else '')
except Exception:
    print('')"
}

# THE ROOT IS DERIVED FROM THE HOOK'S cwd, NOT HARDCODED (feature 131, 2026-08-25 - GUARD_EDIT_OK:
# the split needs one script that works in both repositories). The harness hands every hook the
# session's cwd; its git top level is either main itself or a clone at <main>/.clones/<name>, and
# main is the part before /.clones/. CLONE_MAIN stays as the test seam; the fallback when there is
# no cwd at all (a hook driven by hand with an empty payload) is the repository THIS script lives
# in - since feature 131 that is /diagram here and /gm-assistant there, so it cannot be a literal
# (GUARD_EDIT_OK: split residue - the literal named the OTHER repository's main).
derive_main() {
  local cwd top
  cwd=$(field cwd)
  top=$(git -C "${cwd:-/nonexistent}" rev-parse --show-toplevel 2>/dev/null || true)
  case "$top" in
    */.clones/*) printf '%s' "${top%%/.clones/*}" ;;
    "")          printf '%s' "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" ;;
    *)           printf '%s' "$top" ;;
  esac
}
MAIN=${CLONE_MAIN:-$(derive_main)}
MAPDIR=$MAIN/.clones/.session-clones

canonical_clone() { # canonical_clone <sid> [transcript] - print .clones/<kebab-name> for a session,
  # or "" if neither source names it (unresolvable -> caller falls through).
  # TWO SOURCES, transcript FIRST (GM 2026-08-27). /rename appends {"type":"custom-title"} to the
  # session's transcript (the hook input's transcript_path) synchronously, and /clear - which mints
  # a NEW session_id - re-emits it as line 1 of the new transcript before a first prompt can exist;
  # --resume carries it too. ~/.claude/sessions/<pid>.json is the running process's STATUS file,
  # rewritten asynchronously, so a lookup keyed by the post-/clear session_id could find no entry
  # yet and report "no human-given name" although the tab title (written from the same name) was
  # right all along. The sessions json stays as the FALLBACK, and remains the liveness source
  # (sid_is_live) - that is a different question and the PID filename answers it. The LAST
  # custom-title wins (a session renamed twice). An entry with a derived/auto title or blank name
  # is treated as UNNAMED -> the shared default, matching CLAUDE.md's naming rule.
  SID="$1" TP="${2:-}" MAIN="$MAIN" SDIR="$SESSIONS_DIR" python3 -c "
import glob, json, os, re, sys
sid, tp, main, sdir = os.environ['SID'], os.environ['TP'], os.environ['MAIN'], os.environ['SDIR']
if not sid:
    sys.exit(0)
name = source = None; found = False
if tp and os.path.isfile(tp):
    with open(tp, errors='replace') as fh:
        for line in fh:
            if 'custom-title' not in line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get('type') == 'custom-title' and str(r.get('customTitle') or '').strip():
                found, name, source = True, r['customTitle'], 'transcript'
for f in ([] if found else glob.glob(os.path.join(sdir, '*.json'))):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if sid in (d.get('id'), d.get('sessionId'), d.get('session_id')):
        found, name, source = True, d.get('name'), d.get('nameSource'); break
if not found:
    sys.exit(0)                       # unresolvable -> print nothing -> caller falls through
if source == 'derived' or not str(name or '').strip():
    name = 'gm assistant'             # unnamed / auto-derived -> shared default
kebab = re.sub(r'\s+', '-', re.sub(r'[^a-z0-9\s-]', '', str(name).lower()).strip())
if kebab:
    print(os.path.join(main, '.clones', kebab))"
}

sid_is_live() { # exit 0 iff a live process backs this session_id. The sessions-json FILENAME is the
  # session's PID; /proc/<pid> existing (cmdline naming claude, to survive PID reuse) means live.
  local sid="$1" pid
  pid=$(SID="$sid" SDIR="$SESSIONS_DIR" python3 -c "
import glob, json, os
sid, sdir = os.environ['SID'], os.environ['SDIR']
for f in glob.glob(os.path.join(sdir, '*.json')):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if sid in (d.get('id'), d.get('sessionId'), d.get('session_id')):
        print(os.path.splitext(os.path.basename(f))[0]); break")
  case $pid in ''|*[!0-9]*) return 1 ;; esac              # no numeric pid -> treat as not live
  [ -r "/proc/$pid/cmdline" ] || return 1
  tr '\0' ' ' < "/proc/$pid/cmdline" | grep -q claude
}

claim() { # record clone<-session_id so the prompt hook can find this session's clone
  [ -n "$sid" ] || return 0
  mkdir -p "$MAPDIR"
  printf '%s' "$clone" > "$MAPDIR/$sid"
}

case $MODE in
  pretool)
    # GUARD_EDIT_OK: feature 168 - this guard records what it does (GM 2026-08-30). It has FIVE
    # refusals - a forbidden name, a name routed to another session's clone, a live claim, a stale
    # HEAD - and no record at all, so nobody could tell which of them a session actually meets.
    # `cs_block` records the rule and refuses exactly as before; nothing it forbids changes.
    CS_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # shellcheck source=/dev/null
    . "$CS_HERE/_guardlog.sh"
    cs_block() { guard_log clone-sync blocked "${2:-}" "$1"; }
    fp=$(field tool_input.file_path)
    case $fp in
      "$MAIN"/.clones/*/*) ;;
      *) exit 0 ;;  # not a clone file - this hook has no opinion
    esac
    rest=${fp#"$MAIN"/.clones/}
    clone=$MAIN/.clones/${rest%%/*}
    [ -d "$clone/.git" ] || exit 0
    sid=$(field session_id)
    dirty=$([ -n "$(git -C "$clone" status --porcelain 2>/dev/null)" ] && echo 1 || true)
    canon=$(canonical_clone "$sid" "$(field transcript_path)")

    # DIRTY = mid-task work, sacred: allow (record the claim), never strand in-flight work on a
    # moving main. EVERY guard below is a clean-work-unit-boundary check only.
    if [ -n "$dirty" ]; then claim; exit 0; fi

    # --- clean work-unit boundary: enforce isolation before recording any claim ---

    # (0) 'gm-assistant' is a FORBIDDEN clone name (GM 2026-07-22): it is the repository, not a
    #     session, and being the old unnamed-default is exactly what made two sessions collide in
    #     it. A session that resolves to it has no distinct name; a session editing in it wandered
    #     into the forbidden workspace. Either way, stop and make the GM name the session.
    if [ -n "$canon" ] && [ "$(basename "$canon")" = "gm-assistant" ]; then
      echo "BLOCKED: this session has no distinct name - it resolves to the FORBIDDEN '.clones/gm-assistant' ('gm-assistant' is the repository, not a session workspace). Ask the GM to /rename this session to something distinct, then work in .clones/<that-name>.   (CLAUDE.md 'Session clones' - 'gm-assistant' is a forbidden clone name)" >&2
      cs_block forbidden-name-unnamed "$clone"   # GUARD_EDIT_OK: feature 168
      exit 2
    fi
    if [ "$(basename "$clone")" = "gm-assistant" ]; then
      echo "BLOCKED: '.clones/gm-assistant' is a FORBIDDEN clone name ('gm-assistant' is the repository, not a session). Work in .clones/<your-session-name>${canon:+ (this session resolves to $canon)}.   (CLAUDE.md 'Session clones' - 'gm-assistant' is a forbidden clone name)" >&2
      cs_block forbidden-name "$clone"   # GUARD_EDIT_OK: feature 168
      exit 2
    fi

    # (1) NAME-ROUTING: a session may only edit in .clones/<its-own-name>. Unresolvable -> skip.
    if [ -n "$canon" ] && [ "$clone" != "$canon" ]; then
      echo "BLOCKED: this session's clone is $canon (resolved from its session name); the edit targets $clone. Two sessions must never share a working tree (the 2026-07-22 collision). Work in $canon - if it does not exist: git clone /gm-assistant $canon && cd $canon && git config user.name \"\$(git -C /gm-assistant config user.name)\" && git config user.email \"\$(git -C /gm-assistant config user.email)\" && scripts/sync-with-main.sh sync-in   (CLAUDE.md 'Session clones' - name-routing guard)" >&2
      cs_block name-routing "$clone"   # GUARD_EDIT_OK: feature 168
      exit 2
    fi

    # (2) CLAIM BACKSTOP: another LIVE session already occupying this clone (only possible via a
    #     concurrent duplicate session name). A dead/previous claimant is ignored, so sequential
    #     reuse of a generic name like "miscellaneous" is fine.
    if [ -n "$sid" ] && [ -d "$MAPDIR" ]; then
      for m in "$MAPDIR"/*; do
        [ -f "$m" ] || continue
        other=$(basename "$m")
        [ "$other" = "$sid" ] && continue
        [ "$(cat "$m" 2>/dev/null)" = "$clone" ] || continue
        if sid_is_live "$other"; then
          echo "BLOCKED: $clone is already occupied by another live session ($other) - two sessions must not share a working tree. Ask the GM to /rename one session distinctly and use its own clone.   (CLAUDE.md 'Session clones' - claim backstop)" >&2
          cs_block live-claim "$clone"   # GUARD_EDIT_OK: feature 168
          exit 2
        fi
      done
    fi

    # (3) claim, then the stale-base check.
    claim
    # BEHIND means "main's tip is missing from this clone's history" - NOT "the two HEADs differ".
    # The equality test this replaces (GM-reported 2026-07-25) deadlocked the normal workflow: the
    # moment a session COMMITS in its clone the tree is clean and the HEADs differ, so every later
    # edit was blocked until it pushed - which broke any multi-commit work unit, spec-kit's
    # per-step commits above all. --is-ancestor lets a clone that is merely AHEAD keep working
    # while still blocking a genuinely stale or diverged one. A non-zero exit covers both the
    # "not an ancestor" case and the "main's tip is not even in this clone's object store" case
    # (a local clone hardlinks objects at clone time; commits main gains afterward are absent
    # until a fetch), and both of those mean stale.
    main_head=$(git -C "$MAIN" rev-parse HEAD 2>/dev/null)
    if [ -n "$main_head" ] && ! git -C "$clone" merge-base --is-ancestor "$main_head" HEAD 2>/dev/null; then
      # GUARD_EDIT_OK: feature 168 - FIXING A GUARD THAT SENDS YOU AT A COMMAND THAT CANNOT HELP.
      #
      # THE MIRROR IS NOT ALWAYS MAIN. `/diagram` only ever fast-forwards from GitHub, so its HEAD
      # normally IS main's tip - but a session that lets a bare `cd /diagram` leak into its next
      # command commits INTO the mirror, and that commit then exists on no branch anywhere else.
      # From that moment this check compares every clean clone against a commit GitHub main does not
      # have, and tells all of them to run `sync-in` - which fetches GitHub, finds nothing new,
      # reports success and changes nothing. The session is blocked from every edit with no route
      # forward, and the advice it was handed amounts to building ON the stray commit, which is the
      # one thing the mirror rule forbids.
      #
      # Measured 2026-08-30: it happened TWICE in one day, both times the bare-`cd` leak CLAUDE.md
      # documents and deliberately leaves unenforced, and the second one blocked a peer session until
      # it worked out from outside what had happened. So ask the mirror whether its HEAD is on GitHub
      # main before believing it; when it is not, name the real problem and say who owns it. Nothing
      # about a genuinely stale clone changes - that refusal is below, untouched.
      if git -C "$MAIN" rev-parse --verify -q origin/main >/dev/null 2>&1 \
         && ! git -C "$MAIN" merge-base --is-ancestor "$main_head" origin/main 2>/dev/null; then
        echo "BLOCKED: the mirror $MAIN is carrying a commit GitHub main does not have ($(git -C "$MAIN" log -1 --format='%h %s' 2>/dev/null)), so this clone cannot be judged against it - and \`sync-in\` will NOT fix it: it fetches GitHub, finds nothing new, and reports success." >&2
        echo "That is a STRAY COMMIT in main's tree, almost always a bare \`cd /diagram\` that leaked into the next command (CLAUDE.md, 'NAME THE TREE IN THE COMMAND'). Main is an integration point, never a workspace, so no session may build on it." >&2
        echo "It belongs to whoever made it. Do NOT reset it unless it is yours - the mirror's working tree may be the only copy. Find that session (ListAgents / SendMessage); the recovery that loses nothing is: format-patch or copy the content into THAT session's clone and commit it there, check \`git -C $MAIN status --porcelain\` for untracked files a reset would destroy, then \`git -C $MAIN reset --hard origin/main\`." >&2
        cs_block stray-mirror-commit "$MAIN"
        exit 2
      fi
      echo "BLOCKED: $clone has a clean tree (a new work unit) but its HEAD is behind main - new work must not build on a stale base. Run: cd $clone && scripts/sync-with-main.sh sync-in   (CLAUDE.md 'Session clones' / sync-in rule)" >&2
      cs_block stale-head "$clone"
      exit 2
    fi
    exit 0
    ;;
  prompt)
    sid=$(field session_id)
    [ -n "$sid" ] || exit 0
    if [ ! -f "$MAPDIR/$sid" ]; then
      # NO CLONE CLAIMED YET - normally this session's FIRST prompt. Say RIGHT HERE whether it can
      # even have a workspace, because the pretool backstop only speaks at the first EDIT, which is
      # far too late: on 2026-08-08 a session did 4.7 minutes of recon, worked out its whole plan,
      # and only then discovered it had no resolvable name - so the GM's /rename was 4.6 minutes of
      # dead wall-clock instead of something that could have overlapped the recon. Announcing it at
      # turn 1 makes the rename concurrent with the analysis rather than a barrier in front of it.
      # ONCE PER SESSION (the marker file): a read-only session must not be nagged every prompt.
      notice="$MAPDIR/$sid.name-notice"
      if [ ! -f "$notice" ]; then
        mkdir -p "$MAPDIR"; : > "$notice"
        canon=$(canonical_clone "$sid" "$(field transcript_path)")
        if [ -z "$canon" ]; then
          echo "clone-sync: this session's name does not resolve (no /rename record in its transcript and no entry for it under $SESSIONS_DIR), so it has NO valid clone name. Read-only work is fine. If you are going to modify this repo, ask the GM to /rename the session NOW - before the recon, not after it."
        elif [ "$(basename "$canon")" = "gm-assistant" ]; then
          echo "clone-sync: this session resolves to the FORBIDDEN '.clones/gm-assistant' (unnamed or auto-derived). Read-only work is fine. If you are going to modify this repo, ask the GM to /rename the session NOW - before the recon, not after it."
        fi
      fi
      exit 0
    fi
    clone=$(cat "$MAPDIR/$sid")
    [ -d "$clone/.git" ] || exit 0

    # RE-TRACK GUARD (2026-08-16): .specify/feature.json is spec-kit's ACTIVE-FEATURE pointer and
    # must stay gitignored. It is per-workspace state, and tracking it is not a cosmetic mistake -
    # common.sh resolves FEATURE_DIR from it at PRIORITY 2, above the SPECIFY_FEATURE env var at
    # priority 3. So a tracked copy merges between concurrent sessions and silently redirects
    # setup-plan.sh / setup-tasks.sh / implement into a PEER's specs/NNN-*/, while CURRENT_BRANCH
    # still reads correctly - measured on features 115/116, where a peer's specify commit repointed
    # it mid-chain and `SPECIFY_FEATURE=115` still resolved FEATURE_DIR to 116.
    # A spec-kit upgrade, a `git add -f`, or a clone made before the ignore can all re-track it,
    # and the failure is SILENT, so it is worth a per-session word. Warn once; the fix is one line.
    if git -C "$clone" ls-files --error-unmatch .specify/feature.json >/dev/null 2>&1; then
      fjnotice="$MAPDIR/$sid.feature-json-notice"
      if [ ! -f "$fjnotice" ]; then
        : > "$fjnotice"
        echo "clone-sync: .specify/feature.json is TRACKED again in $clone - it must stay gitignored. It OUTRANKS SPECIFY_FEATURE when spec-kit resolves FEATURE_DIR, so a peer session's copy silently redirects your spec-kit writes into THEIR specs/NNN-*/. Fix: cd $clone && git rm --cached .specify/feature.json && git commit -m 'chore: untrack spec-kit active-feature pointer'   (CLAUDE.md 'Concurrent sessions')"
      fi
    fi

    # THE MIRROR ADVANCES EVERY TURN, DIRTY CLONE OR NOT (feature 130, FR-030 - GUARD_EDIT_OK: the
    # mirror half of sync-in is unconditional). Mid-task work is sacred, so the CLONE merge is
    # skipped as before; but GitHub main is the integration point now and /diagram is a mirror
    # nobody works in, so refreshing it (and its renders) loses nothing and keeps what the GM
    # browses from lagging GitHub by more than one turn.
    if [ -n "$(git -C "$clone" status --porcelain 2>/dev/null)" ]; then
      if out=$(cd "$clone" && scripts/sync-with-main.sh sync-in --mirror-only 2>&1); then
        echo "clone-sync: $clone has uncommitted work (mid-task) - clone merge skipped; mirror refreshed from GitHub main. Finish and run sync-with-main.sh done"
      else
        echo "clone-sync: $clone has uncommitted work (mid-task) - clone merge skipped; mirror refresh FAILED: $(printf '%s' "$out" | tail -1)"
      fi
      exit 0
    fi
    if out=$(cd "$clone" && scripts/sync-with-main.sh sync-in 2>&1); then
      echo "clone-sync: auto-synced $clone with main (git)"
    else
      echo "clone-sync: auto sync-in FAILED in $clone - resolve before modifying the repo: $(printf '%s' "$out" | tail -2)"
    fi
    exit 0
    ;;
  *)
    echo "clone-sync-hooks: unknown mode '$MODE' (want: prompt | pretool)" >&2
    exit 1
    ;;
esac
