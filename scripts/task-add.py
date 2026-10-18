#!/usr/bin/env python3
"""`make task-add` - file a task box, and its plan section, with the next free id (feature 385 T64, plan D83).

WHY. The GM, 2026-10-18: inserting a task "somewhere in the middle of the task list ... sounds like something that could
potentially eat up a lot of tokens if we are doing it by hand. And hence why it should get tooling." Tasks T41-T64 were each
added by a hand-written insertion script of 1-2k tokens, and two hand-picked ids (T47, T48) collided with an umbrella heading.

THE ID is one more than the highest `T<n>` named anywhere in the feature's tasks.md, plan.md and plan-done.md, so an id named
only in a heading is never reused. THE BOX goes before the GM-review box (as `claims-carry` places its boxes), else at the end,
with its research line. THE SECTION, given, is a file whose text has `{T}` for the id; it goes into plan.md before the feature's
`## T<n> - the close` heading, else at the end. The id is printed.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PHYSICAL = "      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited\n"


def _tick():  # noqa: ANN202 - tick-task.py's feature resolution, the one copy
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("tick_task", HERE / "tick-task.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def next_id(d: Path) -> str:
    """One more than the highest task id the feature names, zero-padded as its ids are."""
    text = "".join((d / n).read_text(encoding="utf-8") for n in ("tasks.md", "plan.md", "plan-done.md") if (d / n).is_file())
    return f"T{max((int(n) for n in re.findall(r'\bT(\d+)[a-z]?\b', text)), default=0) + 1:02d}"


def add_box(tasks: str, tid: str, title: str, physical: bool) -> str:
    box = f"- [ ] {tid} {title}\n      research: {'physical' if physical else 'rendering'}\n" + (PHYSICAL if physical else "")
    gm = re.search(r"^- \[[ x]\] GM review\b", tasks, re.M)
    if gm:
        return tasks[: gm.start()] + box + tasks[gm.start() :]
    return tasks + ("" if tasks.endswith("\n") else "\n") + box


def add_section(plan: str, tid: str, section: str) -> str:
    body = section.replace("{T}", tid).rstrip("\n") + "\n\n"
    close = re.search(r"^## T\d+ - the close\b", plan, re.M)
    if close:
        return plan[: close.start()] + body + plan[close.start() :]
    return plan + ("" if plan.endswith("\n") else "\n") + "\n" + body


def main(argv: list[str]) -> int:
    physical = "--physical" in argv
    args = [a for a in argv if a != "--physical"]
    section = ""
    if "--section" in args:
        i = args.index("--section")
        section, args = args[i + 1] if i + 1 < len(args) else "", args[:i] + args[i + 2 :]
    title = os.environ.get("TASK_TITLE", "").strip()
    if len(args) != 1 or not title:
        print('usage: make task-add F=<feature> TITLE="<what the task does>" [SECTION=<file with {T}>] [RESEARCH=physical]', file=sys.stderr)
        return 2
    tick = _tick()
    root = tick.repo_root()
    d = tick.spec_dir(root, args[0])
    if d is None or not (d / "tasks.md").is_file():
        print(f"task-add: no single specs/{args[0]}* directory with a tasks.md under {root}", file=sys.stderr)
        return 2
    if section and not Path(section).is_file():
        print(f"task-add: SECTION={section} is not a file", file=sys.stderr)
        return 2
    tid = next_id(d)
    (d / "tasks.md").write_text(add_box((d / "tasks.md").read_text(encoding="utf-8"), tid, title, physical), encoding="utf-8")
    if section:
        plan = (d / "plan.md").read_text(encoding="utf-8") if (d / "plan.md").is_file() else ""
        (d / "plan.md").write_text(add_section(plan, tid, Path(section).read_text(encoding="utf-8")), encoding="utf-8")
    print(f"task-add: {tid} filed in {(d / 'tasks.md').relative_to(root)}" + (f", its section in {(d / 'plan.md').relative_to(root)}" if section else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
