#!/usr/bin/env python3
"""`make speckit-todo` - every spec-kit feature not yet closed, by state (feature 330).

The GM, 2026-10-08: *"we then need some way to mechanically easily see what spec kit features are open"* - once
the old future-work directory was retired, open work lives in `specs/` only, and this is how anyone finds it.

THE STATE RULE (plan D1). A feature is CLOSED when its `tasks.md` holds at least one task and no open one, or when
its spec's `**Status**:` value begins with one of `CLOSING`. Otherwise it is OPEN: FILED (no tasks yet), PLANNED
(tasks, none ticked) or IN PROGRESS (some ticked). A task is a box at column 0 - the form `make tick` writes and
`scripts/gates/plan_gate.py` counts; an indented box is part of its task. `Implemented` closes nothing: features say
it while holding open tasks, so only the tasks or a closing word decide. A checkbox form this does not read leaves the
feature OPEN - a parsing miss shows as open work, never as finished work.

THE STAGE (the GM, 2026-10-10). Every open feature says when it is owed in an `**Owed at**:` line under its status:
`now`, or the tier conversion that needs it - hamlets are scripted first, then villages, towns, provincial cities and
capitals - and a thing two tiers need is owed at the EARLIER one (*"If something will be required for both towns and
cities, then it is owed at the towns stage"*). The report groups each state by stage; `--check` refuses an open feature
without one, because a label typed into some titles and not others is what this replaced.

    speckit-todo.py [--root <repo>] [--all]     --all adds the closed features and why each is closed
    speckit-todo.py [--root <repo>] --check     exit 1, with the line to add, when an open feature has no valid stage
    speckit-todo.py --state <specs/NNN-slug>     one feature's state
    speckit-todo.py --closed-by-status <dir>     `yes` when the spec's status line closes it (CLOSING), else `no` - the
                                                 push's in-progress refusal keeps its own open-box test and asks only this
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

#: what a `**Status**:` value begins with when a feature is closed without every task ticked (plan D1, D3)
CLOSING = ("done", "superseded by", "withdrawn")
STATES = ("filed", "planned", "in progress")
#: when an open feature is owed, in the order the work reaches it (the GM, 2026-10-10)
STAGES = ("now", "village", "town", "provincial city", "capital")

_TASK = re.compile(r"^- \[( |x|X)\] ", re.M)
_STATUS = re.compile(r"^\*\*Status\*\*:?\s*(.+)$|^\*\*Status:\*\*\s*(.+)$", re.M)
_OWED = re.compile(r"^\*\*Owed at\*\*:?\s*(.+)$|^\*\*Owed at:\*\*\s*(.+)$", re.M)
_TITLE = re.compile(r"^#\s+(?:Feature(?: Specification)?\s*(?:\d+)?\s*[:-]\s*)?(.+)$", re.M)


@dataclass(frozen=True)
class Feature:
    name: str
    title: str
    state: str
    ticked: int
    total: int
    no_spec: bool
    why: str
    owed: str = ""


def owed_at(text: str) -> str:
    """The stage an `**Owed at**:` line names, or `""` when there is none or it names no stage (a note may follow)."""
    m = _OWED.search(text)
    value = (m.group(1) or m.group(2)).strip().lower() if m else ""
    return next((st for st in STAGES if value == st or value.startswith((st + " ", st + " -", st + ","))), "")


def feature(d: Path) -> Feature:
    """One feature directory's state, from its own files."""
    spec = d / "spec.md"
    text = spec.read_text(errors="replace") if spec.is_file() else ""
    m = _TITLE.search(text)
    title = m.group(1).strip() if m else d.name.split("-", 1)[-1]
    s = _STATUS.search(text)
    status = (s.group(1) or s.group(2)).strip() if s else ""
    tasks = d / "tasks.md"
    boxes = _TASK.findall(tasks.read_text(errors="replace")) if tasks.is_file() else []
    ticked = sum(b in "xX" for b in boxes)
    total = len(boxes)
    if status.lower().startswith(CLOSING):
        state, why = "closed", status
    elif total and ticked == total:
        state, why = "closed", "every task ticked"
    elif total == 0:
        state, why = "filed", ""
    else:
        state, why = ("planned" if ticked == 0 else "in progress"), ""
    return Feature(d.name, title, state, ticked, total, not spec.is_file(), why, owed_at(text))


def closed_by_status(d: Path) -> bool:
    """Does the spec's `**Status**:` line open with one of `CLOSING`? Only the line - no task is read."""
    spec = d / "spec.md"
    s = _STATUS.search(spec.read_text(errors="replace")) if spec.is_file() else None
    return bool(s) and (s.group(1) or s.group(2)).strip().lower().startswith(CLOSING)


def features(specs: Path) -> list[Feature]:
    """Every feature directory; a tree with no `specs/` has none (the push runs `--check` in any repository)."""
    return [feature(d) for d in sorted(specs.iterdir()) if d.is_dir()] if specs.is_dir() else []


def _line(f: Feature, extra: str = "") -> str:
    parts = [f.name, f.title]
    if f.total and f.state != "closed":
        parts.append(f"{f.ticked}/{f.total}")
    if f.no_spec:
        parts.append("(no spec.md)")
    if extra:
        parts.append(extra)
    return "  " + "  ".join(parts)


def report(specs: Path, show_closed: bool = False) -> str:
    fs = features(specs)
    out: list[str] = []
    for state in STATES:
        group = [f for f in fs if f.state == state]
        out.append(f"{state.upper()} ({len(group)})")
        for stage in (*STAGES, ""):
            staged = [f for f in group if f.owed == stage]
            if staged:
                out.append(f"  owed at {stage or 'NO STAGE (make speckit-todo CHECK=1 says how to set it)'} ({len(staged)})")
                out.extend("  " + _line(f) for f in staged)
        out.append("")
    closed = [f for f in fs if f.state == "closed"]
    if show_closed:
        out.append(f"CLOSED ({len(closed)})")
        out.extend(_line(f, f.why) for f in closed)
        out.append("")
    n = {s: sum(f.state == s for f in fs) for s in STATES}
    out.append(f"open: {n['filed']} filed, {n['planned']} planned, {n['in progress']} in progress; closed: {len(closed)}")
    return "\n".join(out) + "\n"


def unstaged(specs: Path) -> list[Feature]:
    """The open features whose spec names no stage."""
    return [f for f in features(specs) if f.state != "closed" and not f.owed]


def check_message(missing: list[Feature]) -> str:
    """The refusal, with the line to add - empty when nothing is missing."""
    if not missing:
        return ""
    names = "\n".join(f"  specs/{f.name}/spec.md" + ("  (no spec.md - write one first)" if f.no_spec else "") for f in missing)
    return (
        f"speckit-todo: {len(missing)} open feature(s) say not when they are owed:\n{names}\n"
        "Add this line under the **Status** line, naming ONE stage:\n"
        "  **Owed at**: now | village | town | provincial city | capital\n"
        "`now` unless it concerns a tier not yet scripted (its code, its maps or its generator - a city-only fold is `provincial city`); a thing two tiers need is owed at the earlier one "
        "(hamlets, then villages, towns, provincial cities, capitals - the GM, 2026-10-10).\n"
    )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="list the spec-kit features not yet closed")
    ap.add_argument("--root", default=".", help="the repository root (default: the current directory)")
    ap.add_argument("--all", action="store_true", help="also list the closed features and why")
    ap.add_argument("--check", action="store_true", help="exit 1 when an open feature names no stage")
    ap.add_argument("--state", metavar="DIR", help="print one feature directory's state and nothing else")
    ap.add_argument("--closed-by-status", metavar="DIR", help="print yes when the spec's status line closes it, else no")
    args = ap.parse_args(argv)
    if args.closed_by_status:
        sys.stdout.write(("yes" if closed_by_status(Path(args.closed_by_status)) else "no") + "\n")
        return 0
    if args.check:
        msg = check_message(unstaged(Path(args.root) / "specs"))
        sys.stderr.write(msg)
        return 1 if msg else 0
    if args.state:
        sys.stdout.write(feature(Path(args.state)).state + "\n")
        return 0
    sys.stdout.write(report(Path(args.root) / "specs", show_closed=args.all))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
