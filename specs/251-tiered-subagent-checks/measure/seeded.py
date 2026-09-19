#!/usr/bin/env python3
"""The seeded-fault runs of feature 251 (FR-011): re-run a RECORDED check under its new tier.

A past run's transcript holds everything a fair re-run needs: the prompt the session sent, the reply the
Opus agent gave (the recorded result, with its findings) and the moment it ran. `catalog` lists past runs
of one agent with a signature of each reply, so artifacts with KNOWN findings and known-clean ones can be
picked. `prepare` builds the re-run: a detached worktree of this clone at the last commit before the
recorded run (so the agent reads the files the recorded agent read), with the CURRENT agent files copied
in (so the tier under test is the new one), and the prompt with the old clone's paths rewritten to the
worktree. It prints the command; the run itself is a headless session started in that worktree
(`claude -p --agent <name>`), because this session's Agent tool loads the mirror's agent files and has no
effort parameter (research R4). `usage` folds a finished run's own transcript with the census's rule.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve()
CLONE = HERE.parents[3]
PROJECTS = pathlib.Path.home() / ".claude" / "projects"
SIGNALS = ("CONTRADICTED", "DRIFTED", "IN-STEP", "CANNOT-TELL", "DIFFERS", "NOT-ON-PAGE", "NOT-READABLE", "DOES-NOT-SUPPORT", "PARTIAL", "SESSION NOTE", "HISTORY", "VOCABULARY", "CHANGES REQUIRED", "FAITHFUL", "CUT", "KEEP")


def _census():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_agent_census", CLONE / "scripts" / "_agent_census.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _text(content: object) -> str:
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


def read(transcript: pathlib.Path) -> dict:
    records = [json.loads(line) for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip().startswith("{")]
    prompt = next((_text(r["message"]["content"]) for r in records if r.get("type") == "user"), "")
    reply = next((_text(r["message"]["content"]) for r in reversed(records) if r.get("type") == "assistant" and _text(r["message"].get("content"))), "")
    meta_path = transcript.with_suffix("").with_suffix(".meta.json")
    meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
    return {"agent": meta.get("agentType", ""), "prompt": prompt, "reply": reply, "started": records[0].get("timestamp", "") if records else "", "cwd": records[0].get("cwd", "") if records else ""}


def catalog(agent: str) -> None:
    for t in sorted(PROJECTS.glob("-diagram*/*/subagents/agent-*.jsonl")):
        run = read(t)
        if run["agent"] != agent or not run["reply"]:
            continue
        sig = " ".join(f"{s}={n}" for s in SIGNALS if (n := len(re.findall(rf"\b{re.escape(s)}\b", run["reply"]))))
        print(f"{run['started'][:16]}  {t.parent.parent.name[:8]}/{t.stem[-8:]}  prompt={len(run['prompt']):>6}  reply={len(run['reply']):>6}  {sig}\n      {' '.join(run['prompt'].split())[:170]}")


def prepare(transcript: pathlib.Path, out: pathlib.Path, at_head: bool = False) -> None:
    """`at_head`: the recorded run read ANOTHER clone's unlanded work, which this clone's history only holds later."""
    run = read(transcript)
    out.mkdir(parents=True, exist_ok=True)
    rev = ["rev-parse", "HEAD"] if at_head else ["rev-list", "-1", f"--before={run['started']}", "HEAD"]
    commit = subprocess.run(["git", "-C", str(CLONE), *rev], capture_output=True, text=True, check=True).stdout.strip()
    tree = out / "tree"
    if not tree.is_dir():
        subprocess.run(["git", "-C", str(CLONE), "worktree", "add", "--detach", str(tree), commit], capture_output=True, text=True, check=True)
    shutil.copytree(CLONE / ".claude" / "agents", tree / ".claude" / "agents", dirs_exist_ok=True)
    prompt = re.sub(r"/diagram/\.clones/[\w-]+", str(tree), run["prompt"])
    prompt = re.sub(r"(?<![\w.-])/diagram(?=/(?:\.claude|specs|scripts|docs)\b)", str(tree), prompt)
    (out / "prompt.txt").write_text(prompt, encoding="utf-8")
    (out / "recorded-reply.md").write_text(run["reply"], encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({"agent": run["agent"], "recorded": str(transcript), "started": run["started"], "commit": commit}, indent=1), encoding="utf-8")
    print(f"{run['agent']} @ {commit[:9]} ({run['started'][:16]}) -> {out}")


def usage(project_glob: str) -> None:
    ac = _census()
    for t in sorted(PROJECTS.glob(project_glob)):
        records = [json.loads(line) for line in t.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip().startswith("{")]
        u = ac.fold_usage(records)
        print(f"{t.parent.name[-40:]}/{t.stem[:8]}  model={u['model']}  turns={u['turns']}  in={u['fresh'] + u['cached']:,}  out={u['output']:,}  thinking={u['thinking']:,}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("catalog").add_argument("agent")
    p = sub.add_parser("prepare")
    p.add_argument("transcript")
    p.add_argument("out")
    p.add_argument("--head", action="store_true")
    sub.add_parser("usage").add_argument("glob")
    a = ap.parse_args()
    if a.cmd == "catalog":
        catalog(a.agent)
    elif a.cmd == "prepare":
        prepare(pathlib.Path(a.transcript), pathlib.Path(a.out), a.head)
    else:
        usage(a.glob)
    sys.exit(0)
