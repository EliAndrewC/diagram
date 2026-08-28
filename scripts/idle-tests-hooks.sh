#!/usr/bin/env bash
# idle-tests-hooks.sh - an idle session runs the expensive tests in the background (feature 136).
# (GUARD_EDIT_OK: a NEW guard, feature 136 - the GM's request, verbatim in specs/136-idle-background-tests/gm-request.md)
#
# THE GM (2026-08-27): "if the session has been idle for at least a certain amount of time where
# you have finished the previous round of work, and I have not given you anything new to do, then
# that might be a good time to kick off in the background This kind of test. because then a test
# which is relatively expensive in terms of me having to wait for it time becomes very cheap
# because it is largely going to run unattended. However, because the host ... is a laptop ... I
# would not want to open my laptop and then suddenly have every session fire off the expensive
# tests ... if we are able to detect when the laptop has resumed after a long suspend ... we wait
# an additional hour ... between one and two hours ... based on the hash of the session name ...
# that solves the thundering herd problem".
#
# Modes, wired from .claude/settings.json (the decisions D1-D8 are in specs/136-.../spec.md):
#   stop    (Stop hook)             ARM: write <clone>/.git/idle-tests.json and start a detached
#                                   timer; a no-op while one is armed and alive.
#   prompt  (UserPromptSubmit hook) DISARM: delete the state (the timer sees it gone and exits),
#                                   and print the last idle verdict once, so the session acts on it.
#   timer <clone> <session> [sid]   the detached wait: 60 + (hash(session) mod 61) minutes of AWAKE
#                                   time (a wall-clock jump past the awake count = a suspend, and
#                                   the wait RESTARTS in full); then the host-wide lock (one runner
#                                   at a time; a loser defers 5-15 min and retries, the arming
#                                   lapsing 6 h after it was set); never while a `make` runs in the
#                                   clone; then `make idle-tests` in the clone, the verdict recorded
#                                   in dev/idle-log/<utc>-<session>.json.
#   stagger <session>               print the wait in minutes for a name (the test reads the band).
#
# NEVER IN MAIN: a cwd whose git root is not <main>/.clones/<name> arms nothing - main is not a
# workspace. NEVER RE-ARMS ITSELF: only a Stop arms, so one idle = at most one run. NEVER THE
# MERGE'S BUSINESS: the state lives in .git/, the run records under its own target name, the timer
# waits for any make the session left running, and a PROMPT ABORTS a run in progress (D9) - nothing
# of the session's ever waits on an idle run.
#
# SEAMS ONLY IN A FIXTURE: the IDLE_* overrides are honored only with IDLE_FIXTURE=1 AND a git root
# outside this repository's own tree (the rule test-sync-with-main.sh proves for the ritual); set
# outside a fixture they are ignored and said so. Companion: test-idle-tests-hooks.sh.
set -u
MODE=${1:-}
HERE=$(cd "$(dirname "$0")" && pwd)
OWN_ROOT=$(cd "$HERE/.." && pwd)
INPUT=""
case "$MODE" in stop|prompt) INPUT=$(cat 2>/dev/null || true) ;; esac

field() { # field <dotted.path> - a string field of the hook's stdin JSON
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

# ---- configuration (D2, D4), and the seams
DEF_TICK=60 DEF_WAIT_MIN=60 DEF_WAIT_SPAN=60 DEF_SUSPEND_S=300 DEF_DEFER_MIN=5 DEF_DEFER_SPAN=10 DEF_GIVE_UP_S=21600
seams_ok() { # exit 0 iff the seams may be honored here: a fixture, outside this repository's tree
  [ "${IDLE_FIXTURE:-}" = "1" ] || return 1
  case "${IDLE_ROOT:-$PWD}" in "$OWN_ROOT"|"$OWN_ROOT"/*) return 1 ;; esac
  return 0
}
configure() {
  if seams_ok; then
    TICK=${IDLE_TICK:-$DEF_TICK}; WAIT_MIN=${IDLE_WAIT_MIN:-$DEF_WAIT_MIN}; WAIT_SPAN=${IDLE_WAIT_SPAN:-$DEF_WAIT_SPAN}
    SUSPEND_S=${IDLE_SUSPEND_S:-$DEF_SUSPEND_S}; DEFER_MIN=${IDLE_DEFER_MIN:-$DEF_DEFER_MIN}; DEFER_SPAN=${IDLE_DEFER_SPAN:-$DEF_DEFER_SPAN}
    GIVE_UP_S=${IDLE_GIVE_UP_S:-$DEF_GIVE_UP_S}; CLOCK=${IDLE_CLOCK:-date +%s}; RUN=${IDLE_RUN:-}
    IDLE_HOME_DIR=${IDLE_HOME:-${HOME:-/home/agent}/.claude}; SESSIONS_DIR=${IDLE_SESSIONS_DIR:-${HOME:-/home/agent}/.claude/sessions}
    WAIT_S_OVERRIDE=${IDLE_WAIT_S:-}; DEFER_S_OVERRIDE=${IDLE_DEFER_S:-}; BUSY_CMD=${IDLE_BUSY_CMD:-}
  else
    if env | grep -q '^IDLE_[A-Z]' ; then echo "idle-tests: IDLE_* seams are honored only inside a fixture (IDLE_FIXTURE=1, outside $OWN_ROOT) - ignored" >&2; fi
    TICK=$DEF_TICK; WAIT_MIN=$DEF_WAIT_MIN; WAIT_SPAN=$DEF_WAIT_SPAN; SUSPEND_S=$DEF_SUSPEND_S; DEFER_MIN=$DEF_DEFER_MIN; DEFER_SPAN=$DEF_DEFER_SPAN
    GIVE_UP_S=$DEF_GIVE_UP_S; CLOCK="date +%s"; RUN=""; IDLE_HOME_DIR=${HOME:-/home/agent}/.claude; SESSIONS_DIR=${HOME:-/home/agent}/.claude/sessions
    WAIT_S_OVERRIDE=""; DEFER_S_OVERRIDE=""; BUSY_CMD=""
  fi
}
now() { $CLOCK; }
hash_of() { printf '%s' "$1" | cksum | awk '{print $1}'; }
stagger_min() { echo $(( WAIT_MIN + $(hash_of "$1") % (WAIT_SPAN + 1) )); }
defer_min() { echo $(( DEFER_MIN + $(hash_of "$1") % (DEFER_SPAN + 1) )); }

# ---- where am I: the clone, its main, the session name
locate() { # sets CLONE MAIN SESSION, or returns 1 when the cwd is not a session clone
  local cwd top
  cwd=$(field cwd); cwd=${cwd:-$PWD}
  top=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null) || return 1
  case "$top" in */.clones/*) ;; *) return 1 ;; esac
  CLONE=$top; MAIN=${top%%/.clones/*}; SESSION=$(basename "$top")
  return 0
}
state_of() { python3 -c "import json;print(json.load(open('$1')).get('$2','') or '')" 2>/dev/null; }
sid_is_live() { # a live process backs this session_id (the sessions-json FILENAME is its PID)
  local sid="$1" pid
  [ -n "$sid" ] || return 0  # no id known: assume live (a hand-driven hook)
  pid=$(SID="$sid" SDIR="$SESSIONS_DIR" python3 -c "
import glob, json, os
sid, sdir = os.environ['SID'], os.environ['SDIR']
for f in sorted(glob.glob(os.path.join(sdir, '*.json'))):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if d.get('sessionId') == sid or d.get('session_id') == sid:
        print(os.path.basename(f).split('.')[0]); break" 2>/dev/null)
  [ -n "$pid" ] && [ -d "/proc/$pid" ]
}
make_running_in() { # exit 0 iff a make process has its cwd inside the clone (a gate or sweep the session left running)
  local c="$1" p cwd
  if [ -n "$BUSY_CMD" ]; then $BUSY_CMD "$c"; return $?; fi
  for p in $(pgrep -x make 2>/dev/null); do
    cwd=$(readlink "/proc/$p/cwd" 2>/dev/null) || continue
    case "$cwd" in "$c"|"$c"/*) return 0 ;; esac
  done
  return 1
}

# ---- the modes
do_stop() {
  configure; locate || exit 0  # main, or no git: nothing to arm
  local sf sid pid
  sf="$CLONE/.git/idle-tests.json"; sid=$(field session_id)
  if [ -f "$sf" ]; then
    pid=$(state_of "$sf" timer_pid)
    if [ -n "$pid" ] && [ -d "/proc/$pid" ]; then exit 0; fi  # armed and alive: a no-op
  fi
  python3 - "$sf" "$SESSION" "$sid" "$(now)" "$(stagger_min "$SESSION")" <<'PY'
import json, sys
sf, session, sid, at, wait = sys.argv[1:]
json.dump({"session": session, "session_id": sid, "armed_at": int(at), "wait_min": int(wait), "timer_pid": None}, open(sf, "w"))
PY
  setsid nohup env IDLE_ROOT="${IDLE_ROOT:-$CLONE}" "$0" timer "$CLONE" "$SESSION" "$sid" > "$CLONE/.git/idle-tests.log" 2>&1 < /dev/null &
  pid=$!
  python3 - "$sf" "$pid" <<'PY'
import json, sys
sf, pid = sys.argv[1], int(sys.argv[2])
d = json.load(open(sf)); d["timer_pid"] = pid; json.dump(d, open(sf, "w"))
PY
  exit 0
}

do_prompt() {
  configure; locate || exit 0
  local sf pid seen latest
  sf="$CLONE/.git/idle-tests.json"
  if [ -f "$sf" ]; then
    pid=$(state_of "$sf" timer_pid)
    rm -f "$sf"
    if [ -f "$CLONE/.git/idle-tests.running" ]; then  # a run in progress is ABORTED (D9): nothing of the session's ever waits on it
      kill -TERM -- "-$pid" 2>/dev/null; kill -TERM "$pid" 2>/dev/null; sleep 0.2; kill -KILL -- "-$pid" 2>/dev/null
      rm -f "$CLONE/.git/idle-tests.running"
      python3 - "$CLONE/.claude/skills/diagram/dev/idle-log/$(date -u +%Y%m%dT%H%M%SZ)-$SESSION.json" "$SESSION" "$(git -C "$CLONE" rev-parse --short HEAD 2>/dev/null)" <<'PY'
import json, os, sys
rec, session, commit = sys.argv[1:]
os.makedirs(os.path.dirname(rec), exist_ok=True)
json.dump({"utc": os.path.basename(rec).split("-")[0], "session": session, "commit": commit, "target": "make idle-tests", "rc": -1, "aborted": "on-prompt", "wall_s": 0, "suspends": 0, "deferrals": 0, "failures": [], "log": ""}, open(rec, "w"), indent=1)
PY
    elif [ -n "$pid" ] && [ -d "/proc/$pid" ]; then kill "$pid" 2>/dev/null; fi
  fi
  # the last verdict, once: the record newer than the one already shown
  seen="$CLONE/.git/idle-tests.seen"
  latest=$(ls -t "$CLONE"/.claude/skills/diagram/dev/idle-log/*-"$SESSION".json 2>/dev/null | head -1)
  if [ -n "$latest" ] && [ "$(cat "$seen" 2>/dev/null)" != "$latest" ]; then
    printf '%s\n' "$latest" > "$seen"
    python3 - "$latest" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
tail = "aborted on your prompt (D9) - nothing waited on it" if d.get("aborted") else ("clean" if d.get("rc") == 0 else f"FAILED (rc {d.get('rc')}): {', '.join(d.get('failures') or [])[:200] or 'see ' + str(d.get('log', ''))}")
print(f"idle-tests: ran {d.get('utc')} in {d.get('wall_s')}s on {d.get('commit')} ({d.get('target')}; suspends {d.get('suspends')}, deferrals {d.get('deferrals')}): {tail}")
PY
  fi
  exit 0
}

do_timer() {
  CLONE=$2; SESSION=$3; SID=${4:-}
  IDLE_ROOT=${IDLE_ROOT:-$CLONE}; export IDLE_ROOT
  configure
  local sf armed wait_s last t suspends=0 deferrals=0 defer_s lock rc t0 t1 rec utc commit log target running tick_ms
  sf="$CLONE/.git/idle-tests.json"; running="$CLONE/.git/idle-tests.running"
  armed=$(state_of "$sf" armed_at); [ -n "$armed" ] || exit 0
  wait_s=${WAIT_S_OVERRIDE:-$(( $(stagger_min "$SESSION") * 60 ))}
  defer_s=${DEFER_S_OVERRIDE:-$(( $(defer_min "$SESSION") * 60 ))}
  alive() { # the arming still stands, the session still exists, the arming has not lapsed
    [ -f "$sf" ] || return 1
    [ "$(state_of "$sf" armed_at)" = "$armed" ] || return 1
    sid_is_live "$SID" || return 1
    [ $(( $(now) - armed )) -lt "$GIVE_UP_S" ] || return 1
    return 0
  }
  tick_ms=$(python3 -c "print(max(1, int(float('$TICK') * 1000)))")
  wait_awake() { # wait $1 seconds of AWAKE time; a wall jump past the ticks restarts the count (D2, D3)
    local need_ms=$(( $1 * 1000 )) awake_ms=0 drift_ms
    last=$(now)
    while [ "$awake_ms" -lt "$need_ms" ]; do
      sleep "$TICK"; alive || exit 0
      t=$(now); drift_ms=$(( (t - last) * 1000 - tick_ms )); last=$t
      if [ "$drift_ms" -gt $(( SUSPEND_S * 1000 )) ]; then awake_ms=0; suspends=$((suspends + 1)); echo "suspend detected (wall jumped $(( drift_ms / 1000 ))s past the ticks): the wait restarts"; continue; fi
      awake_ms=$(( awake_ms + tick_ms ))
    done
  }
  wait_awake "$wait_s"
  lock="$IDLE_HOME_DIR/idle-tests.lock"; mkdir -p "$IDLE_HOME_DIR"
  exec 9>"$lock"
  while :; do
    if ! flock -n 9; then deferrals=$((deferrals + 1)); echo "another session's idle run holds the lock: deferring ${defer_s}s"; wait_awake "$defer_s"; continue; fi
    if make_running_in "$CLONE"; then deferrals=$((deferrals + 1)); echo "a make is running in this clone: deferring ${defer_s}s"; flock -u 9; wait_awake "$defer_s"; continue; fi
    break
  done
  alive || exit 0
  target=${RUN:-make idle-tests}
  log="$CLONE/.git/idle-tests.run.log"
  utc=$(date -u +%Y%m%dT%H%M%SZ); commit=$(git -C "$CLONE" rev-parse --short HEAD 2>/dev/null)
  echo "$$" > "$running"
  t0=$(now)
  ( cd "$CLONE/.claude/skills/diagram" 2>/dev/null || cd "$CLONE"; $target ) > "$log" 2>&1; rc=$?
  t1=$(now)
  rm -f "$running"
  mkdir -p "$CLONE/.claude/skills/diagram/dev/idle-log"
  rec="$CLONE/.claude/skills/diagram/dev/idle-log/$utc-$SESSION.json"
  python3 - "$rec" "$utc" "$SESSION" "$commit" "$target" "$rc" "$((t1 - t0))" "$suspends" "$deferrals" "$log" <<'PY'
import json, re, sys
rec, utc, session, commit, target, rc, wall, sus, dfr, log = sys.argv[1:]
fails = []
try:
    for line in open(log, errors="replace"):
        m = re.match(r"\s*FAIL\S*\s+(\S+)", line)
        if m and m.group(1) not in fails:
            fails.append(m.group(1))
        m2 = re.search(r"tripwire seed\s+(\d+): (?!ok|expected)(.+)", line)
        if m2:
            fails.append(f"seed{m2.group(1)}: {m2.group(2).strip()[:80]}")
except Exception:
    pass
json.dump({"utc": utc, "session": session, "commit": commit, "target": target, "rc": int(rc), "wall_s": int(wall), "suspends": int(sus), "deferrals": int(dfr), "failures": fails, "log": log}, open(rec, "w"), indent=1)
PY
  rm -f "$sf"  # the arming is consumed: only a Stop arms again (D6)
  echo "idle-tests: recorded $rec (rc $rc)"
  exit 0
}

case "$MODE" in
  stop) do_stop ;;
  prompt) do_prompt ;;
  timer) do_timer "$@" ;;
  stagger) configure; stagger_min "${2:-}" ;;
  *) echo "usage: idle-tests-hooks.sh stop|prompt|timer <clone> <session> [sid]|stagger <session>" >&2; exit 1 ;;
esac
