#!/usr/bin/env python3
"""Launch one run of the effort-level experiment (feature 293, contracts/cli.md `make effort-run`).

WHAT A RUN IS. One task (R, the servants' quarters research; I, the burial-ground footpath) at one arm (`medium` or
`xhigh`), as top-level headless sessions in a fresh clone of its own at the experiment's one start commit. Task R is the
project's two page sessions (write, then check-and-apply) through `scripts/page-session.sh`; task I is one full session.
Everything the arms share - the start commit, the prompts, the pinned ad-hoc judge, the sources snapshot - is recorded
ONCE in `experiment.json` by `init`, and every launch is checked against it.

THE CONTROLS THIS ENFORCES, each with its research decision (specs/293-effort-level-experiment/research.md):
- R1 D1: the arm is set with `--effort` and never `CLAUDE_CODE_EFFORT_LEVEL`, which would also override the effort every
  check agent pins in its frontmatter; the launcher removes it from the run's environment.
- R1 D2: every session carries the same `--agents` JSON defining `adhoc-judge` (opus, effort high).
- R5 D7: strictly sequential (the GM, 2026-09-29, "sequentially rather than in parallel for memory reasons"): no launch
  while another run is live, while the working set plus the measured offset is over the threshold, or while a memwatch
  warning is fresh.
- R6 D4/D6: each run reads its own copy of the sources ledger and page cache (`L7R_SOURCES_HOME`), and the run record says
  what shared state it found.
- Spec SC-002: no launch once the rubrics or prompts differ from their frozen hashes.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import random
import shutil
import subprocess
import sys
import time
import uuid

FEATURE = "293-effort-level-experiment"
ARMS = ("medium", "xhigh")
TASKS = ("R", "I")
PROMPTS = {"R": ("prompts/R-write.md", "prompts/R-check.md"), "I": ("prompts/I.md",)}
RUBRICS = ("rubrics/research.md", "rubrics/implementation.md")
# R5 D7. Both figures are GUESSES recorded with their arithmetic in research.md: the 9.0 GB shared cap less a run's own
# peak leaves about 4.5 GB for everything else; a warning under 15 minutes old has not yet passed.
THRESHOLD_GB = 4.5
WARNING_FRESH_S = 15 * 60
GB = 1_000_000_000
# R1 D2: the one ad-hoc judge, pinned by definition; frontmatter effort overrides the session's.
ADHOC_JUDGE = {
    "adhoc-judge": {
        "description": "Any ad-hoc work that checks or judges (a verdict, a review, a comparison) that no defined agent covers.",
        "prompt": "You check or judge the work the dispatch describes and report a compact verdict: counts first, then only what to act on.",
        "model": "opus",
        "effort": "high",
    }
}
APPEND_PROMPT = "container-scripts/append-system-prompt.md"
MAKE_VARS = ("MAKEFLAGS", "MAKELEVEL", "MFLAGS", "MAKEOVERRIDES", "TASK", "RUN", "ARM", "ORDER", "START", "SEED", "OFFSET",
             "SOURCES_HOME", "SNAPSHOT")
# R5 D7 (revised at T09): the 9.0 GB cap is ONE host cgroup over every Claude container, read through the host-diag tool
# (read-only, no sudo for cgroup files). memwatch's figure is that cgroup's raw memory.current, page cache included.
HOST_DIAG = "/host-l7r-repo/gm-assistant/scripts/claude-diagnostics/client/host-diag"
SHARED_SLICE = "/sys/fs/cgroup/user.slice/user-1001.slice/user@1001.service/claude.slice/claude-containers.slice"


class Refused(Exception):
    """A launch the controls do not admit; nothing was started."""


def sha256(data: bytes | str) -> str:
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


def agents_json() -> str:
    return json.dumps(ADHOC_JUDGE, sort_keys=True)


def frozen_hashes(feature_dir: pathlib.Path) -> dict[str, str]:
    """The sha256 of every rubric and prompt file, keyed by its path in the feature directory."""
    files = [*RUBRICS, *(p for ps in PROMPTS.values() for p in ps)]
    return {f: sha256((feature_dir / f).read_bytes()) for f in files}


def working_set(cgroup: pathlib.Path) -> int:
    """`memory.current` less `inactive_file` - the memory the kernel cannot simply drop (R5 D7)."""
    current = int((cgroup / "memory.current").read_text().split()[0])
    for line in (cgroup / "memory.stat").read_text().splitlines():
        key, _, val = line.partition(" ")
        if key == "inactive_file":
            return current - int(val)
    return current


def parse_working_set(text: str) -> int | None:
    """`memory.current` less `inactive_file` from the two files' text printed one after the other, or None."""
    lines = text.split("\n")
    try:
        current = int(lines[0].split()[0])
    except (IndexError, ValueError):
        return None
    for line in lines[1:]:
        key, _, val = line.partition(" ")
        if key == "inactive_file" and val.strip().isdigit():
            return current - int(val)
    return None


def shared_working_set(host_diag: str) -> int | None:
    """The working set of the shared cgroup every Claude container is capped by, or None when the host cannot be read."""
    try:
        out = subprocess.run([host_diag, f"cat {SHARED_SLICE}/memory.current {SHARED_SLICE}/memory.stat"],
                             capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return parse_working_set(out.stdout) if out.returncode == 0 else None


def fresh_warning(events: pathlib.Path, now: float) -> str:
    """The newest memwatch warning younger than WARNING_FRESH_S, or ''."""
    if not events.is_dir():
        return ""
    recent = [p for p in events.iterdir() if p.is_file() and now - p.stat().st_mtime < WARNING_FRESH_S]
    return max(recent, key=lambda p: p.stat().st_mtime).name if recent else ""


def live_runs(runs: pathlib.Path) -> list[str]:
    """Run ids whose record has no `ended` - still live, or never measured."""
    if not runs.is_dir():
        return []
    return sorted(p.stem for p in runs.glob("*.json") if not json.loads(p.read_text()).get("ended"))


def refusal(exp: dict, feature_dir: pathlib.Path, task: str, cgroup: pathlib.Path, events: pathlib.Path,
            now: float, shared: int | None = None) -> tuple[str, dict]:
    """Why this launch may not start ('' when it may), and the memory reading it was judged on. With the SHARED cgroup's
    working set (R5 D7 revised) the gate reads it directly, no offset, and a memwatch warning - a raw figure that counts
    the page cache the kernel drops first - does not block; without it, this container's working set plus the offset,
    and a fresh warning blocks."""
    if shared is not None:
        reading = {"source": "shared-slice", "working_set_gb": round(shared / GB, 2), "offset_gb": 0.0,
                   "threshold_gb": THRESHOLD_GB, "fresh_warning": ""}
    else:
        reading = {"source": "container+offset", "working_set_gb": round(working_set(cgroup) / GB, 2),
                   "offset_gb": exp["offset_gb"], "threshold_gb": THRESHOLD_GB, "fresh_warning": fresh_warning(events, now)}
    if live := live_runs(feature_dir / "runs"):
        return f"another run is live or unmeasured: {', '.join(live)}", reading
    changed = [f for f, h in frozen_hashes(feature_dir).items() if exp["hashes"].get(f) != h]
    if changed:
        return f"changed since the freeze: {', '.join(changed)}", reading
    if exp["agents_sha256"] != sha256(agents_json()):
        return "the --agents JSON differs from the recorded one", reading
    if reading["fresh_warning"]:
        return f"a memwatch warning under 15 minutes old ({reading['fresh_warning']})", reading
    if reading["working_set_gb"] + reading["offset_gb"] > THRESHOLD_GB:
        return (f"memory: working set {reading['working_set_gb']} GB ({reading['source']}) + offset {reading['offset_gb']} GB is over "
                f"{THRESHOLD_GB} GB - retry later"), reading
    if task not in TASKS:
        return f"no task {task}", reading
    return "", reading


def arm_order(seed: int) -> dict[str, list[str]]:
    """Spec US2 AS6: task R's order drawn from the seed, task I's the other way round."""
    first = list(ARMS)
    random.Random(seed).shuffle(first)
    return {"R": first, "I": first[::-1]}


def run_env(env: dict[str, str], sources: pathlib.Path) -> dict[str, str]:
    # CLAUDE_CODE_EFFORT_LEVEL would override the checkers' pinned effort (R1 D1); SPECIFY_FEATURE would name the experiment
    # to any tool that prints it (FR-004's intent, the plan review's aside) - the runs push nothing and need no feature.
    # MAKEFLAGS, MAKELEVEL, MFLAGS and the target's own variables: `make effort-run ARM=xhigh ...` exports its command-line
    # variables to every child, so run e1 saw ARM=xhigh in its environment and its own `make` calls inherited TASK/RUN/ARM
    # through MAKEFLAGS (two of its make runs failed until it unset them - recorded in interventions.md).
    drop = {"CLAUDE_CODE_EFFORT_LEVEL", "SPECIFY_FEATURE", "SPECIFY_FEATURE_DIRECTORY", *MAKE_VARS}
    out = {k: v for k, v in env.items() if k not in drop}
    return out | {"L7R_SOURCES_HOME": str(sources)}


def full_session_cmd(prompt: str, name: str, sid: str, effort: str, appended: str) -> list[str]:
    """Task I's one session: the project's full instructions and tools, as an interactive session has them."""
    cmd = ["claude", "-p", prompt, "-n", name, "--session-id", sid, "--effort", effort, "--agents", agents_json(),
           "--permission-mode", "bypassPermissions"]
    if appended:
        cmd += ["--append-system-prompt", appended]
    return cmd + ["--output-format", "json"]


def make_clone(clone: pathlib.Path, source: str, start: str, mirror: str) -> None:
    """The run's clone at `start`, holding nothing later (spec FR-003: no record linking a run id or position to an arm).

    A `git clone` of the session's repository would copy every object and keep its tip in the reflog, where the run records
    and the order can be read back (the amendment review, round 2); so a fresh repository fetches the start commit alone, the
    feature directory is left out of the working tree, and `origin` is the mirror (main), as in any clone the hooks expect.
    """
    git = ["git", "-C", str(clone)]
    subprocess.run(["git", "init", "-q", "-b", "main", str(clone)], check=True)
    subprocess.run([*git, "fetch", "-q", source, start], check=True)
    subprocess.run([*git, "sparse-checkout", "set", "--no-cone", "/*", f"!/specs/{FEATURE}/"], check=True)
    subprocess.run([*git, "reset", "-q", "--hard", start], check=True)
    subprocess.run([*git, "remote", "add", "origin", mirror], check=True)
    subprocess.run([*git, "fetch", "-q", "origin"], check=True)


def mangled(path: pathlib.Path) -> str:
    return str(path).replace("/", "-").replace(".", "-")


def launch(args: argparse.Namespace, repo: pathlib.Path, now: float) -> dict:
    feature_dir = repo / "specs" / FEATURE
    exp = json.loads((feature_dir / "experiment.json").read_text())
    why, reading = refusal(exp, feature_dir, args.task, pathlib.Path(args.cgroup), pathlib.Path(args.events), now,
                           shared_working_set(args.host_diag) if args.host_diag else None)
    if why:
        raise Refused(why)
    run_id, arm = args.run, args.arm
    base = pathlib.Path(args.clones)
    clone = base / f"diagram-exp-{run_id}"
    if clone.exists():
        raise Refused(f"{clone} exists - a run id is used once")
    start = exp["start_commit"]  # ONE start commit for every run (FR-005); a replaced task's files come from the freeze below
    make_clone(clone, args.origin or str(repo), start, args.mirror)
    work = base / ".runs-293" / run_id  # a neutral name: the sources path is in the run's environment
    sources = work / "sources"
    shutil.copytree(exp["sources_snapshot"], sources)
    env = run_env(dict(os.environ), sources)
    projects = pathlib.Path.home() / ".claude" / "projects" / mangled(clone)
    record = {"run_id": run_id, "task": args.task, "arm": arm, "seed": exp["seed"], "order": args.order,
              "start_commit": start, "clone": str(clone), "started": iso(now), "ended": None,
              "pauses": [], "memory_at_launch": reading, "agents_json_sha256": sha256(agents_json()),
              "env": {"L7R_SOURCES_HOME": str(sources), "CLAUDE_CODE_EFFORT_LEVEL": "unset", "SPECIFY_FEATURE": "unset"},
              "shared_state": {"sources_snapshot_sha256": exp["sources_snapshot_sha256"], **claims_at_start(args.claims)},
              "sessions": []}
    if args.task == "R":
        # FR-004: the page runner's prompt names the brief's path, and the feature directory's name says "effort"; the briefs
        # are copied, byte for byte, to a neutral path in the run clone and run from there.
        neutral = clone / "handoffs" / "293"
        neutral.mkdir(parents=True, exist_ok=True)
        briefs = []
        for p in PROMPTS["R"]:
            shutil.copyfile(feature_dir / p, neutral / pathlib.Path(p).name)  # the frozen file (its hash was checked above)
            briefs.append(str(neutral / pathlib.Path(p).name))
        agents = work / "agents.json"
        agents.write_text(agents_json(), encoding="utf-8")
        cmd = [str(clone / "scripts" / "page-session.sh"), " ".join(briefs), clone.name, "", arm, str(agents)]
        out = subprocess.run(cmd, cwd=clone, env=env, capture_output=True, text=True, check=False)
        if out.returncode:
            # Nothing started: the clone and the run's directory go, so the run id can be used again.
            shutil.rmtree(clone)
            shutil.rmtree(work)
            raise Refused(f"page-session refused: {out.stderr.strip()[:300]}")
        record["argv"] = cmd
        record["sessions"] = [{"brief": b, "prompt_sha256": exp["hashes"][p], "effort": arm, "log": None}
                              for b, p in zip(briefs, PROMPTS["R"], strict=True)]
        record["runner_stdout"] = out.stdout
    else:
        sid = str(uuid.uuid4())
        log = work / "session"
        log.mkdir(parents=True)
        prompt = (feature_dir / PROMPTS["I"][0]).read_text(encoding="utf-8")  # the frozen file (its hash was checked above)
        appended_file = clone / APPEND_PROMPT
        appended = appended_file.read_text(encoding="utf-8").strip() if appended_file.is_file() else ""
        cmd = full_session_cmd(prompt, clone.name, sid, arm, appended)
        with open(log / "result.json", "w") as out_f, open(log / "stderr.txt", "w") as err_f:
            subprocess.Popen(cmd, cwd=clone, env=env, stdin=subprocess.DEVNULL, stdout=out_f, stderr=err_f,
                             start_new_session=True, close_fds=True)
        record["argv"] = [c if c != prompt else f"<prompts/I.md sha256 {exp['hashes'][PROMPTS['I'][0]]}>" for c in cmd]
        record["sessions"] = [{"sid": sid, "prompt_sha256": exp["hashes"][PROMPTS["I"][0]], "effort": arm,
                               "transcript": str(projects / f"{sid}.jsonl"), "log": str(log)}]
    runs = feature_dir / "runs"
    runs.mkdir(exist_ok=True)
    (runs / f"{run_id}.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return record


RESUME_MESSAGE = ("The detached run you were waiting for has ended - nothing will notify you of it in this headless session. "
                  "Read its output and continue the task.")


def last_event(transcript: pathlib.Path) -> str:
    stamps = [json.loads(ln).get("timestamp") for ln in transcript.read_text(errors="replace").splitlines() if ln.strip()]
    return max(t for t in stamps if t)


def resume(repo: pathlib.Path, run_id: str, now: float, kill: bool = True) -> dict:
    """Spec edge case: a headless task-I session left waiting on a detached run nothing can wake it for is resumed with ONE
    fixed, arm-neutral message (the same for every run it happens to); the wait, from its last event to now, is a pause and
    is excluded from its wall-clock; the idle process is stopped first, so two processes never write one session."""
    feature_dir = repo / "specs" / FEATURE
    path = feature_dir / "runs" / f"{run_id}.json"
    run = json.loads(path.read_text())
    if run["task"] != "I":
        raise Refused("only a task I session is resumed this way; a page session is resumed by its runner")
    sess = run["sessions"][0]
    if kill:
        for pid in subprocess.run(["pgrep", "-f", "--", f"(--session-id|--resume) {sess['sid']}"], capture_output=True, text=True).stdout.split():
            subprocess.run(["kill", pid], check=False)
    clone = pathlib.Path(run["clone"])
    appended_file = clone / APPEND_PROMPT
    appended = appended_file.read_text(encoding="utf-8").strip() if appended_file.is_file() else ""
    cmd = full_session_cmd(RESUME_MESSAGE, clone.name, sess["sid"], run["arm"], appended)
    cmd[cmd.index("--session-id")] = "--resume"
    env = run_env(dict(os.environ), pathlib.Path(run["env"]["L7R_SOURCES_HOME"]))
    log = pathlib.Path(sess["log"])
    n = len(run.get("resumes", []))
    with open(log / f"result-{n}.json", "w") as out_f, open(log / f"stderr-{n}.txt", "w") as err_f:
        subprocess.Popen(cmd, cwd=clone, env=env, stdin=subprocess.DEVNULL, stdout=out_f, stderr=err_f,
                         start_new_session=True, close_fds=True)
    run.setdefault("pauses", []).append([last_event(pathlib.Path(sess["transcript"])), iso(now)])
    run.setdefault("resumes", []).append({"at": iso(now), "message": RESUME_MESSAGE, "result": str(log / f"result-{n}.json")})
    path.write_text(json.dumps(run, indent=1) + "\n", encoding="utf-8")
    return run


def claims_at_start(claims: str) -> dict:
    """R6 D6: the claims file as the run found it - its hash, and the lines naming the servants' quarters question."""
    p = pathlib.Path(claims)
    if not p.is_file():
        return {"claims_sha256_at_start": None, "claims_lines_at_start": []}
    text = p.read_text(encoding="utf-8")
    hits = [ln for ln in text.splitlines() if "servants" in ln.lower() or "293" in ln]
    return {"claims_sha256_at_start": sha256(text), "claims_lines_at_start": hits}


def iso(t: float) -> str:
    return dt.datetime.fromtimestamp(t, dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


TASK_FILES = {"R": ("rubrics/research.md", *PROMPTS["R"]), "I": ("rubrics/implementation.md", *PROMPTS["I"])}


def refreeze_task(repo: pathlib.Path, task: str, now: float) -> dict:
    """Spec edge case (a task found impossible after the freeze, replaced after asking the GM): the task's prompt and rubric
    are frozen again - their hashes recorded - before its next run; its runs still start from the one start commit, the
    launcher supplying the frozen files; every other task's record is untouched."""
    feature_dir = repo / "specs" / FEATURE
    target = feature_dir / "experiment.json"
    exp = json.loads(target.read_text())
    runs = [json.loads(p.read_text()) for p in (feature_dir / "runs").glob("*.json")] if (feature_dir / "runs").is_dir() else []
    if any(r["task"] == task and r.get("status") == "valid" for r in runs):
        raise Refused(f"task {task} has a valid run - void or replace it before re-freezing")
    hashes = frozen_hashes(feature_dir)
    for f in TASK_FILES[task]:
        exp["hashes"][f] = hashes[f]
    exp.pop("starts", None)
    exp.setdefault("refrozen", []).append({"task": task, "at": iso(now), "hashes": {f: hashes[f] for f in TASK_FILES[task]}})
    target.write_text(json.dumps(exp, indent=1) + "\n", encoding="utf-8")
    return exp


def init(args: argparse.Namespace, repo: pathlib.Path, now: float) -> dict:
    """Pre-flight (T09-T11): record what every run shares. Refuses to overwrite an experiment already recorded."""
    feature_dir = repo / "specs" / FEATURE
    target = feature_dir / "experiment.json"
    if target.exists():
        raise Refused(f"{target} exists - the experiment's shared record is written once")
    snapshot = pathlib.Path(args.snapshot)
    src = pathlib.Path(args.sources_home)
    snapshot.mkdir(parents=True)
    for name in ("sources-consulted.jsonl", "page-cache"):  # the ledger and the cache `_sources.home()` holds - nothing else
        if (src / name).is_dir():
            shutil.copytree(src / name, snapshot / name)
        elif (src / name).is_file():
            shutil.copyfile(src / name, snapshot / name)
    ledger = snapshot / "sources-consulted.jsonl"
    exp = {"start_commit": args.start, "seed": args.seed, "order": arm_order(args.seed), "offset_gb": args.offset,
           "sources_snapshot": str(snapshot),
           "sources_snapshot_sha256": sha256(ledger.read_bytes()) if ledger.is_file() else None,
           "hashes": frozen_hashes(feature_dir), "agents_sha256": sha256(agents_json()), "recorded": iso(now)}
    target.write_text(json.dumps(exp, indent=1) + "\n", encoding="utf-8")
    return exp


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="effort-run")
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    i.add_argument("--start", required=True)
    i.add_argument("--seed", type=int, required=True)
    i.add_argument("--offset", type=float, required=True)
    i.add_argument("--sources-home", required=True)
    i.add_argument("--snapshot", required=True)
    f = sub.add_parser("refreeze-task")
    f.add_argument("--task", required=True, choices=TASKS)
    rs = sub.add_parser("resume")
    rs.add_argument("--run", required=True)
    r = sub.add_parser("run")
    r.add_argument("--task", required=True, choices=TASKS)
    r.add_argument("--run", required=True)
    r.add_argument("--arm", required=True, choices=ARMS)
    r.add_argument("--order", type=int, required=True)
    # The runs clone from the SESSION's clone at the frozen start commit: the feature's tooling cannot land on main while its
    # tasks are open (sync-with-main's open-task refusal), so the start commit exists only here until the feature lands.
    r.add_argument("--origin", default="", help="default: this repository")
    r.add_argument("--mirror", default="/diagram", help="the run clone's origin (main), fetched after the start commit")
    r.add_argument("--clones", default="/diagram/.clones")
    r.add_argument("--claims", default="/diagram/.clones/RESEARCH-CLAIMS.md")
    r.add_argument("--cgroup", default="/sys/fs/cgroup")
    r.add_argument("--host-diag", default=HOST_DIAG, help="'' to judge on this container's working set plus the offset")
    r.add_argument("--events", default=str(pathlib.Path.home() / ".claude" / "memwatch" / "events"))
    args = ap.parse_args(argv)
    repo = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                                       check=True).stdout.strip())
    try:
        if args.cmd == "resume":
            run = resume(repo, args.run, time.time())
            print(f"effort-run: {args.run} resumed; paused {run['pauses'][-1][0]} - {run['pauses'][-1][1]}")
        elif args.cmd == "refreeze-task":
            refreeze_task(repo, args.task, time.time())
            print(f"effort-run: task {args.task}'s prompt and rubric re-frozen; its runs start from the experiment's start commit")
        elif args.cmd == "init":
            exp = init(args, repo, time.time())
            print(f"effort-run: experiment recorded - start {exp['start_commit'][:10]}, order {exp['order']}")
        else:
            rec = launch(args, repo, time.time())
            print(f"effort-run: {rec['run_id']} started ({rec['task']}) in {rec['clone']}")
            for s in rec["sessions"]:
                print(f"  session {s.get('sid') or s.get('brief')}  transcript {s.get('transcript', 'see runner output')}")
            if rec.get("runner_stdout"):
                print(rec["runner_stdout"])
    except Refused as e:
        print(f"effort-run: REFUSED, nothing started - {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
