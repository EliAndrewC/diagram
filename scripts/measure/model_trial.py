#!/usr/bin/env python3
"""A review check re-run on another model against a RECORDED run with known findings (feature 383 amendment 3, plan D24).

Feature 251's seeded-run method (`specs/251-tiered-subagent-checks/measure/seeded.py`, research R5), kept as a tool so the
next trial is a command, not an archaeology. The GM, 2026-10-17: *"If we have never tried spec fidelity or glyph check or
implementation drift or building review. Or the three modal checks on Sonnet, then that is definitely 100% worth testing"*.

    model_trial.py catalog <agent> [--since YYYY-MM-DD]     the recorded runs of a check, newest first, with their verdict words
    model_trial.py prepare <transcript> <out> [--model M] [--head]
    model_trial.py run <out> [--runs 3]                      each run a headless session in the case's worktree, backgrounded
    model_trial.py usage <out>                               turns, tokens and seconds of the recorded run and of each new one
    model_trial.py run-all <root> [--runs 3] [--parallel 6] every prepared case under <root>, queued
    model_trial.py snapshot <out>                            rebuild a review snapshot at the case's commit (renders are not tracked)

`prepare` builds a detached worktree at the last commit of this clone's history before the recorded run (`--head`: at HEAD,
for a run that read another clone's work this history holds only later), copies the CURRENT agent files in with the tested
model written into the tested agent's copy (`model:` in its frontmatter - the worktree's copy only), and rewrites the prompt's
clone paths to the worktree. A prompt naming a path outside the repository that no longer exists (an old bundle under
`/tmp/l7r-check/`) is reported MISSING: such a case is not a fair re-run. A run is `claude -p --agent <name>` started in the
worktree with every hook off (they are wired to the mirror and judge the session, not the check - 251 research R4).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve()
CLONE = HERE.parents[2]
PROJECTS = pathlib.Path.home() / ".claude" / "projects"
SIGNALS = (
    "FAITHFUL",
    "CHANGES REQUIRED",
    "CLEAR",
    "BLOCKED",
    "NOT-REVIEWABLE",
    "IN-STEP",
    "DRIFTED",
    "NEEDS-RESEARCH",
    "MISLABELED",
    "CANNOT-TELL",
    "UNCLAIMED",
    "PASS",
    "FAIL",
    "OK",
    "ISSUE",
    "FINDING",
)
SONNET = "claude-sonnet-5-5"


def text_of(content: object) -> str:
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


def read(transcript: pathlib.Path) -> dict:
    """The recorded run: its agent, prompt, final reply, start and working directory."""
    records = [json.loads(line) for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip().startswith("{")]
    prompt = next((text_of(r["message"]["content"]) for r in records if r.get("type") == "user"), "")
    reply = next((text_of(r["message"]["content"]) for r in reversed(records) if r.get("type") == "assistant" and text_of(r["message"].get("content"))), "")
    meta_path = transcript.with_suffix("").with_suffix(".meta.json")
    meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
    stamps = [r.get("timestamp", "") for r in records if r.get("timestamp")]
    return {"agent": meta.get("agentType", ""), "prompt": prompt, "reply": reply, "started": stamps[0] if stamps else "", "ended": stamps[-1] if stamps else "", "records": records}


def signature(reply: str) -> str:
    return " ".join(f"{s}={n}" for s in SIGNALS if (n := len(re.findall(rf"\b{re.escape(s)}\b", reply))))


def replayable(run: dict) -> bool:
    """Every path outside the repository the prompt names exists and was not written after the run started."""
    started = _epoch(run["started"])
    for p in outside_paths(run["prompt"]):
        src = pathlib.Path(p)
        if not src.exists():
            return False
        root = src if src.is_dir() else src.parent
        if max((f.stat().st_mtime for f in root.rglob("*") if f.is_file()), default=root.stat().st_mtime) > started:
            return False
    return True


def catalog(agent: str, since: str = "", only_replayable: bool = False) -> None:
    rows = []
    for meta in PROJECTS.glob("-diagram*/*/subagents/agent-*.meta.json"):
        try:
            if json.loads(meta.read_text()).get("agentType") != agent:
                continue
        except OSError, ValueError:
            continue
        t = meta.with_name(meta.name.replace(".meta.json", ".jsonl"))
        if not t.is_file():
            continue
        run = read(t)
        if run["reply"] and run["started"][:10] >= since and (not only_replayable or replayable(run)):
            rows.append((run["started"], t, run))
    for started, t, run in sorted(rows, key=lambda r: r[0], reverse=True):
        print(f"{started[:16]}  {t}\n    prompt={len(run['prompt'])} reply={len(run['reply'])}  {signature(run['reply'])}\n    {' '.join(run['prompt'].split())[:200]}")


def set_model(agent_file: pathlib.Path, model: str) -> None:
    """The tested model in the agent file's frontmatter (the worktree's copy)."""
    text = agent_file.read_text(encoding="utf-8")
    head, sep, body = text.partition("\n---\n")
    head = re.sub(r"(?m)^model:.*$", f"model: {model}", head) if re.search(r"(?m)^model:", head) else head + f"\nmodel: {model}"
    agent_file.write_text(head + sep + body, encoding="utf-8")


def _epoch(stamp: str) -> float:
    from datetime import datetime  # noqa: PLC0415

    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp() if stamp else 0.0


def clone_head_at(clone: pathlib.Path, when: float) -> str:
    """A clone's HEAD at a moment, from its reflog ("" when the reflog does not reach back that far)."""
    log = subprocess.run(["git", "-C", str(clone), "log", "-g", "--date=unix", "--format=%H %gd", "HEAD"], capture_output=True, text=True, check=False).stdout
    for line in log.splitlines():  # newest first
        sha, _, rest = line.partition(" ")
        m = re.search(r"@\{(\d+)\}", rest)
        if m and int(m.group(1)) <= when:
            return sha
    return ""


def outside_paths(prompt: str) -> list[str]:
    """Paths a prompt names that no checkout holds, each once: a bundle under `/tmp/`, and a clone's git directory (the review
    snapshots under `<clone>/.git/review-snapshot/`, which hold the renders a glyph or building review judges)."""
    found = re.findall(r"(?:/tmp/|/diagram/\.clones/[\w-]+/\.git/)[^\s`'\")]+", prompt)
    return sorted({p.rstrip(".,):;`'\"") for p in found})


def prepare(transcript: pathlib.Path, out: pathlib.Path, model: str = SONNET, at_head: bool = False) -> int:
    run = read(transcript)
    out.mkdir(parents=True, exist_ok=True)
    rev = ["rev-parse", "HEAD"]
    commit = subprocess.run(["git", "-C", str(CLONE), *rev], capture_output=True, text=True, check=True).stdout.strip()
    if not at_head:  # the HEAD the run read: the recording clone's reflog (a commit's own date is not when it was checked out)
        cwd = next((r.get("cwd", "") for r in run["records"] if r.get("cwd")), "")
        m = re.match(r"/diagram/\.clones/([\w-]+)", cwd)
        home = CLONE.parent / m.group(1) if m and (CLONE.parent / m.group(1) / ".git").exists() else CLONE
        at = clone_head_at(home, _epoch(run["started"]))
        if at:
            subprocess.run(["git", "-C", str(CLONE), "fetch", "-q", str(home), at], capture_output=True, check=False)
            commit = at
    # A RUN THAT JUDGED ANOTHER CLONE judged that clone's HEAD at the time, unlanded then: its reflog gives the commit, and a
    # local fetch brings it here if this history lacks it
    named = re.search(r"/diagram/\.clones/([\w-]+)", run["prompt"])
    if named and not at_head and (CLONE.parent / named.group(1) / ".git").exists():
        other = CLONE.parent / named.group(1)
        at = clone_head_at(other, _epoch(run["started"]))
        if at:
            subprocess.run(["git", "-C", str(CLONE), "fetch", "-q", str(other), at], capture_output=True, check=False)
            commit = at
    tree = out / "tree"
    if not tree.is_dir():
        # A CLONE OF ITS OWN, not a worktree: a check's last act writes review state (`make review-verdict`, `make
        # plan-verdict`) into its git directory, and a worktree's is this clone's - a trial would overwrite a real verdict
        subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(CLONE), str(tree)], capture_output=True, text=True, check=True)
        subprocess.run(["git", "-C", str(tree), "checkout", "-q", "--detach", commit], capture_output=True, text=True, check=True)
    shutil.copytree(CLONE / ".claude" / "agents", tree / ".claude" / "agents", dirs_exist_ok=True)
    set_model(tree / ".claude" / "agents" / f"{run['agent']}.md", model)
    prompt = run["prompt"]
    missing, stale = [], []
    started = _epoch(run["started"])
    rebuild = sorted(set(re.findall(r"/diagram/\.clones/[\w-]+/\.git/review-snapshot/([\w.-]+)", prompt)))
    for unit in rebuild:  # a review snapshot is rebuilt at the case's commit (`snapshot`): later rounds overwrite it in place
        prompt = re.sub(rf"/diagram/\.clones/[\w-]+/\.git/review-snapshot/{re.escape(unit)}", str(tree / ".git" / "review-snapshot" / unit), prompt)
    for p in outside_paths(prompt):
        src = pathlib.Path(p)
        if not src.exists():
            missing.append(p)
            continue
        # A BUNDLE IS FROZEN INTO THE CASE: the builders rebuild `/tmp/l7r-check/<name>/` in place every round, so only a bundle
        # not written since the recorded run started is what that run read - copied here, so a later rebuild cannot move it
        root = src if src.is_dir() else src.parent
        newest = max((f.stat().st_mtime for f in root.rglob("*") if f.is_file()), default=root.stat().st_mtime)
        if newest > started:
            stale.append(p)
        dest = out / "inputs" / root.name
        if not dest.exists():
            shutil.copytree(root, dest) if root.is_dir() else shutil.copy2(root, dest)
        prompt = prompt.replace(str(root), str(dest))
    # the frozen inputs first, the checkout's paths after: a rewrite into the case's worktree (itself under /tmp) must not be
    # mistaken for an outside input
    prompt = re.sub(r"/diagram/\.clones/[\w-]+(?!/\.git/)", str(tree), prompt)
    prompt = re.sub(r"(?<![\w.-])/diagram(?=/(?:\.claude|specs|scripts|docs|research|l7r|pool|tests|dev)\b)", str(tree), prompt)
    (out / "prompt.txt").write_text(prompt, encoding="utf-8")
    (out / "recorded-reply.md").write_text(run["reply"], encoding="utf-8")
    (out / "meta.json").write_text(
        json.dumps({"agent": run["agent"], "recorded": str(transcript), "started": run["started"], "commit": commit, "model": model, "missing": missing, "stale": stale, "rebuild": rebuild}, indent=1),
        encoding="utf-8",
    )
    print(
        f"{run['agent']} @ {commit[:9]} ({run['started'][:16]}) -> {out}"
        + (f"\n  MISSING (not a fair re-run): {', '.join(missing)}" if missing else "")
        + (f"\n  CHANGED SINCE the run (not a fair re-run): {', '.join(stale)}" if stale else "")
    )
    return 1 if missing or stale else 0


SNAP_SUFFIXES = (".json", ".svg", ".png", ".html", ".notes.md")


def _render(tree: pathlib.Path, name: str) -> pathlib.Path | None:
    """Draw map or sheet `name` in a checkout (renders are not tracked); its folder, or None."""
    gens = sorted(tree.glob(f"pool/*/{name}/{name}.gen.py"))
    if not gens:
        return None
    subprocess.run(["make", "--no-print-directory", "map", f"GEN={gens[0].relative_to(tree)}"], cwd=tree, capture_output=True, check=False)
    return gens[0].parent


def read_back(transcript: pathlib.Path, suffix: str) -> str:
    """A file's text as the recorded agent read it whole (its Read result, line numbers stripped), or ""."""
    records = [json.loads(line) for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip().startswith("{")]
    ids = {
        b["id"]
        for r in records
        if r.get("type") == "assistant"
        for b in r["message"].get("content", [])
        if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Read" and str(b.get("input", {}).get("file_path", "")).endswith(suffix)
    }
    results = [
        b
        for r in records
        if r.get("type") == "user" and isinstance(r.get("message", {}).get("content"), list)
        for b in r["message"]["content"]
        if isinstance(b, dict) and b.get("type") == "tool_result"
    ]
    for b in results:
        if b.get("tool_use_id") in ids:
            body = text_of(b.get("content"))
            return "\n".join(re.sub(r"^\s*\d+\t", "", ln) for ln in body.splitlines()) + "\n"
    return ""


def read_dispatch(transcript: pathlib.Path, unit: str) -> str:
    """The dispatch prompt of `unit` as the recorded agent saw it: its Read, or any tool output holding the whole prompt
    (from its `UNIT:` line to its last instruction) - a `cat` serves as well as a Read."""
    text = read_back(transcript, f"/{unit}/dispatch.md")
    if text:
        return text
    for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
        if f"UNIT: {unit}" not in line or '"tool_result"' not in line:
            continue
        for r in [json.loads(line)]:
            for b in r.get("message", {}).get("content", []) if isinstance(r.get("message", {}).get("content"), list) else []:
                body = text_of(b.get("content")) if isinstance(b, dict) else ""
                i = body.find(f"UNIT: {unit}")
                j = body.find("as your last act, and quote the line it prints.", i)
                if i >= 0 and j > i:
                    return body[i : j + len("as your last act, and quote the line it prints.")] + "\n"
    return ""


def snapshot(out: pathlib.Path) -> int:
    """Rebuild each review snapshot the recorded run read: the map drawn at the case's commit (`clone/`) and at main's commit
    of the time (`main/`), and the dispatch prompt as the recorded agent read it."""
    meta = json.loads((out / "meta.json").read_text())
    tree = out / "tree"
    main_tree = out / "main-tree"
    # main's tip AT THE TIME, from the mirror's reflog: a commit's own date says when it was made, not when it landed
    main_commit = clone_head_at(CLONE.parent.parent, _epoch(meta["started"])) or meta["commit"]
    if not main_tree.is_dir():
        subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(CLONE), str(main_tree)], capture_output=True, check=True)
        subprocess.run(["git", "-C", str(main_tree), "checkout", "-q", "--detach", main_commit], capture_output=True, check=True)
    rc = 0
    for unit in meta.get("rebuild", []):
        name = unit.rsplit("--", 1)[-1]
        dest = tree / ".git" / "review-snapshot" / unit
        for side, checkout in (("clone", tree), ("main", main_tree)):
            folder = _render(checkout, name)
            if folder is None:
                print(f"{unit}: no {name} in the {side} checkout")
                rc = 1
                continue
            (dest / side).mkdir(parents=True, exist_ok=True)
            for f in folder.iterdir():
                if f.name.endswith(SNAP_SUFFIXES):
                    shutil.copy2(f, dest / side / f.name)
        text = read_dispatch(pathlib.Path(meta["recorded"]), unit)
        if text:
            (dest / "dispatch.md").write_text(re.sub(r"/diagram/\.clones/[\w-]+", str(tree), text), encoding="utf-8")
        print(f"{unit}: rebuilt at {meta['commit'][:9]} (main {main_commit[:9]}){'' if text else '; no dispatch.md read in the recorded run'}")
    return rc


def run_case(out: pathlib.Path, runs: int = 3) -> None:
    """Start each run as a headless session in the case's worktree, in the background; each writes run-<i>.json."""
    meta = json.loads((out / "meta.json").read_text())
    prompt = (out / "prompt.txt").read_text(encoding="utf-8")
    for i in range(1, runs + 1):
        log = out / f"run-{i}.json"
        cmd = [
            "claude", "-p", "--agent", meta["agent"], "--output-format", "json", "--permission-mode", "bypassPermissions",
            "--settings", json.dumps({"disableAllHooks": True}), prompt,
        ]  # fmt: skip
        with open(log, "w", encoding="utf-8") as fh:
            p = subprocess.Popen(cmd, cwd=out / "tree", stdout=fh, stderr=subprocess.STDOUT, start_new_session=True)
        (out / f"run-{i}.pid").write_text(f"{p.pid} {time.time():.0f}\n")
        print(f"started run {i}: pid {p.pid} -> {log}")


def run_all(root: pathlib.Path, runs: int = 3, parallel: int = 6) -> None:
    """Every prepared case under `root`, `runs` runs each, at most `parallel` sessions at once (each holds a few hundred MB);
    a run already finished (its run-<i>.json parses) is not started again."""
    queue = []
    for out in sorted(d for d in root.iterdir() if (d / "meta.json").is_file()):
        for i in range(1, runs + 1):
            try:
                json.loads((out / f"run-{i}.json").read_text(encoding="utf-8"))
            except OSError, ValueError:
                queue.append((out, i))
    live: list[subprocess.Popen] = []
    for out, i in queue:
        while len(live) >= parallel:
            live = [p for p in live if p.poll() is None]
            time.sleep(5)
        meta = json.loads((out / "meta.json").read_text())
        cmd = ["claude", "-p", "--agent", meta["agent"], "--output-format", "json", "--permission-mode", "bypassPermissions",
               "--settings", json.dumps({"disableAllHooks": True}), (out / "prompt.txt").read_text(encoding="utf-8")]  # fmt: skip
        fh = open(out / f"run-{i}.json", "w", encoding="utf-8")  # noqa: SIM115 - closed when the process ends
        live.append(subprocess.Popen(cmd, cwd=out / "tree", stdout=fh, stderr=subprocess.STDOUT))
        print(f"{time.strftime('%H:%M:%S')} started {out.name} run {i}", flush=True)
    for p in live:
        p.wait()
    print(f"{time.strftime('%H:%M:%S')} all {len(queue)} run(s) finished", flush=True)


def usage(out: pathlib.Path) -> None:
    meta = json.loads((out / "meta.json").read_text())
    rec = read(pathlib.Path(meta["recorded"]))
    sys.path.insert(0, str(CLONE / "scripts" / "reviews"))
    import agent_census  # noqa: PLC0415

    u = agent_census.fold_usage(rec["records"])
    print(f"recorded  model={u['model']} turns={u['turns']} in={u['fresh'] + u['cached']:,} out={u['output']:,}")
    for f in sorted(out.glob("run-*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            print(f"{f.stem}  not finished")
            continue
        uu = r.get("usage", {})
        tin = uu.get("input_tokens", 0) + uu.get("cache_read_input_tokens", 0) + uu.get("cache_creation_input_tokens", 0)
        print(
            f"{f.stem}  models={list((r.get('modelUsage') or {}).keys())} turns={r.get('num_turns')} in={tin:,} out={uu.get('output_tokens', 0):,} {r.get('duration_ms', 0) / 1000:.0f} s cost=${r.get('total_cost_usd', 0):.2f}"
        )
        (out / f"{f.stem}-reply.md").write_text(r.get("result", ""), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("catalog")
    c.add_argument("agent")
    c.add_argument("--since", default="")
    c.add_argument("--replayable", action="store_true", help="only runs whose outside inputs exist unchanged since they ran")
    p = sub.add_parser("prepare")
    p.add_argument("transcript")
    p.add_argument("out")
    p.add_argument("--model", default=SONNET)
    p.add_argument("--head", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("out")
    r.add_argument("--runs", type=int, default=3)
    sub.add_parser("usage").add_argument("out")
    ra = sub.add_parser("run-all")
    ra.add_argument("root")
    ra.add_argument("--runs", type=int, default=3)
    ra.add_argument("--parallel", type=int, default=6)
    sub.add_parser("snapshot").add_argument("out")
    a = ap.parse_args(argv)
    if a.cmd == "catalog":
        catalog(a.agent, a.since, a.replayable)
    elif a.cmd == "prepare":
        return prepare(pathlib.Path(a.transcript), pathlib.Path(a.out), a.model, a.head)
    elif a.cmd == "run-all":
        run_all(pathlib.Path(a.root), a.runs, a.parallel)
    elif a.cmd == "snapshot":
        return snapshot(pathlib.Path(a.out))
    elif a.cmd == "run":
        run_case(pathlib.Path(a.out), a.runs)
    else:
        usage(pathlib.Path(a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
