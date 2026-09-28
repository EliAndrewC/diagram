#!/bin/bash
# page-session.sh "<brief> [<brief> ...]" [name] [model] - a research page's work in FRESH headless sessions (feature 250 D7).
#
# WHY. On feature 250's measured slice (research R1) the main session was 87% of every token spent: 92
# turns at a mean context of 202,000, because everything that enters a session - a file, a report, a
# tool result - is paid for again on every later turn, and one session carried the whole slice. A
# session that does ONE page and ends never grows that far; the first page session then showed the
# applying turns at the END of a session that had read every source were a third of it (research R2), so
# a page is now two briefs - write, then check-and-apply - run one after another, each in a fresh session.
# The briefs and the handoff between them, not the context, carry the state.
#
# WHAT IT DOES. Starts `claude -p` in this clone once per brief, in order, each named like this clone (so the
# clone-sync hooks route it here), with the project's appended system prompt (the review agents' standing
# authorization, as the `claude()` wrapper in ~/.bashrc adds it, then the slim page-session rules), and a session id chosen here so every
# transcript is known before it starts. The runner is DETACHED and this returns at once, printing each id,
# transcript and log directory; `<log>/result.json` is written when that session ends, and the next begins.
#
# The sessions commit in the clone and do NOT push. Do not edit the clone while they run.
#
# DETACHED THROUGH Popen(close_fds, start_new_session), not `setsid nohup ... &`: the shell form hands the
# child every descriptor the caller holds open, and a caller reading this script through a pipe then waits
# for the CHILD to end - measured on the first run (feature 250 T18), which held its `make` for the whole
# session.
set -uo pipefail
ROOT=$(git rev-parse --show-toplevel)
BRIEFS=${1:-}; NAME=${2:-$(basename "$ROOT")}; MODEL=${3:-}
[ -n "$BRIEFS" ] || { echo "page-session: BRIEF=<file> (or several, space-separated, run one after another) is required" >&2; exit 2; }
for b in $BRIEFS; do f=${b#then:}; case $f in resume:*) f=${f#resume:*:};; esac; [ -f "$f" ] || { echo "page-session: no brief or step at $f" >&2; exit 2; }; done
command -v claude >/dev/null || { echo "page-session: no claude on PATH" >&2; exit 2; }
# The appended system prompt - the standing authorization, then the slim rules file in place of the root CLAUDE.md
# (feature 274 D6) - is added by the runner's floor_flags, where its test reads it.
EXTRA=(); [ -n "$MODEL" ] && EXTRA+=(--model "$MODEL")
MANGLED=$(printf '%s' "$ROOT" | sed 's#[/.]#-#g')
# shellcheck disable=SC2086 # BRIEFS is a space-separated list on purpose
exec python3 "$ROOT/scripts/_page_session_runner.py" "$ROOT" "$NAME" "$HOME/.claude/projects/$MANGLED" "${EXTRA[@]}" -- $BRIEFS
