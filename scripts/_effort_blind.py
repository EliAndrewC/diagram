#!/usr/bin/env python3
"""Blind one task's two outputs for grading (feature 293, spec FR-009, contracts/cli.md `make effort-blind`).

Each valid run's output is exported from its clone - task R: every research file the run added or changed (the question's
fragment, its notes, new sources and glossary words); task I: the diff since the start commit, the moved maps' pictures and
design notes, and the run's last `make done` summary - with the arm-identifying text removed, labeled A and B in an order
drawn from the seed, and written to a bundle OUTSIDE the repository beside the rubric. The key goes under `.git/effort-keys/`
of the session's clone, which no bundle includes; it is committed to the feature directory only after both grades are in.

WHAT IS STRIPPED is what identifies the ARM or the RUN: the run id, the clone path and name, the session ids, commit trailers,
the token `xhigh`, and an arm name where it names an effort setting (`--effort medium`, `effort: xhigh`). The word `medium`
in ordinary prose is left: both outputs may use it, it identifies nothing, and removing it would damage what is graded.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import random
import re
import shutil
import subprocess
import sys

FEATURE = "293-effort-level-experiment"
RUBRIC = {"R": "rubrics/research.md", "I": "rubrics/implementation.md"}
LEVEL = r"(?:medium|xhigh|high|low|max)"
EFFORT_SETTING = re.compile(rf"(--effort|\beffort(?:[ _-]?level)?\"?)\s*[:=]?\s*\"?{LEVEL}\b\"?|\b{LEVEL}[ -]effort\b", re.I)
XHIGH = re.compile(r"\bxhigh\b", re.I)
TRAILER = re.compile(r"^\s*Co-Authored-By:.*$", re.M | re.I)


def strip(text: str, run: dict, sids: list[str]) -> str:
    out = text.replace(run["clone"], "<clone>").replace(pathlib.Path(run["clone"]).name, "<clone>")
    for s in sids:
        out = out.replace(s, "<session>")
    out = re.sub(rf"\b{re.escape(run['run_id'])}\b", "<run>", out)
    out = EFFORT_SETTING.sub(lambda m: f"{m.group(1)} <arm>" if m.group(1) else "<arm> effort", out)
    out = XHIGH.sub("<arm>", out)
    return TRAILER.sub("", out)


def git(clone: str, *args: str) -> str:
    return subprocess.run(["git", "-C", clone, *args], capture_output=True, text=True, check=True).stdout


def changed(run: dict) -> list[str]:
    return git(run["clone"], "diff", "--name-only", "--diff-filter=AM", run["start_commit"], "HEAD").splitlines()


def export(run: dict, task: str, dest: pathlib.Path, sids: list[str], done_summary: str) -> list[str]:
    """Write one run's output under `dest`; return the files written, relative to it."""
    dest.mkdir(parents=True)
    written = []
    clone = pathlib.Path(run["clone"])
    files = changed(run)
    if task == "R":
        keep = [f for f in files if "/research/" in "/" + f]
    else:
        diff = git(run["clone"], "diff", run["start_commit"], "HEAD", "--", ".", ":(exclude)*.png")
        (dest / "changes.diff").write_text(strip(diff, run, sids), encoding="utf-8")
        (dest / "make-done.txt").write_text(strip(done_summary or "no make done output found", run, sids), encoding="utf-8")
        written += ["changes.diff", "make-done.txt"]
        keep = [f for f in files if f.startswith("pool/") or "/pool/" in f if f.endswith((".png", ".notes.md"))]
    for f in keep:
        target = dest / "files" / f
        target.parent.mkdir(parents=True, exist_ok=True)
        if f.endswith(".png"):
            shutil.copyfile(clone / f, target)
        else:
            target.write_text(strip((clone / f).read_text(encoding="utf-8", errors="replace"), run, sids), encoding="utf-8")
        written.append(f"files/{f}")
    return written


def last_done_summary(transcripts: list[pathlib.Path]) -> str:
    """The output of the last `make done` any of the run's sessions ran, from its transcript."""
    last = ""
    for t in transcripts:
        uses: dict[str, str] = {}
        for line in t.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            content = (r.get("message") or {}).get("content")
            for b in content if isinstance(content, list) else []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use" and "make done" in str((b.get("input") or {}).get("command") or ""):
                    uses[str(b.get("id"))] = ""
                elif b.get("type") == "tool_result" and str(b.get("tool_use_id")) in uses:
                    c = b.get("content")
                    last = c if isinstance(c, str) else json.dumps(c)
    return last[-4000:]


def blind(repo: pathlib.Path, task: str, seed: int, out: pathlib.Path, projects: pathlib.Path) -> tuple[pathlib.Path, dict]:
    fdir = repo / "specs" / FEATURE
    runs = [json.loads(p.read_text()) for p in sorted((fdir / "runs").glob("*.json"))]
    runs = [r for r in runs if r["task"] == task and r.get("status") == "valid"]
    if len(runs) != 2:
        raise SystemExit(f"effort-blind: task {task} has {len(runs)} valid runs, not 2")
    order = list(runs)
    random.Random(seed).shuffle(order)
    bundle = out / task
    if bundle.exists():
        shutil.rmtree(bundle)
    lines = [f"# Blinded pair - task {task}", "", "Grade A and B against `rubric.md` in this directory. Read nothing outside it.", ""]
    for label, run in zip("AB", order, strict=True):
        project = projects / run["clone"].replace("/", "-").replace(".", "-")
        transcripts = sorted(project.glob("*.jsonl")) if project.is_dir() else []
        sids = [t.stem for t in transcripts]
        files = export(run, task, bundle / label, sids, last_done_summary(transcripts) if task == "I" else "")
        lines += [f"## {label}", "", *(f"- `{label}/{f}`" for f in files), ""]
    shutil.copyfile(fdir / RUBRIC[task], bundle / "rubric.md")
    (bundle / "MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")
    key = {"A": order[0]["run_id"], "B": order[1]["run_id"], "seed": seed}
    keys = repo / ".git" / "effort-keys"
    keys.mkdir(parents=True, exist_ok=True)
    (keys / f"{task}.json").write_text(json.dumps(key) + "\n", encoding="utf-8")
    return bundle, key


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="effort-blind")
    ap.add_argument("--task", required=True, choices=("R", "I"))
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", default="/tmp/effort-blind-293")
    ap.add_argument("--projects", default=str(pathlib.Path.home() / ".claude" / "projects"))
    args = ap.parse_args(argv)
    repo = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                                       check=True).stdout.strip())
    bundle, _ = blind(repo, args.task, args.seed, pathlib.Path(args.out), pathlib.Path(args.projects))
    print(bundle / "MANIFEST.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
