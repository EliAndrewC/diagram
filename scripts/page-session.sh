#!/bin/bash
# page-session.sh <brief> [name] [model] - one research page's work in a FRESH headless session (feature 250 D7).
#
# WHY. On feature 250's measured slice (research R1) the main session was 87% of every token spent: 92
# turns at a mean context of 202,000, because everything that enters a session - a file, a report, a
# tool result - is paid for again on every later turn, and one session carried the whole slice. A
# session that does ONE page and ends never grows that far. The brief, not the context, carries the
# state: what the page owes, the procedure, and where to write what it found.
#
# WHAT IT DOES. Starts `claude -p` in this clone, named like this clone (so the clone-sync hooks route it
# here), with the project's appended system prompt (the review agents' standing authorization, as the
# `claude()` wrapper in ~/.bashrc adds it), a session id chosen here so its transcript is known before it
# starts, and DETACHED, because a long run under a tool's background mode can be killed. It prints the
# id, the transcript and the log directory, and returns at once; `<log>/result.json` is written when the
# session ends.
#
# The child commits in the clone and does NOT push: the brief says so, and a session that started work
# on a page is not the one that decides the feature is done. Do not edit the clone while it runs.
set -uo pipefail
BRIEF=${1:-}; ROOT=$(git rev-parse --show-toplevel)
NAME=${2:-$(basename "$ROOT")}; MODEL=${3:-}
[ -n "$BRIEF" ] && [ -f "$BRIEF" ] || { echo "page-session: BRIEF=<file> is required and must exist (got '$BRIEF')" >&2; exit 2; }
BRIEF=$(realpath "$BRIEF")
command -v claude >/dev/null || { echo "page-session: no claude on PATH" >&2; exit 2; }
SID=$(python3 -c 'import uuid; print(uuid.uuid4())')
LOG="$ROOT/.git/page-sessions/$SID"; mkdir -p "$LOG"
ASP="$ROOT/container-scripts/append-system-prompt.md"
PROMPT="You are a fresh session started to do the work ONE brief describes. Read $BRIEF first, and do what it says, end to end and unattended. Commit in this clone as you finish each part; never run the stop-work push. When the brief's work is done, or it tells you to stop, write the one-paragraph summary it asks for and stop."
EXTRA=(); [ -r "$ASP" ] && EXTRA+=(--append-system-prompt "$(cat "$ASP")"); [ -n "$MODEL" ] && EXTRA+=(--model "$MODEL")
# Started through Popen with close_fds and a new session, not `setsid nohup ... &`: the shell form hands the
# child every descriptor the caller holds open, and a caller reading this script through a pipe then waits
# for the CHILD to end - measured on the first run (feature 250 T18), which held its `make` for the session's
# whole length.
python3 - "$ROOT" "$LOG" "$PROMPT" "$NAME" "$SID" "${EXTRA[@]}" <<'PY'
import subprocess, sys
root, log, prompt, name, sid, *extra = sys.argv[1:]
with open(f"{log}/result.json", "w") as out, open(f"{log}/stderr.txt", "w") as err:
    subprocess.Popen(["claude", "-p", prompt, "-n", name, "--session-id", sid, "--permission-mode", "bypassPermissions",
                      *extra, "--output-format", "json"], cwd=root, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                     start_new_session=True, close_fds=True)
PY
MANGLED=$(printf '%s' "$ROOT" | sed 's#[/.]#-#g')
printf 'page-session: started %s\n  session:    %s\n  transcript: %s\n  log:        %s  (result.json is written when it ends)\n' \
  "$NAME" "$SID" "$HOME/.claude/projects/$MANGLED/$SID.jsonl" "$LOG"
