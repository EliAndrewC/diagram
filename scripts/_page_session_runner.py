#!/usr/bin/env python3
"""The detached runner behind `page-session.sh` (feature 250 D7): each brief in a fresh headless session, in order.

    _page_session_runner.py <root> <name> <projects dir> [claude args ...] -- <brief | then:<script>> ...

Prints every known session's id, transcript and log directory at once, then starts ONE detached process that
works the queue in order: a brief runs as a fresh session; a `then:<script>` runs the script when it is reached
and queues the briefs it prints, one path a line - which is how a page's check sessions are planned from the
handoff its write session leaves (feature 250 R3, recommendation 2). Every session started is appended to
`<root>/.git/page-sessions/index.txt` as `<session id> <brief>`, so the meter can find the ones planned late.

THE FLOOR (feature 250 R3, recommendation 1). A page session is launched with only the tools research uses, no
MCP servers, no skill listing, and - in a clone - without the MIRROR's root CLAUDE.md, which sits above every
clone and otherwise loads beside the clone's own copy. Measured on a probe, 2026-09-26: the first turn of a
page session fell from 40,280 tokens to 21,267; every turn carries that floor.
"""

from __future__ import annotations

import calendar
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import uuid

PROMPT = ("You are a fresh session started to do the work ONE brief describes. Read {brief} first, and do what it says, "
          "end to end and unattended. Commit in this clone as you finish each part; never run the stop-work push. When the "
          "brief's work is done, or it tells you to stop, write the one-paragraph summary it asks for and stop.")

TOOLS = "Bash,Read,Edit,Write,Grep,Glob,Agent,WebFetch,WebSearch"


def floor_flags(root: str) -> list[str]:
    """The launch flags that lower a page session's fixed floor, and the reason for each in the docstring above."""
    flags = ["--disable-slash-commands", "--strict-mcp-config", "--tools", TOOLS]
    parts = root.rstrip("/").split("/")
    if ".clones" in parts:
        mirror = "/".join(parts[: parts.index(".clones")])
        flags += ["--settings", json.dumps({"claudeMdExcludes": [f"{mirror}/CLAUDE.md"]})]
    return flags


def command(root: str, name: str, extra: list[str], brief: str, sid: str) -> list[str]:
    return ["claude", "-p", PROMPT.format(brief=os.path.realpath(brief)), "-n", name, "--session-id", sid,
            "--permission-mode", "bypassPermissions", *floor_flags(root), *extra, "--output-format", "json"]


def plan(root: str, name: str, projects: str, extra: list[str], items: list[str]) -> list[dict]:
    """The queue: `{"sid", "log", "cmd"}` per brief (its log directory made), `{"then": script}` per late step."""
    queue: list[dict] = []
    for item in items:
        if item.startswith("resume:"):
            # `resume:<sid>:<brief>` - a session whose runner died with it (feature 271, 2026-09-27: the dispatching
            # session's process ended and took five queues' runners with it, each mid-way through a write session with
            # its work uncommitted). The same session is resumed with its own context, never started over.
            sid, brief = item[7:].split(":", 1)
            log = os.path.join(root, ".git", "page-sessions", sid)
            os.makedirs(log, exist_ok=True)
            queue.append({"sid": sid, "log": log, "brief": brief, "cmd": resume_command(command(root, name, extra, brief, sid), sid)})
            print(f"page-session: resume {sid} ({os.path.basename(brief)})")
            continue
        if item.startswith("then:"):
            queue.append({"then": os.path.realpath(item[5:])})
            print(f"page-session: then {os.path.basename(item[5:])} - the sessions it plans are listed in .git/page-sessions/index.txt")
            continue
        sid = str(uuid.uuid4())
        log = os.path.join(root, ".git", "page-sessions", sid)
        os.makedirs(log)
        queue.append({"sid": sid, "log": log, "brief": item, "cmd": command(root, name, extra, item, sid)})
        print(f"page-session: {os.path.basename(item)}\n  session:    {sid}\n  transcript: {projects}/{sid}.jsonl\n  log:        {log}")
    return queue


def dispatcher(root: str) -> str:
    """The session whose claim on `root` was written last - the one dispatching this queue into its own clone.

    WHY (feature 250 D14, 2026-09-26): the clone guard refuses an edit in a clone a LIVE other session claims, and
    the dispatcher is live, waiting on the queue - so a queued session was refused whenever the dispatcher's tree
    was clean. Its id goes to each session as `L7R_DISPATCHER`, which the guard lets through and nothing else."""
    parts = root.rstrip("/").split("/")
    if ".clones" not in parts:
        return ""
    mapdir = pathlib.Path("/".join(parts[: parts.index(".clones") + 1])) / ".session-clones"
    claims = [m for m in mapdir.glob("*") if m.is_file() and m.read_text(encoding="utf-8", errors="replace").strip() == root.rstrip("/")]
    return max(claims, key=lambda m: m.stat().st_mtime).name if claims else ""


def headless_env(parent: "os._Environ[str] | dict[str, str]", dispatcher_id: str) -> dict[str, str]:
    """The environment a queued session runs in: the dispatcher's, with its id added and its TMUX variables removed.

    WHY (2026-09-27): a queued session is headless and has no tab, but it inherited `TMUX`/`TMUX_PANE` from the
    session that started the queue, so it registered itself as living in THAT session's tmux pane - and the
    tab-title hook, finding a pane, retitled the GM's tab with the queued session's name (`diagram-research`)."""
    return {**{k: v for k, v in parent.items() if k not in ("TMUX", "TMUX_PANE")}, "L7R_DISPATCHER": dispatcher_id}


def work(root: str, name: str, extra: list[str], queue: list[dict], run_log: str = os.devnull) -> None:
    """The detached loop: each session in turn; a `then` step's printed briefs join the queue where it stood.

    THE RUN LOG (feature 250, 2026-09-26): one file, held OPEN for the whole queue, with a line as each session
    starts and ends and `ALL DONE` last. A caller waits on it with the ordinary backgrounded file-watch, and the
    liveness check the no-poll guard adds finds the runner holding it - so the wait ends when the runner does,
    finished or killed. Before it, a page's sessions left no one file to wait on, and a wait on `tasks.md` (edited,
    never held open) was declared dead after two minutes while the sessions ran on."""
    index = os.path.join(root, ".git", "page-sessions", "index.txt")
    runlog = open(run_log, "a", buffering=1)  # noqa: SIM115 - held open on purpose for the whole queue
    env = headless_env(os.environ, dispatcher(root))
    while queue:
        item = queue.pop(0)
        if "then" in item:
            got = subprocess.run([item["then"]], cwd=root, capture_output=True, text=True, check=False)
            late = []
            for brief in (ln.strip() for ln in got.stdout.splitlines() if ln.strip()):
                sid = str(uuid.uuid4())
                log = os.path.join(root, ".git", "page-sessions", sid)
                os.makedirs(log)
                late.append({"sid": sid, "log": log, "brief": brief, "cmd": command(root, name, extra, brief, sid)})
            queue[:0] = late
            runlog.write(f"planned {len(late)} session(s) from {os.path.basename(item['then'])}\n")
            continue
        with open(index, "a") as fh:
            fh.write(f"{item['sid']} {item['brief']}\n")
        runlog.write(f"started {item['sid']} {os.path.basename(item['brief'])}\n")
        cmd = item["cmd"]
        for attempt in range(RETRIES + 1):
            with open(item["log"] + "/result.json", "w") as out, open(item["log"] + "/stderr.txt", "w") as err:
                rc = subprocess.run(cmd, cwd=root, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err, check=False).returncode
            text = _read(item["log"] + "/result.json") + _read(item["log"] + "/stderr.txt")
            if not failed(rc, text) or attempt == RETRIES:
                break
            wait = wait_for(text, attempt, time.time())
            runlog.write(f"failed {item['sid']} rc={rc} - waiting {wait // 60} min, then resuming it ({first_line(text)})\n")
            time.sleep(wait)
            cmd = resume_command(item["cmd"], item["sid"])
        runlog.write(f"ended {item['sid']} rc={rc}\n")
    runlog.write("ALL DONE\n")
    runlog.close()


# THE USAGE LIMIT (2026-09-27, the GM: "if that happens, then we automatically resume once the window refreshes ... it's
# really important to me that we try to get this done without just kind of stopping for hours and hours"). A session
# that fails - the plan's five-hour window spent, an overloaded API, a crash - used to be logged and the NEXT brief
# started, which fails the same way at once, so one spent window burned the whole rest of the queue. Now a failed
# session is RESUMED (`--resume <id>`, so it carries on with its own context) after a wait: until the reset time the
# message names when it names one, else a backoff of 15, 30, then 60 minutes, for up to RETRIES attempts (~11 hours).
RETRIES = 14
BACKOFF = (15 * 60, 30 * 60, 60 * 60)
RESUME = "Continue the work of the brief you were given, from where you stopped - an error or the usage limit ended your last turn."


def _read(path: str) -> str:
    try:
        return pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def failed(rc: int, text: str) -> bool:
    """Whether a session ended in failure: a non-zero exit, or the JSON result says it was an error."""
    if rc != 0:
        return True
    try:
        got = json.loads(text[: text.rfind("}") + 1] or "{}")
    except ValueError:
        return False
    return bool(got.get("is_error")) or got.get("subtype") not in (None, "success")


def wait_for(text: str, attempt: int, now: float) -> int:
    """Seconds to wait before resuming: two minutes past the reset the message names (an epoch after a `|`, or `resets
    <h>am|pm` in UTC), else the backoff for this attempt. Never under a minute, never over six hours."""
    m = re.search(r"\|(\d{10})\b", text)
    if m:
        return int(min(max(int(m.group(1)) - now + 120, 60), 6 * 3600))
    m = re.search(r"resets?\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*([ap]m)", text, re.I)
    if m:
        t = time.gmtime(now)
        hour = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "pm" else 0)
        target = calendar.timegm((t.tm_year, t.tm_mon, t.tm_mday, hour, int(m.group(2) or 0), 0))
        if target <= now:
            target += 86400
        return int(min(max(target - now + 120, 60), 6 * 3600))
    return BACKOFF[min(attempt, len(BACKOFF) - 1)]


def resume_command(cmd: list[str], sid: str) -> list[str]:
    """The same session's command, resumed: `--session-id <sid>` becomes `--resume <sid>`, the prompt a continue."""
    out = list(cmd)
    i = out.index("--session-id")
    out[i : i + 2] = ["--resume", sid]
    out[out.index("-p") + 1] = RESUME
    return out


def first_line(text: str) -> str:
    return next((ln.strip()[:160] for ln in text.splitlines() if ln.strip()), "no output")


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--work":
        _, root, name, extra, queue, run_log = argv
        work(root, name, json.loads(extra), json.loads(queue), run_log)
        return 0
    root, name, projects, *rest = argv
    cut = rest.index("--")
    extra, items = rest[:cut], rest[cut + 1:]
    queue = plan(root, name, projects, extra, items)
    run_log = os.path.join(root, ".git", "page-sessions", f"run-{uuid.uuid4().hex[:8]}.log")
    open(run_log, "w").close()  # it exists before the wait starts, so the wait never races its creation
    subprocess.Popen([sys.executable, os.path.abspath(__file__), "--work", root, name, json.dumps(extra), json.dumps(queue), run_log],
                     cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True, close_fds=True)
    print("page-session: started - each result.json is written when its session ends, and the next session begins")
    print(f"page-session: to be told when the whole queue has ended, run this BACKGROUNDED (run_in_background):\n"
          f"    until grep -q '^ALL DONE' {run_log}; do sleep 60; done; tail -20 {run_log}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
