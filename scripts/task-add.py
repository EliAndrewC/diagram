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
    """One more than the highest id of the feature's own tasks - its boxes and its plan's `## T<n>` sections - zero-padded as its
    ids are. Never an id a title or a section merely QUOTES (feature 405 T31, D3): 405's moved titles name "(385 T147)", and
    reading every `T<n>` gave its new tasks T148 on."""
    text = "".join((d / n).read_text(encoding="utf-8") for n in ("tasks.md", "plan.md", "plan-done.md") if (d / n).is_file())
    ids = re.findall(r"^(?:\s*- \[[ xX]\]|##) T(\d+)[a-z]?\b", text, re.M)
    return f"T{max((int(n) for n in ids), default=0) + 1:02d}"


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


RED_EXIT = "Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`."
"""Checklist item 6's red exit (feature 426, D6): the wording T48's and T50's plan reviews each blocked a round on. Generic, never
one feature's: the first form copied feature 417's D35 ("FR-008 green ... placed correctly ... (D11, D35)"), and feature 427's
first plan review blocked on that text in a profiling tool's section (2026-10-26)."""

TEMPLATE = """### {T} (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### {T} Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. """ + RED_EXIT + """
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>
"""
"""The section `make task-add` writes when no `SECTION=` is given (feature 426, D6): the alone-off table and checklist item 6's red
exit already in place, the two things the plan reviews kept asking for."""


PERFORMANCE = """
### {T} Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** <the stage and the loop: `make perf-profile` time beside `make phase-calls` / `make perf-fanout` calls>
2. **Removes work, or only moves it?** <fewer candidates, a screen, a kept result, an index, an early stop, a better algorithm,
   a loop into C - or an inlining, a merge, a builtin written out: never the goal, only where the time evidence shows a gain>
3. **What do you expect it to save, and why?** <a share of the stage's profiled time>
4. **How does the work grow with the settlement?** <the growth exponent between sizes, and whether this bends it>
5. **What did the before and after show, and under what conditions?** <calls; `make perf-ab` best of N with each arm's spread,
   the host's load - evidence, not a pass>
6. **Did any map move, and does it still keep the research?** <`make maps-moved`, the cohort>
"""
"""What `make task-add ... PERF=1` appends to a performance task's section (feature 435, D2; the GM 2026-10-27: the checklist
helps "us not forget steps as we work towards our goal, rather than the checklist items being taken as if they are themselves
the goal")."""


def lacks_red_exit(section: str) -> bool:
    """A section whose checklist item 6 does not route a red result through `make arbiter-ask`."""
    item6 = next((ln for ln in section.splitlines() if ln.lstrip().startswith("6.")), "")
    return "make arbiter-ask" not in item6


def main(argv: list[str]) -> int:
    physical = "--physical" in argv
    performance = "--performance" in argv
    args = [a for a in argv if a not in ("--physical", "--performance")]
    section = ""
    if "--section" in args:
        i = args.index("--section")
        section, args = args[i + 1] if i + 1 < len(args) else "", args[:i] + args[i + 2 :]
    title = os.environ.get("TASK_TITLE", "").strip()
    if len(args) != 1 or not title:
        print('usage: make task-add F=<feature> TITLE="<what the task does>" [SECTION=<file with {T}>] [RESEARCH=physical] [PERF=1]', file=sys.stderr)
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
    text = (Path(section).read_text(encoding="utf-8") if section else TEMPLATE) + (PERFORMANCE if performance else "")
    if section and lacks_red_exit(text):
        print(f"task-add: SECTION={section}'s checklist item 6 has no red exit through `make arbiter-ask` - the plan review will ask for: {RED_EXIT}", file=sys.stderr)
    tid = next_id(d)
    # NO LANDS-OPEN MARK OR LINE (feature 405 T32, D4; the GM 2026-10-20): a task nobody has started holds no landing, so a task
    # filed mid-feature needs neither - the mark and the `**Lands open**:` line that T69 (plan D88) wrote here are retired.
    (d / "tasks.md").write_text(add_box((d / "tasks.md").read_text(encoding="utf-8"), tid, title, physical), encoding="utf-8")
    plan = (d / "plan.md").read_text(encoding="utf-8") if (d / "plan.md").is_file() else ""
    (d / "plan.md").write_text(add_section(plan, tid, text), encoding="utf-8")
    print(f"task-add: {tid} filed in {(d / 'tasks.md').relative_to(root)}, its section in {(d / 'plan.md').relative_to(root)}" + ("" if section else " (the template: fill each <...>)"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
