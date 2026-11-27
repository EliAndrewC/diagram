"""451 T536: bytes each hot command reads of 451's large records, and its wall time, run on a COPY (read-only on the real tree).

Usage: python3 -I t536-readers-run.py <scratch dir holding repo/ and target/> > t536-readers-run.txt

The copy: `git clone --shared` of the pool tree at HEAD, its 451 records replaced by the snapshot copies (t536-snapshot.txt), the
feature's event log copied to repo/.git/l7r-events/, the tree's built l7r-gate and l7r-guard copied to target/ (cargo set to
/bin/false so nothing is rebuilt), the copy's rust/ sources dated old so no wrapper thinks them stale.

Each case runs once under the LD_PRELOAD shim t536-readcount.so (built from t536-readcount.c; strace is refused here: ptrace is
not permitted in this container) and its read() returns are summed per path, by DIRECTORY
PREFIX (the feature directory, the events directory), so a split record's parts are counted the same way after T537. Then it runs
RUNS times without the shim for the median wall time. Any open for writing outside the scratch directory is listed (a safety check).
"""
import json, os, statistics, subprocess, sys, time

S = os.path.abspath(sys.argv[1])
REPO = f"{S}/repo"
FEAT = "451-time-retro-and-efficiency"
FDIR = f"{REPO}/specs/{FEAT}/"
EDIR = f"{REPO}/.git/l7r-events/"
GUARD = f"{S}/target/l7r-guard.good"
GATE = f"{S}/target/tool/l7r-gate"
RUNS = int(os.environ.get("RUNS", "5"))
# the open task the section and decide cases name: T536 for T536's own run; T537's after figure named T537, by then 451's one open task
OPEN = os.environ.get("T536_OPEN", "T536")
ENV = dict(os.environ, CLAUDE_PROJECT_DIR=REPO, L7R_GATE_TARGET=f"{S}/target", L7R_GUARD_TARGET=f"{S}/target",
           L7R_GATE_CARGO="/bin/false", L7R_GUARD_CARGO="/bin/false", L7R_EVENTS_DIR=EDIR.rstrip("/"),
           SPECIFY_FEATURE=FEAT, SPECIFY_FEATURE_DIRECTORY=f"specs/{FEAT}", CLONE_MAIN=REPO)
SID = "t536-copy-session"
TRANSCRIPT = f"{S}/transcripts/{SID}.jsonl"
os.makedirs(os.path.dirname(TRANSCRIPT), exist_ok=True)
open(TRANSCRIPT, "a").close()


def payload(ev, **kw):
    p = {"session_id": SID, "transcript_path": TRANSCRIPT, "cwd": REPO, "hook_event_name": ev,
         "agent_id": "a536000000000000", "agent_type": "general-purpose"}
    p.update(kw)
    return json.dumps(p)


PLAN = f"{FDIR}plan.md"
REVIEW_PROMPT = (f"MODE 4 (plan review)\nReview the plan section of feature {FEAT}, task T536 against the GM's words.\n")
CASES = [
    ("hook PreToolUse Bash", [GUARD, "PreToolUse"], payload("PreToolUse", tool_name="Bash",
        tool_input={"command": "ls", "description": "List files"}, tool_use_id="toolu_t536a")),
    ("hook PostToolUse Bash", [GUARD, "PostToolUse"], payload("PostToolUse", tool_name="Bash",
        tool_input={"command": "ls", "description": "List files"}, tool_use_id="toolu_t536a",
        tool_response={"stdout": "x", "stderr": "", "interrupted": False})),
    ("hook PreToolUse Edit plan.md", [GUARD, "PreToolUse"], payload("PreToolUse", tool_name="Edit",
        tool_input={"file_path": PLAN, "old_string": "### T536 (", "new_string": "### T536 ("}, tool_use_id="toolu_t536b")),
    ("hook PostToolUse Edit plan.md", [GUARD, "PostToolUse"], payload("PostToolUse", tool_name="Edit",
        tool_input={"file_path": PLAN, "old_string": "### T536 (", "new_string": "### T536 ("}, tool_use_id="toolu_t536b",
        tool_response={"filePath": PLAN})),
    ("hook PreToolUse Agent plan review", [GUARD, "PreToolUse"], payload("PreToolUse", tool_name="Agent",
        tool_input={"subagent_type": "spec-fidelity", "description": "451 T536 plan review", "prompt": REVIEW_PROMPT},
        tool_use_id="toolu_t536c")),
    ("hook SubagentStart", [GUARD, "SubagentStart"], payload("SubagentStart")),
    ("hook SessionStart", [GUARD, "SessionStart"], payload("SessionStart", source="startup")),
    ("hook Stop", [GUARD, "Stop"], payload("Stop", stop_hook_active=False)),
    (f"make plan-section T={OPEN}", [GATE, "plan", "section", FEAT, OPEN], ""),
    (f"make decide F=451 T={OPEN}", [GATE, "plan", "decide", "451", OPEN], ""),
    ("make plan-delta F=451", [GATE, "plan", "delta", "451"], ""),
    ("make queue F=451", [GATE, "queue", "451"], ""),
    ("make builder-next F=451", [GATE, "builder-next", "451"], ""),
    ("speckit-todo --holding (the push)", [GATE, "speckit-todo", "--holding", FDIR.rstrip("/")], ""),
    ("make task-time SINCE=24h", [GATE, "measure", "task-time", "--root", REPO, "--since", "24h"], ""),
    ("make task-add F=451", [GATE, "task-add", "451"], ""),
    ("make claims-triage", [GATE, "claims", "--root", REPO, "triage"], ""),
    ("make plan-section T=T499 (a done task's section, in plan-done.md)", [GATE, "plan", "section", FEAT, "T499"], ""),
    ("make where-time F=451", [GATE, "measure", "where-time", "451"], ""),
    ("make feature-report F=451", [GATE, "measure", "feature-report", "--root", REPO, "451"], ""),
]
ENV["TASK_TITLE"] = "t536 copy-only probe task (never landed)"

# UserPromptSubmit is left out unless T536_PROMPT=1: on 2026-11-27 its synthetic call set off the once-a-day scratch-sweep
# (869 removals, 886 guard-log rows under the fake session name). The stub plan-verdict and the tick were refused before any read
# and were dropped; those readers are named by code in results.md.
if os.environ.get("T536_PROMPT") == "1":
    CASES.insert(7, ("hook UserPromptSubmit", [GUARD, "UserPromptSubmit"], payload("UserPromptSubmit", prompt="status?")))
if os.environ.get("ONLY"):
    CASES = [c for c in CASES if os.environ["ONLY"] in c[0]]



def under(path):
    if path.startswith(FDIR):
        return "specs/451/" + path[len(FDIR):]
    if path.startswith(EDIR):
        return "events/" + path[len(EDIR):]
    return None


def run(argv, stdin, trace=None):
    env = dict(ENV)
    if trace:
        env.update(LD_PRELOAD=f"{S}/t536-readcount.so", T536_PREFIX=f"{FDIR}:{EDIR}", T536_LOG=trace, T536_SAFE=S)
    t = time.perf_counter()
    r = subprocess.run(argv, input=stdin, text=True, capture_output=True, cwd=REPO, env=env, timeout=600)
    return time.perf_counter() - t, r


for name, argv, stdin in CASES:
    trace = f"{S}/t536-trace.txt"
    if os.path.exists(trace):
        os.remove(trace)
    _, r = run(argv, stdin, trace)
    per, calls, writes, procs = {}, {}, set(), {}
    for line in open(trace, errors="replace") if os.path.exists(trace) else []:
        f = line.rstrip("\n").split("\t")
        if f[0] == "WRITE":
            writes.add(f[1])
            continue
        k = under(f[1])
        if k:
            per[k] = per.get(k, 0) + int(f[2])
            calls[k] = calls.get(k, 0) + int(f[3])
            procs.setdefault(k, set()).add(f[0])
    walls = [run(argv, stdin)[0] for _ in range(RUNS)]
    print(f"## {name}\texit {r.returncode}\twall median {statistics.median(walls) * 1000:.0f} ms (n={RUNS}, min "
          f"{min(walls) * 1000:.0f}, max {max(walls) * 1000:.0f})")
    for k in sorted(per):
        print(f"  {k}\t{per[k]:,} bytes\t{calls[k]} read calls\t{len(procs[k])} process(es)")
    if not per:
        print("  (none of 451's records read)")
    for w in sorted(writes):
        print(f"  WRITE OUTSIDE SCRATCH: {w}")
    out = (r.stdout + r.stderr).strip().splitlines()
    print("  output head: " + " | ".join(out[:2])[:240])
    sys.stdout.flush()
