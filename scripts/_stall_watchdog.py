#!/usr/bin/env python3
"""The stall watchdog's one pass (feature 295 item 4): every live session judged from outside it.

    _stall_watchdog.py pass     judge every live session once, act, append each action to the log and print it

WHY. A session can stop with its work unfinished and nothing inside it will notice: R12's headless check session sat
two and a half hours after its re-checks returned (2026-09-30), and the in-session hourly `CronCreate` check added that
day lives only as long as its session. So this runs OUTSIDE every session - a loop `stall-watchdog-hooks.sh` keeps
alive, one instance on the host - and on each pass looks at every live session in Claude Code's own registry.

WHAT IS A STALL (spec FR-005a, plan D5). All of: silent an hour or more (the newest write to its transcript or any of
its subagents'); not waiting on the GM (registry status `waiting`, or a pending `AskUserQuestion`); unfinished work in
its clone (uncommitted changes, commits not on `origin/main`, or a live make - the mirror `/diagram` is never a
workspace and never counts); and not one of a page-session queue's own sessions while that queue is in its usage-limit
retry wait - which holds only while the queue's runner lives and its retry line is younger than the wait it states
(the 292 watcher read such a wait as a stall; plan review round 1 found three stale retry lines that must exempt nothing).

WHAT IT DOES (the GM, 2026-09-30: "Tab title + bell"; "Nudge if prompt empty"; plan D6). The stalled session's tab is
retitled `⚠ STALLED <idle> - <name>` and the bell rung (once per stall); in the session's OWN pane, when the input line is
empty, one nudge is typed, once per stall. A session with no pane of its own is marked on its host's tab - the session
that dispatched it (`L7R_DISPATCHER`), the one that parked it (a `bg` job), or an interactive session in the same clone -
and never nudged: the GM approved typing into a stalled session's own pane only. Its log line carries the command that
resumes it. The session's next hook rewrites its own title, so the mark clears itself when the session moves.

Every path and the tmux binary come from the environment when set, so the suite drives a pass against fixtures.
"""

from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
#: the GM's threshold (request item 4: "a session idle for over an hour with unfinished work")
STALL_AFTER = int(os.environ.get("STALL_AFTER", 60 * 60))
#: the runner resumes a minute or so after the wait it logged; five minutes of slack covers that and no more
RETRY_SLACK = 5 * 60
_RULE = re.compile(r"^\s*─{10,}")
_EMPTY_INPUT = re.compile(r"\s*❯\s*")
_RETRY = re.compile(r"^failed (\S+) .* - waiting (\d+) min")


def _env(name: str, default: str) -> str:
    return os.environ.get(name) or default


def sessions_dir() -> str:
    return _env("STALL_SESSIONS_DIR", os.path.expanduser("~/.claude/sessions"))


def projects_dir() -> str:
    return _env("STALL_PROJECTS_DIR", os.path.expanduser("~/.claude/projects"))


def state_dir() -> str:
    return _env("STALL_STATE_DIR", os.path.expanduser("~/.claude/stall-watchdog"))


def clones_map() -> str:
    return _env("STALL_CLONES_MAP", "/diagram/.clones/.session-clones")


def mirror() -> str:
    return _env("STALL_MIRROR", "/diagram")


def proc_dir() -> str:
    return _env("STALL_PROC", "/proc")


def alive(pid: object) -> bool:
    try:
        os.kill(int(str(pid)), 0)
    except (OSError, ValueError):
        return False
    return True


def live_sessions() -> list[dict]:
    """Every registry entry whose process lives - stale files of dead pids stay behind and are skipped."""
    out = []
    for f in sorted(glob.glob(os.path.join(sessions_dir(), "*.json"))):
        try:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        if isinstance(d, dict) and d.get("sessionId") and alive(d.get("pid")):
            out.append(d)
    return out


def transcripts(sid: str) -> list[str]:
    root = projects_dir()
    return glob.glob(os.path.join(root, "*", f"{sid}.jsonl")) + glob.glob(os.path.join(root, "*", sid, "subagents", "*.jsonl"))


def last_activity(sid: str) -> float | None:
    times = [os.path.getmtime(p) for p in transcripts(sid) if os.path.exists(p)]
    return max(times) if times else None


def asking_gm(transcript: str) -> bool:
    """Is the transcript's last record an `AskUserQuestion` call still waiting for its answer?"""
    try:
        with open(transcript, "rb") as fh:
            fh.seek(max(0, os.path.getsize(transcript) - 262_144))
            tail = fh.read().decode("utf-8", errors="replace").splitlines()
    except OSError:
        return False
    for line in reversed(tail):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        msg = rec.get("message") if isinstance(rec, dict) else None
        if not isinstance(msg, dict) or rec.get("type") not in ("assistant", "user"):
            continue
        content = msg.get("content")
        if rec["type"] == "user":
            return False
        return isinstance(content, list) and any(
            isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "AskUserQuestion" for c in content)
    return False


def _git(clone: str, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", clone, *args], capture_output=True, text=True, timeout=30, check=False).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def clone_of(entry: dict) -> str:
    """The working tree the session works in: its claim in the session-clone map, else its cwd's - never the mirror."""
    clone = ""
    try:
        with open(os.path.join(clones_map(), entry["sessionId"]), encoding="utf-8") as fh:
            clone = fh.read().strip()
    except OSError:
        pass
    clone = clone or _git(str(entry.get("cwd") or "/"), "rev-parse", "--show-toplevel")
    return "" if not clone or os.path.realpath(clone) == os.path.realpath(mirror()) else clone


def unfinished(clone: str) -> str:
    """What is unfinished in the clone, in words, or "" when nothing is."""
    what = []
    if _git(clone, "status", "--porcelain"):
        what.append("uncommitted changes")
    # LANDED is asked of the MIRROR, which fast-forwards from GitHub main: a clone's own `origin/main` is only as fresh as
    # its last fetch, and a dry run on 2026-09-30 read a synced-and-landed clone as "147 commits not on main" through it.
    # A HEAD the mirror does not hold, or holds off main, is unlanded.
    head = _git(clone, "rev-parse", "HEAD")
    if head and subprocess.run(["git", "-C", mirror(), "merge-base", "--is-ancestor", head, "main"],
                               capture_output=True, check=False).returncode != 0:
        what.append("commits not on main")
    live = subprocess.run([os.path.join(HERE, "finished-run-hooks.sh"), "live", clone], capture_output=True, text=True, check=False).stdout
    if live.strip():
        what.append("a live make")
    return ", ".join(what)


def _cmdlines() -> list[list[str]]:
    out = []
    for d in glob.glob(os.path.join(proc_dir(), "[0-9]*")):
        try:
            with open(os.path.join(d, "cmdline"), "rb") as fh:
                out.append([a.decode(errors="replace") for a in fh.read().split(b"\0")])
        except OSError:
            continue
    return out


def in_retry_wait(clone: str, sid: str, now: float) -> bool:
    """Is `sid` a session of a page-session queue whose live runner is in a current usage-limit retry wait?"""
    for log in glob.glob(os.path.join(clone, ".git", "page-sessions", "run-*.log")):
        try:
            with open(log, encoding="utf-8", errors="replace") as fh:
                lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
        except OSError:
            continue
        if not lines or f"started {sid}" not in "\n".join(lines):
            continue
        m = _RETRY.match(lines[-1])
        if not m or now - os.path.getmtime(log) > int(m.group(2)) * 60 + RETRY_SLACK:
            continue
        if any(any("_page_session_runner.py" in a for a in argv) and "--work" in argv and log in argv for argv in _cmdlines()):
            return True
    return False


def _environ(pid: object) -> dict[str, str]:
    try:
        with open(os.path.join(proc_dir(), str(pid), "environ"), "rb") as fh:
            pairs = [p.decode(errors="replace").split("=", 1) for p in fh.read().split(b"\0") if b"=" in p]
    except OSError:
        return {}
    return {k: v for k, v in pairs}


def _pane(entry: dict | None) -> str:
    return str(entry["tmux"]).rsplit(".", 1)[-1] if entry and entry.get("tmux") else ""


def host_pane(entry: dict, regs: list[dict], clone: str) -> tuple[str, bool]:
    """The pane the stall lands on, and whether it is the session's OWN (plan D6, spec FR-005c)."""
    if entry.get("tmux"):
        return _pane(entry), True
    disp = _environ(entry.get("pid")).get("L7R_DISPATCHER", "")
    for cand in (
        next((r for r in regs if disp and r.get("sessionId") == disp and r.get("tmux")), None),
        next((r for r in regs if entry.get("jobId") and r.get("parkedJobId") == entry.get("jobId") and r.get("tmux")), None),
        next((r for r in regs if r is not entry and r.get("kind") == "interactive" and r.get("tmux") and clone and clone_of(r) == clone), None),
    ):
        if cand:
            return _pane(cand), False
    return "", False


def judge(entry: dict, now: float) -> dict | None:
    """The stall, or None. `{"last", "idle", "clone", "what"}`."""
    sid = entry["sessionId"]
    last = last_activity(sid)
    if last is None or now - last < STALL_AFTER or entry.get("status") == "waiting":
        return None
    main = [t for t in transcripts(sid) if t.endswith(f"/{sid}.jsonl")]
    if main and asking_gm(main[0]):
        return None
    clone = clone_of(entry)
    what = unfinished(clone) if clone else ""
    if not what or in_retry_wait(clone, sid, now):
        return None
    return {"last": last, "idle": int(now - last), "clone": clone, "what": what}


def human(seconds: int) -> str:
    h, m = divmod(seconds // 60, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m"


def tmux(*args: str) -> str:
    try:
        return subprocess.run([_env("STALL_TMUX", "tmux"), *args], capture_output=True, text=True, timeout=10, check=False).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def input_empty(pane: str) -> bool:
    """One line between the last two rules, and it is the prompt mark with nothing typed after it."""
    lines = tmux("capture-pane", "-p", "-t", pane).splitlines()
    rules = [i for i, ln in enumerate(lines) if _RULE.match(ln)]
    if len(rules) < 2:
        return False
    between = lines[rules[-2] + 1 : rules[-1]]
    return len(between) == 1 and bool(_EMPTY_INPUT.fullmatch(between[0]))


def mark(pane: str, name: str, idle: int, bell: bool) -> bool:
    tty = tmux("display", "-p", "-t", pane, "#{pane_tty}").strip()
    if not tty:
        return False
    try:
        with open(tty, "w", encoding="utf-8") as fh:
            fh.write(f"\033]0;⚠ STALLED {human(idle)} - {name}\007" + ("\a" if bell else ""))
    except OSError:
        return False
    return True


def nudge(pane: str, text: str) -> None:
    tmux("send-keys", "-t", pane, "-l", text)
    tmux("send-keys", "-t", pane, "Enter")


def resume_command(entry: dict, clone: str) -> str:
    sid = entry["sessionId"]
    try:
        with open(os.path.join(clone, ".git", "page-sessions", "index.txt"), encoding="utf-8") as fh:
            brief = next((ln.split(" ", 1)[1].strip() for ln in fh if ln.startswith(sid + " ")), "")
    except OSError:
        brief = ""
    return f'make page-session BRIEF="resume:{sid}:{brief}"' if brief else f"cd {entry.get('cwd') or clone} && claude --resume {sid}"


def nudge_text(stall: dict) -> str:
    return (f"watchdog (feature 295): this session has been idle {stall['idle'] // 60} min with unfinished work in "
            f"{stall['clone']} ({stall['what']}). If you are waiting on the GM, say so in one line and stop; otherwise "
            "check your background work and carry on.")


def _state(sid: str) -> dict:
    try:
        with open(os.path.join(state_dir(), f"{sid}.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def run_pass(now: float | None = None) -> list[str]:
    """One pass over every live session; returns the log lines it wrote."""
    now = time.time() if now is None else now
    os.makedirs(state_dir(), exist_ok=True)
    regs = live_sessions()
    said = []
    for entry in regs:
        stall = judge(entry, now)
        sid = entry["sessionId"]
        if stall is None:
            continue
        if os.environ.get("STALL_DRYRUN"):  # judge only: no tab, no nudge, no state (a session inspecting the judgment)
            said.append(f"would mark {entry.get('name')} ({sid}) idle {stall['idle'] // 60} min, {stall['what']} in {stall['clone']}")
            continue
        st = _state(sid)
        if st.get("stall") != stall["last"]:  # activity since the last stall: this is a new one
            st = {"stall": stall["last"], "belled": False, "nudged": False}
        name = entry.get("name") or os.path.basename(stall["clone"])
        pane, own = host_pane(entry, regs, stall["clone"])
        marked = bool(pane) and mark(pane, name, stall["idle"], not st["belled"])
        st["belled"] = st["belled"] or marked
        nudged = ""
        if own and marked and not st["nudged"] and input_empty(pane):
            nudge(pane, nudge_text(stall))
            st["nudged"], nudged = True, "; nudged"
        where = f"marked {pane}{' (own)' if own else ' (host)'}" if marked else "no tab, logged only"
        resume = "" if own else f"; resume: {resume_command(entry, stall['clone'])}"
        said.append(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now))} stalled {name} ({sid}) idle "
                    f"{stall['idle'] // 60} min, {stall['what']} in {stall['clone']}; {where}{nudged}{resume}")
        with open(os.path.join(state_dir(), f"{sid}.json"), "w", encoding="utf-8") as fh:
            json.dump(st, fh)
    if said and not os.environ.get("STALL_DRYRUN"):
        with open(os.path.join(state_dir(), "log"), "a", encoding="utf-8") as fh:
            fh.write("".join(s + "\n" for s in said))
    return said


if __name__ == "__main__":
    if sys.argv[1:] == ["pass"]:
        for line in run_pass():
            print(line)
        sys.exit(0)
    print("usage: _stall_watchdog.py pass", file=sys.stderr)
    sys.exit(2)
