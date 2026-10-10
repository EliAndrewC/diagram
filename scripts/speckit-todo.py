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

WHAT IT AFFECTS, AND THE STAGE FROM THAT (the GM, 2026-10-10). Every open feature names what it affects in an
`**Affects**:` line under its status - comma-separated tags from `.specify/affects.json`: the kinds of diagram (the
five settlement tiers, the magistracy and country shrine sheets) and the kinds of work that are no diagram (tooling,
performance, the research record, ...). The stage it is owed at is DERIVED: hamlets are scripted first, then villages,
towns, provincial cities and capitals, and a feature is owed at the earliest stage among its tags - `now` when any
tag is live today (*"If something will be required for both towns and cities, then it is owed at the towns stage"*;
a farmhouse change touches every tier, so it is owed now). An `**Owed at**:` line with a reason overrides the derived
stage where it is wrong. The report groups each state by stage, or by tag with `--by-affects`; `--check` refuses an
open feature with no tag or an unknown one.

    speckit-todo.py [--root <repo>] [--all]     --all adds the closed features and why each is closed
    speckit-todo.py [--root <repo>] --by-affects     the open features grouped by tag (a feature under each of its tags)
    speckit-todo.py [--root <repo>] --check     exit 1, with the line to add, when an open feature's tags are missing or unknown
    speckit-todo.py --state <specs/NNN-slug>     one feature's state
    speckit-todo.py --closed-by-status <dir>     `yes` when the spec's status line closes it (CLOSING), else `no` - the
                                                 push's in-progress refusal keeps its own open-box test and asks only this
"""

from __future__ import annotations

import argparse
import json
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
#: the tag vocabulary, relative to the repository root
AFFECTS = Path(".specify/affects.json")

_TASK = re.compile(r"^- \[( |x|X)\] ", re.M)
_STATUS = re.compile(r"^\*\*Status\*\*:?\s*(.+)$|^\*\*Status:\*\*\s*(.+)$", re.M)
_OWED = re.compile(r"^\*\*Owed at\*\*:?\s*(.+)$|^\*\*Owed at:\*\*\s*(.+)$", re.M)
_AFFECTS = re.compile(r"^\*\*Affects\*\*:?\s*(.+)$|^\*\*Affects:\*\*\s*(.+)$", re.M)
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
    affects: tuple[str, ...] = ()
    unknown: tuple[str, ...] = ()


@dataclass(frozen=True)
class Vocabulary:
    stage: dict[str, str]
    aliases: dict[str, tuple[str, ...]]


def vocabulary(root: Path) -> Vocabulary:
    """The tags and the stage of each, from `.specify/affects.json`; none when the file is absent."""
    path = root / AFFECTS
    data = json.loads(path.read_text()) if path.is_file() else {}
    tags = data.get("tags", {})
    return Vocabulary({t: v["stage"] for t, v in tags.items()}, {a: tuple(ts) for a, ts in data.get("aliases", {}).items()})


def affects(text: str, vocab: Vocabulary) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The known tags an `**Affects**:` line names (aliases expanded, in order, once each) and the unknown ones."""
    m = _AFFECTS.search(text)
    words = [w.strip().lower() for w in (m.group(1) or m.group(2)).split(",")] if m else []
    known: list[str] = []
    unknown: list[str] = []
    for w in filter(None, words):
        for t in vocab.aliases.get(w, (w,)):
            (known if t in vocab.stage else unknown).append(t)
    return tuple(dict.fromkeys(known)), tuple(dict.fromkeys(unknown))


def derived_stage(tags: tuple[str, ...], vocab: Vocabulary) -> str:
    """The earliest stage among the tags, `""` for none."""
    stages = [vocab.stage[t] for t in tags if vocab.stage[t] in STAGES]
    return min(stages, key=STAGES.index) if stages else ""


def owed_at(text: str) -> str:
    """The stage an overriding `**Owed at**:` line names, or `""` when there is none or it names no stage (a reason may follow)."""
    m = _OWED.search(text)
    value = (m.group(1) or m.group(2)).strip().lower() if m else ""
    return next((st for st in STAGES if value == st or value.startswith((st + " ", st + " -", st + ","))), "")


def feature(d: Path, vocab: Vocabulary | None = None) -> Feature:
    """One feature directory's state, tags and stage, from its own files."""
    vocab = vocab or vocabulary(d.parent.parent)
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
    known, unknown = affects(text, vocab)
    owed = owed_at(text) or derived_stage(known, vocab)
    return Feature(d.name, title, state, ticked, total, not spec.is_file(), why, owed, known, unknown)


def closed_by_status(d: Path) -> bool:
    """Does the spec's `**Status**:` line open with one of `CLOSING`? Only the line - no task is read."""
    spec = d / "spec.md"
    s = _STATUS.search(spec.read_text(errors="replace")) if spec.is_file() else None
    return bool(s) and (s.group(1) or s.group(2)).strip().lower().startswith(CLOSING)


def features(specs: Path) -> list[Feature]:
    """Every feature directory; a tree with no `specs/` has none (the push runs `--check` in any repository)."""
    vocab = vocabulary(specs.parent)
    return [feature(d, vocab) for d in sorted(specs.iterdir()) if d.is_dir()] if specs.is_dir() else []


def _line(f: Feature, extra: str = "") -> str:
    parts = [f.name, f.title]
    if f.total and f.state != "closed":
        parts.append(f"{f.ticked}/{f.total}")
    if f.no_spec:
        parts.append("(no spec.md)")
    if f.affects and f.state != "closed":
        parts.append(f"[{', '.join(f.affects)}]")
    if extra:
        parts.append(extra)
    return "  " + "  ".join(parts)


def _by_stage(group: list[Feature]) -> list[str]:
    out: list[str] = []
    for stage in (*STAGES, ""):
        staged = [f for f in group if f.owed == stage]
        if staged:
            out.append(f"  owed at {stage or 'NO STAGE (make speckit-todo CHECK=1 says how to set it)'} ({len(staged)})")
            out.extend("  " + _line(f) for f in staged)
    return out


def _by_affects(group: list[Feature], tags: list[str]) -> list[str]:
    out: list[str] = []
    for tag in (*tags, ""):
        tagged = [f for f in group if (tag in f.affects if tag else not f.affects)]
        if tagged:
            out.append(f"  affects {tag or 'NOTHING NAMED (make speckit-todo CHECK=1 says how to set it)'} ({len(tagged)})")
            out.extend("  " + _line(f) for f in tagged)
    return out


def report(specs: Path, show_closed: bool = False, by_affects: bool = False) -> str:
    fs = features(specs)
    tags = list(vocabulary(specs.parent).stage)
    out: list[str] = []
    for state in STATES:
        group = [f for f in fs if f.state == state]
        out.append(f"{state.upper()} ({len(group)})")
        out.extend(_by_affects(group, tags) if by_affects else _by_stage(group))
        out.append("")
    closed = [f for f in fs if f.state == "closed"]
    if show_closed:
        out.append(f"CLOSED ({len(closed)})")
        out.extend(_line(f, f.why) for f in closed)
        out.append("")
    n = {s: sum(f.state == s for f in fs) for s in STATES}
    out.append(f"open: {n['filed']} filed, {n['planned']} planned, {n['in progress']} in progress; closed: {len(closed)}")
    return "\n".join(out) + "\n"


def untagged(specs: Path) -> list[Feature]:
    """The open features that name no known tag, or an unknown one - none in a repository with no vocabulary."""
    if not (specs.parent / AFFECTS).is_file():
        return []
    return [f for f in features(specs) if f.state != "closed" and (not f.affects or f.unknown)]


def _problem(f: Feature) -> str:
    if f.no_spec:
        return "no spec.md - write one first"
    if f.unknown:
        return "unknown: " + ", ".join(f.unknown)
    return "no **Affects** line"


def check_message(missing: list[Feature], vocab: Vocabulary | None = None) -> str:
    """The refusal, with the line to add and the tags it may name - empty when nothing is missing."""
    if not missing:
        return ""
    names = "\n".join(f"  specs/{f.name}/spec.md  ({_problem(f)})" for f in missing)
    known = ", ".join([*(vocab.stage if vocab else ()), *(vocab.aliases if vocab else ())])
    return (
        f"speckit-todo: {len(missing)} open feature(s) do not say what they affect:\n{names}\n"
        "Add this line under the **Status** line, naming every tag it touches, comma-separated:\n"
        "  **Affects**: hamlet, magistracy\n"
        f"Tags: {known}.\n"
        "A new tag is one entry in .specify/affects.json. The stage is derived - the earliest among the tags, a tier not\n"
        "yet scripted counting its code too; a thing two tiers need is owed at the earlier one (the GM, 2026-10-10).\n"
    )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="list the spec-kit features not yet closed")
    ap.add_argument("--root", default=".", help="the repository root (default: the current directory)")
    ap.add_argument("--all", action="store_true", help="also list the closed features and why")
    ap.add_argument("--check", action="store_true", help="exit 1 when an open feature's tags are missing or unknown")
    ap.add_argument("--by-affects", action="store_true", help="group the open features by tag, not by stage")
    ap.add_argument("--state", metavar="DIR", help="print one feature directory's state and nothing else")
    ap.add_argument("--closed-by-status", metavar="DIR", help="print yes when the spec's status line closes it, else no")
    args = ap.parse_args(argv)
    if args.closed_by_status:
        sys.stdout.write(("yes" if closed_by_status(Path(args.closed_by_status)) else "no") + "\n")
        return 0
    if args.check:
        msg = check_message(untagged(Path(args.root) / "specs"), vocabulary(Path(args.root)))
        sys.stderr.write(msg)
        return 1 if msg else 0
    if args.state:
        sys.stdout.write(feature(Path(args.state)).state + "\n")
        return 0
    sys.stdout.write(report(Path(args.root) / "specs", show_closed=args.all, by_affects=args.by_affects))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
