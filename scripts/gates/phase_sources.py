#!/usr/bin/env python3
"""The old code of a stage being rebuilt, held off-limits while its task runs (feature 444, the GM 2026-10-30).

WHY (the GM, 2026-10-30): "a big part of the goal for the rewrite is that we are not trying to re-implement the same algorithms,
because the old algorithms were computationally inefficient ... My biggest fear with this ... is that ... you would just end up
re-implementing the same bad algorithms." A phase task (a `tasks.md` block carrying `phase: <stage>`) rebuilds its stage in Rust
from the stage's greenfield derivation (feature 444 FR-015, FR-017); nothing stopped the session writing it from reading today's
Python as it wrote. So `make task-start` on such a task records the stage's old modules here, and `phase-source-hooks.sh` refuses
a read of them until the task is ticked; `make phase-read FILE= WHY=` lets one file be read for ten minutes, the reason logged.

THE OLD CODE: the module defining `stage_<phase>` (its subpackage's siblings with it, `work_budget_bundle.stage_files`), every
module defining a function the stage's counters name in the newest `make work-budget` run (`counted_files` - where its work
is), and any path or glob the task block names on an `old-code:` line.

    phase_sources.py allow <file> <why>     `make phase-read`
"""

from __future__ import annotations

import datetime
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
for d in (HERE, HERE.parent / "reviews"):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))

STATE = "phase-sources.json"  # in the git common directory, beside `active-task`
ALLOW_MINUTES = 10


def common_dir(root: pathlib.Path) -> pathlib.Path:
    out = subprocess.run(["git", "-C", str(root), "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True)
    return pathlib.Path(out.stdout.strip())


def phase_of(block: str) -> tuple[str, list[str]]:
    """The task block's `phase:` stage ('' for none) and its `old-code:` paths or globs."""
    m = re.search(r"^\s*phase:\s*(\w+)\s*$", block, re.M)
    extra = [g for line in re.findall(r"^\s*old-code:\s*(.+)$", block, re.M) for g in line.split()]
    return (m.group(1) if m else ""), extra


def sources(root: pathlib.Path, phase: str, extra: list[str]) -> list[str]:
    """The stage's old modules, relative to `root`."""
    import work_budget_bundle as wb  # noqa: PLC0415

    # THE OLD CODE IS THE PYTHON: `stage_files` also names a Rust phase's `.rs` source (the audit bundle reads it), which is the
    # very code the task writes and must stay readable
    files = [p for p in wb.stage_files(root, phase) if p.suffix == ".py"]
    runs = sorted((root / wb.RUNS).glob("*.json"))
    if runs:
        run = json.loads(runs[-1].read_text(encoding="utf-8"))
        counts = [r["stages"][phase] for r in run["rows"] if phase in r["stages"]]
        files += [p for p in wb.counted_files(root, counts) if p not in files]
    for g in extra:
        files += [p for p in sorted(root.glob(g)) if p.is_file() and p not in files]
    return sorted({str(p.relative_to(root)) for p in files})


def record(root: pathlib.Path, feature: str, task: str, block: str) -> str:
    """Write the state for a phase task, or clear it for any other; the line `make task-start` prints ('' when none)."""
    path = common_dir(root) / STATE
    phase, extra = phase_of(block)
    if not phase:
        path.unlink(missing_ok=True)
        return ""
    files = sources(root, phase, extra)
    path.write_text(json.dumps({"feature": feature, "task": task, "phase": phase, "files": files, "allow": []}, indent=1) + "\n", encoding="utf-8")
    return (
        f"phase-sources: {task} rebuilds `{phase}` from its derivation - {len(files)} file(s) of its old code are not read until it is "
        f"ticked (`make phase-read FILE= WHY=` for one, ten minutes)"
    )


def allow(root: pathlib.Path, file: str, why: str, now: datetime.datetime | None = None) -> int:
    path = common_dir(root) / STATE
    if not path.is_file():
        print("phase-read: no phase task is started - nothing is held", file=sys.stderr)
        return 2
    if len(why.split()) < 2:
        print('phase-read: WHY="<two words or more>" is required - the reason is what the log keeps', file=sys.stderr)
        return 2
    state = json.loads(path.read_text(encoding="utf-8"))
    rel = str(pathlib.Path(file).resolve().relative_to(root.resolve())) if pathlib.Path(file).is_absolute() else file
    if rel not in state["files"]:
        print(f"phase-read: {rel} is not one of {state['phase']}'s held files - read it as usual", file=sys.stderr)
        return 2
    until = (now or datetime.datetime.now(datetime.UTC)) + datetime.timedelta(minutes=ALLOW_MINUTES)
    state["allow"].append({"file": rel, "until": until.strftime("%Y-%m-%dT%H:%M:%SZ"), "why": why})
    path.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8")
    print(f"phase-read: {rel} may be read until {until:%H:%M} UTC - {why}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    root = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip())
    if len(args) == 3 and args[0] == "allow":
        return allow(root, args[1], args[2])
    print("usage: phase_sources.py allow <file> <why>", file=sys.stderr)
    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.path.insert(0, str(HERE.parent / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    sys.exit(usage_log.exited("phase_sources", main()))
