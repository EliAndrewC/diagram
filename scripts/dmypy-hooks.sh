#!/usr/bin/env bash
# dmypy-hooks.sh - stop the mypy daemons that outlive the Claude Code sessions they served
# (GM 2026-08-28; GUARD_EDIT_OK: a new guard, born with its companion test-dmypy-hooks.sh).
#
# WHY. `make quick` type-checks through the mypy daemon (`dmypy run`, Makefile MYPY) so a warm
# re-check costs ~0.15 s instead of up to ~3 s (below). The daemon is started by the first quick in a clone
# and then simply stays: nothing in mypy stops it, and nothing here did either. Measured 2026-08-28
# in the claude-diagram container: five daemons, one per session clone, 380-600 MB RSS EACH
# (~2.3 GB), one of them for a session that had ended half an hour earlier. The RSS is the daemon's
# design, not a leak - it keeps every module's typed tree (163 project files plus typeshed and the
# third-party stubs) in memory so a fine-grained re-check touches only what changed; a one-shot
# `python3 -m mypy` peaks at the same ~440 MB and then exits. There is no mypy flag that caps it.
#
# WHAT THIS DOES, two ways, so a miss on one is caught by the other:
#   session-end  - the SessionEnd hook (.claude/settings.json): stop the daemon of THIS session's
#                  clone (the claim in .clones/.session-clones/<session_id>, the same record the
#                  clone-sync hook keeps), then sweep.
#   sweep        - stop every daemon whose clone no LIVE session owns; run by `make quick` as a
#                  side effect (never by `make done`: an error stopping something unrelated to the
#                  work must not block a merge - the GM's own reasoning). Always exits 0 and
#                  prints one line per daemon it stops, nothing when there is nothing to do.
#
# A clone is OWNED when a live session claims it (.session-clones/<sid> -> clone, and the session's
# ~/.claude/sessions/<pid>.json names a pid whose cmdline says claude) OR a live session's name
# kebab-cases to it (the naming rule of CLAUDE.md 'Session clones' - a session that has not edited
# yet has no claim but still owns its clone). A daemon in main's own tree is always stopped: main
# is never a workspace. Stopping is `dmypy stop` through the daemon's own status file, then TERM,
# then KILL - a fake daemon (the test's) falls through to the signals.
#
# WHAT THE RAM BUYS (measured 2026-08-28): on a comment-only edit the daemon answers in 0.13 s and a
# warm one-shot mypy in 0.21-0.31 s, but on an INTERFACE change to a central module (a function added
# to settlement/__init__.py) it is 0.15 s against 2.9 s - one-shot re-checks every dependent, the
# daemon's fine-grained graph does not. ~2.7 s per engine-editing quick; the daemon stays.
#
# DECLINED: `dmypy run --timeout N` (the daemon exits after N idle seconds). A cold daemon start is
# ~12 s, so a timeout would charge the first quick after every break 12 s. A daemon that is owned stays
# until its session ends; that is the trade the GM asked for.
#
# Seams (DMYPY_MAIN, DMYPY_SESSIONS_DIR) are honored only inside a fixture (DMYPY_FIXTURE=1, outside
# this repository's tree), like the idle-tests hook's - a seam a session could set is an override.
set -uo pipefail
MODE="${1:-sweep}"
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
OWN_ROOT=$(cd "$HERE/.." && pwd)
case "$OWN_ROOT" in */.clones/*) DEFAULT_MAIN=${OWN_ROOT%%/.clones/*} ;; *) DEFAULT_MAIN=$OWN_ROOT ;; esac
if [ "${DMYPY_FIXTURE:-}" = "1" ] && [ -n "${DMYPY_MAIN:-}" ] && [ "${DMYPY_MAIN#"$OWN_ROOT"}" = "$DMYPY_MAIN" ]; then
  MAIN=$DMYPY_MAIN; SESSIONS_DIR=${DMYPY_SESSIONS_DIR:-${HOME:-/home/agent}/.claude/sessions}
else
  MAIN=$DEFAULT_MAIN; SESSIONS_DIR=${HOME:-/home/agent}/.claude/sessions
fi
MAPDIR=$MAIN/.clones/.session-clones
SKILL=.claude/skills/diagram
INPUT=""
case "$MODE" in session-end) INPUT=$(cat 2>/dev/null || true) ;; esac

field() { printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    print(json.load(sys.stdin).get('$1', '') or '')
except Exception:
    print('')"; }

pid_alive_as() { # pid_alive_as <pid> <word> - a live process whose cmdline mentions <word>
  local pid=$1
  case $pid in ''|*[!0-9]*) return 1 ;; esac
  [ -r "/proc/$pid/cmdline" ] || return 1
  tr '\0' ' ' < "/proc/$pid/cmdline" | grep -q -- "$2"
}

owned_clones() { # every clone a LIVE session owns, one absolute path per line
  MAIN="$MAIN" MAPDIR="$MAPDIR" SDIR="$SESSIONS_DIR" python3 - <<'PY'
import glob, json, os, re
main, mapdir, sdir = os.environ["MAIN"], os.environ["MAPDIR"], os.environ["SDIR"]
live = {}  # session_id -> name, for sessions whose pid is a live claude
for f in glob.glob(os.path.join(sdir, "*.json")):
    pid = os.path.splitext(os.path.basename(f))[0]
    try:
        cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ")
        d = json.load(open(f))
    except Exception:
        continue
    if b"claude" not in cmd:
        continue
    for k in ("id", "sessionId", "session_id"):
        if d.get(k):
            live[d[k]] = d.get("name") or ""
owned = set()
for sid, name in live.items():
    claim = os.path.join(mapdir, sid)
    if os.path.isfile(claim):
        c = open(claim).read().strip()
        if c:
            owned.add(os.path.normpath(c))
    kebab = re.sub(r"\s+", "-", re.sub(r"[^a-z0-9\s-]", "", name.lower()).strip())
    if kebab:
        owned.add(os.path.join(main, ".clones", kebab))
for c in sorted(owned):
    print(c)
PY
}

stop_daemon() { # stop_daemon <status-file> <why> - stop the daemon a .dmypy.json names; say so
  local sf=$1 why=$2 pid rss dir
  dir=$(dirname "$sf")
  pid=$(python3 -c "import json;print(json.load(open('$sf')).get('pid',''))" 2>/dev/null)
  if ! pid_alive_as "$pid" dmypy; then rm -f "$sf"; return 0; fi   # a stale status file, no daemon
  rss=$(awk '/VmRSS/{printf "%d", $2/1024}' "/proc/$pid/status" 2>/dev/null)
  ( cd "$dir" && timeout 10 python3 -m mypy.dmypy --status-file "$sf" stop ) >/dev/null 2>&1 || true
  if pid_alive_as "$pid" dmypy; then kill -TERM "$pid" 2>/dev/null; sleep 0.3; fi
  if pid_alive_as "$pid" dmypy; then kill -KILL "$pid" 2>/dev/null; fi
  rm -f "$sf"
  echo "dmypy: stopped the daemon for ${dir#"$MAIN"/} (pid $pid, ${rss:-?} MB) - $why"
}

do_sweep() {
  local owned sf clone
  owned=$(owned_clones)
  for sf in "$MAIN"/.clones/*/"$SKILL"/.dmypy.json "$MAIN/$SKILL/.dmypy.json"; do
    [ -f "$sf" ] || continue
    clone=${sf%/"$SKILL"/.dmypy.json}
    if [ "$clone" != "$MAIN" ] && printf '%s\n' "$owned" | grep -qxF -- "$clone"; then continue; fi
    stop_daemon "$sf" "$([ "$clone" = "$MAIN" ] && echo 'main is never a workspace' || echo 'no live session owns this clone')"
  done
}

do_session_end() {
  local sid clone sf
  sid=$(field session_id)
  if [ -n "$sid" ] && [ -f "$MAPDIR/$sid" ]; then
    clone=$(cat "$MAPDIR/$sid"); sf="$clone/$SKILL/.dmypy.json"
    [ -f "$sf" ] && stop_daemon "$sf" "its session ended"
  fi
  do_sweep
}

case "$MODE" in
  sweep) do_sweep ;;
  session-end) do_session_end ;;
  *) exit 0 ;;
esac
exit 0
