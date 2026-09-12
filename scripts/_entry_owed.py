#!/usr/bin/env python3
"""Which feature classes' MODAL PROSE may have gone stale - the report that makes a drifted entry
impossible to miss silently.

WHY THIS EXISTS (feature 234, GM 2026-09-12). Told to update the pigsty write-up on the map page, the
GM asked the obvious next question: *"if I hadn't said that ... then would you have done it? it's not
then... that should be another fix to the project guidelines and what have you."* It would not have
been. What a modal says about a feature IS the docstring of its `Kind` class (feature 189), written FROM
a research section the class names in its `Entry:` tag - and nothing noticed when that section's content
moved underneath it. The prose and the record simply agreed with themselves, separately.

WHAT IT REPORTS, AND WHAT IT DOES NOT. A class is named when the research section its `Entry:` points at
had its BODY changed in this delta AND the class's own EXPLANATION PROSE did not. It is a REPORT: it
never blocks, at either decision point, and there is no escape token because there is nothing to escape.
The reason is measured rather than felt - `specs/234-entry-owed-when-the-record-moves/research.md` R2
replayed the same key over this repository's history and it fires on 30 of the last 32 research-only
commits, up to 41 classes at once, every one of them a maintenance sweep of the record (footnotes moved
onto citations pages, session notes turned into comments, the translation pass) that changes no
obligation on any modal. The root CLAUDE.md keeps rules off the enforced list for exactly that, so this
one names and does not refuse. What is owed on a named pair is doctrine: dispatch `entry-drift`, then
rewrite the prose or record why not to `dev/bypass-log/` (spec D6, which also records that the GM has
not ruled on the absence of a mechanism).

THE PROSE HALF IS DERIVED, NEVER RESTATED. "Explanation prose" is `_TAGS` less `_DATA_TAGS`, asked of
the engine, so a tag added or moved there cannot leave this script quietly checking the wrong thing. The
exemption is keyed on the prose and NOT on the whole docstring: the docstring also carries
`Name:`/`Covers:`/`Label:`/`Sources:`/`Entry:` (feature 207), so re-pointing an `Entry:` or fixing a
house-style slip would otherwise silence the check for that class while the words a reader sees stood
untouched.

ASKED FRESH AT TWO DECISION POINTS, NEVER CACHED - the same discipline as `_review_owed.py`:
  1. `make page-check` - the target a research-page-plus-docstring delta actually owes;
  2. `scripts/sync-with-main.sh` at push time.
`make done` is deliberately NOT one: it exits at its short-circuit (skill `Makefile:122`) before any
phase runs when engine content is unchanged, and neither a `research/*.html` edit nor a class docstring
is engine content (features 188, 189, 207) - so a report there would ship green and never print once on
the delta shape this exists for.

Usage: _entry_owed.py [--root DIR] [--why]
  prints one line per named class (empty when nothing is named); `--why` prints the one-line ruling.
  Exit 0 either way; 1 when DIR is not a git repository.
"""

from __future__ import annotations

import argparse
import ast
import os
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

SKILL = ".claude/skills/diagram"
RESEARCH = f"{SKILL}/research"
CLASSES = f"{SKILL}/l7r/diagram/interactive/classes"


def _git(root: Path, *args: str) -> str | None:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return p.stdout if p.returncode == 0 else None


def base_of(root: Path) -> tuple[str, str]:
    """(ref, description): the merge base of HEAD with origin/main, as `_review_owed.py` computes it."""
    head = (_git(root, "rev-parse", "--verify", "-q", "HEAD") or "").strip()
    if not head:
        return "", "no commits yet"
    if (_git(root, "rev-parse", "--verify", "-q", "origin/main") or "").strip():
        mb = (_git(root, "merge-base", "HEAD", "origin/main") or "").strip()
        if mb:
            return mb, f"origin/main (merge base {mb[:8]})"
    return head, f"HEAD ({head[:8]}; no origin/main)"


def _engine(root: Path):  # noqa: ANN202 - the engine's own modules, imported once
    """The engine's parsers, so this script has no second copy of them to drift from."""
    skill = str(root / SKILL)
    if skill not in sys.path:
        sys.path.insert(0, skill)
    from l7r.diagram.interactive import sources
    from l7r.diagram.interactive.classes import _base

    return sources, _base


def prose_of(doc: str | None, name: str, _base) -> str:  # noqa: ANN001
    """A class's EXPLANATION prose - every tag the engine does not class as data. DERIVED from
    `_DATA_TAGS` rather than listed here (spec FR-002/FR-010)."""
    parts = _base.parse_explanation(doc, name)
    return "␟".join(parts.get(t, "") for t in _base._TAGS if t not in _base._DATA_TAGS)


def classes_in(text: str, _base, lines: dict[str, int] | None = None) -> dict[str, str]:  # noqa: ANN001
    """key -> explanation prose, for every `Kind` subclass in one `classes/*.py` SOURCE TEXT. Parsed
    with `ast` so the old side of a delta can be read straight out of a git blob. `lines`, when given,
    collects key -> the class's line number, which is what a report has to hand a reader (FR-005)."""
    out: dict[str, str] = {}
    lines = {} if lines is None else lines
    for node in ast.walk(ast.parse(text)):
        if not isinstance(node, ast.ClassDef):
            continue
        key = None
        for st in node.body:
            if isinstance(st, ast.Assign) and isinstance(st.value, ast.Constant) and isinstance(st.value.value, str):
                if any(isinstance(tg, ast.Name) and tg.id == "key" for tg in st.targets):
                    key = st.value.value
        doc = ast.get_docstring(node)
        if not key or not doc:
            continue
        try:
            out[key] = prose_of(doc, node.name, _base)
        except ValueError:
            continue  # not a Kind - no tagged explanation
        lines[key] = node.lineno
    return out


def moved_anchors(root: Path, base: str, sources) -> set[str]:  # noqa: ANN001
    """The `file#anchor` of every research section whose BODY changed against `base`."""
    moved: set[str] = set()
    names = (_git(root, "diff", "--name-only", base, "--", f"{RESEARCH}/*.html") or "").split()
    for rel in names:
        new = root / rel
        old_text = _git(root, "show", f"{base}:{rel}")
        if old_text is None or not new.is_file():
            continue
        with tempfile.TemporaryDirectory() as td:
            op = Path(td) / Path(rel).name
            op.write_text(old_text, encoding="utf-8")
            before = {h: b for h, b, _a in sources._parsed(str(op))}
        for head, body, anchor in sources._parsed(str(new)):
            if before.get(head) != body:
                moved.add(f"{os.path.relpath(rel, RESEARCH)}#{anchor}")
    return moved


def owed(root: Path) -> tuple[str, list[str]]:
    """(the base's description, one `key - what moved - where the prose lives` line per named class)."""
    base, desc = base_of(root)
    if not base:
        return desc, []
    sources, _base = _engine(root)
    moved = moved_anchors(root, base, sources)
    if not moved:
        return desc, []
    now: dict[str, str] = {}
    was: dict[str, str] = {}
    at: dict[str, str] = {}
    for path in sorted((root / CLASSES).glob("*.py")):
        rel = os.path.relpath(path, root)
        here: dict[str, int] = {}
        now |= classes_in(path.read_text(encoding="utf-8"), _base, here)
        at |= {k: f"{rel}:{n}" for k, n in here.items()}
        old_text = _git(root, "show", f"{base}:{rel}")
        if old_text is not None:
            was |= classes_in(old_text, _base)
    from l7r.diagram.interactive.classes import CLASSES as REGISTRY

    out: list[str] = []
    for key, fc in sorted(REGISTRY.items()):
        hit = sorted({q["url"].rsplit("/", 1)[-1] for q in sources.research_questions(fc.entry)} & moved)
        if hit and key in was and was[key] == now.get(key):
            out.append(f"{key} - {' '.join(hit)} - prose at {at.get(key, CLASSES)}")
    return desc, out


def ruling(desc: str, lines: Sequence[str]) -> str:
    if not lines:
        return f"no modal's research section moved against {desc}"
    return f"research moved under {len(lines)} unchanged modal(s) against {desc} - dispatch `entry-drift` at each, then rewrite the prose or record why not in dev/bypass-log/"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the clone (default: the cwd's repository)")
    ap.add_argument("--why", action="store_true", help="print the one-line ruling instead of the names")
    args = ap.parse_args(argv)
    top = (_git(Path(args.root), "rev-parse", "--show-toplevel") or "").strip()
    if not top:
        print(f"_entry_owed: {args.root} is not a git repository", file=sys.stderr)
        return 1
    desc, lines = owed(Path(top))
    print(ruling(desc, lines) if args.why else "\n".join(lines), end="\n" if (args.why or lines) else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
