#!/usr/bin/env python3
"""`make task-start` (feature 449 T066, from `plan_gate.py`; `ask:449-T066-scope`): the task's mark, its start logged, and its feature named
in `.specify/feature.json`. In Python with what it reads (`plan_hold.py`'s `speckit-todo`, `phase_sources.py`'s `work_budget_bundle`) until
phase 3 ports them; what it needs of the plan gate goes through the door."""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "gates")]
import plan_door  # noqa: E402


def task_start(feature: str, task: str) -> int:
    root = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False).stdout.strip())
    d = plan_door.resolve(feature, root)
    if d is None:
        print(f"task-start: no single specs/{feature}* directory", file=sys.stderr)
        return 2
    # ...NOT A HELD FEATURE'S TASK (feature 417 T02, plan D4/D9): the hold is asked where a task becomes active
    import plan_hold  # noqa: PLC0415

    plan = d / "plan.md"
    section = plan_door.task_sections(plan.read_text(encoding="utf-8")).get(task) if plan.is_file() else None
    if why := plan_hold.refusal(d, task, section, os.environ.get("HOLD_OK", "")):
        print(why, file=sys.stderr)
        return 2
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True, check=False).stdout.strip()
    pathlib.Path(common, "active-task").write_text(json.dumps({"feature": d.name, "task": task}) + "\n", encoding="utf-8")
    # ...AND THE FEATURE NAMED where `active_task` reads it (405 T106): a mark naming another feature than `.specify/feature.json`
    # is ignored, so a session that started 405's task with 415 still named there had the cohort and `claims-carry` charge 405's work to 415
    (d.parent.parent / ".specify").mkdir(exist_ok=True)
    (d.parent.parent / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": f"specs/{d.name}"}, indent=2) + "\n", encoding="utf-8")
    # ...AND WHEN, for the report's per-task split (feature 385 T02, plan D10)
    with pathlib.Path(common, "task-starts.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"feature": d.name, "task": task, "utc": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")}) + "\n")
    print(f"task-start: {d.name} {task} is the active task - its checks need its decisions ruled first (make decide)")
    # ...AND A PHASE TASK'S OLD CODE HELD (feature 444, the GM 2026-10-30): its stage is rebuilt from its derivation, never read
    # from today's Python - `phase_sources.py`, read by `rust/guard's phase_source_hooks`; any other task clears the hold
    import phase_sources  # noqa: PLC0415

    tasks = (d / "tasks.md").read_text(encoding="utf-8") if (d / "tasks.md").is_file() else ""
    m = re.search(rf"^- \[[ x]\] {re.escape(task)}\b.*?(?=^- \[|\Z)", tasks, re.M | re.S)
    if line := phase_sources.record(d.parent.parent, d.name, task, m.group(0) if m else ""):
        print(line)
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: task_start.py <feature> <task>", file=sys.stderr)
        return 2
    return task_start(argv[0], argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
