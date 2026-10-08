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

    speckit-todo.py [--root <repo>] [--all]     --all adds the closed features and why each is closed
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

_TASK = re.compile(r"^- \[( |x|X)\] ", re.M)
_STATUS = re.compile(r"^\*\*Status\*\*:?\s*(.+)$|^\*\*Status:\*\*\s*(.+)$", re.M)
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
    return Feature(d.name, title, state, ticked, total, not spec.is_file(), why)


def features(specs: Path) -> list[Feature]:
    return [feature(d) for d in sorted(specs.iterdir()) if d.is_dir()]


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
        out.extend(_line(f) for f in group)
        out.append("")
    closed = [f for f in fs if f.state == "closed"]
    if show_closed:
        out.append(f"CLOSED ({len(closed)})")
        out.extend(_line(f, f.why) for f in closed)
        out.append("")
    n = {s: sum(f.state == s for f in fs) for s in STATES}
    out.append(f"open: {n['filed']} filed, {n['planned']} planned, {n['in progress']} in progress; closed: {len(closed)}")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="list the spec-kit features not yet closed")
    ap.add_argument("--root", default=".", help="the repository root (default: the current directory)")
    ap.add_argument("--all", action="store_true", help="also list the closed features and why")
    args = ap.parse_args(argv)
    sys.stdout.write(report(Path(args.root) / "specs", show_closed=args.all))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
