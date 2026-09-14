"""Which research sections' VISIBLE WORDING moved against the merge base - the measurement behind feature
242's answer to the entry-drift gate (spec D7, research.md R12).

`scripts/_entry_owed.py` names a modal whenever the raw BODY of a section its entry points at differs
from the merge base - and feature 242 touched nearly every section by adding footnote marks, absence
notes and HTML comments, none of which is a finding moving. This script asks the narrower question the
gate cannot: per moved section, does the prose a READER sees differ once footnote marks, HTML comments,
tags, the `Sources:` roster line and whitespace are stripped? MARKS-ONLY sections gained nothing a modal
could drift from; WORDING-MOVED sections are the ones `entry-drift` is dispatched at.

    python3 specs/242-cite-the-unfootnoted-assertions/measure/prose_moved.py [--root <clone>] [--diff]

Prints one line per moved section: `MARKS-ONLY <file>#<anchor>` or `WORDING-MOVED <file>#<anchor>`, then
the totals; `--diff` appends a unified diff of the stripped prose for each WORDING-MOVED section.
"""

from __future__ import annotations

import argparse
import difflib
import html
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = ".claude/skills/diagram"
RESEARCH = f"{SKILL}/research"


def _git(root: Path, *args: str) -> str | None:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return p.stdout if p.returncode == 0 else None


def base_of(root: Path) -> str:
    return (_git(root, "merge-base", "HEAD", "origin/main") or "").strip()


_COMMENT = re.compile(r"<!--.*?-->", re.S)
_SUP = re.compile(r"<sup\b[^>]*class=\"fn\"[^>]*>.*?</sup>", re.S)
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def visible(body: str) -> str:
    """The prose a reader sees: comments, footnote marks and tags stripped, the roster line dropped,
    whitespace collapsed, entities decoded."""
    text = _COMMENT.sub("", body)
    text = _SUP.sub("", text)
    paras = re.split(r"(?=<p\b)|(?=<li\b)|(?=<h[1-6]\b)|(?=<t[dh]\b)", text)
    kept = []
    for para in paras:
        plain = _WS.sub(" ", html.unescape(_TAG.sub(" ", para))).strip()
        if plain.startswith("Sources:"):
            continue
        kept.append(plain)
    return _WS.sub(" ", " ".join(kept)).strip()


def sections(root: Path, path: Path):
    skill = str(root / SKILL)
    if skill not in sys.path:
        sys.path.insert(0, skill)
    from l7r.diagram.interactive import sources

    return list(sources._parsed(str(path)))


def moved(root: Path, base: str) -> list[tuple[str, str, str, str]]:
    """(file#anchor, verdict, old visible, new visible) for every section whose raw body moved."""
    out = []
    names = (_git(root, "diff", "--name-only", base, "--", f"{RESEARCH}/*.html") or "").split()
    for rel in sorted(names):
        if "/citations/" in rel or rel.endswith("SOURCES.html"):
            continue
        new = root / rel
        old_text = _git(root, "show", f"{base}:{rel}")
        if old_text is None or not new.is_file():
            continue
        with tempfile.TemporaryDirectory() as td:
            op = Path(td) / Path(rel).name
            op.write_text(old_text, encoding="utf-8")
            before = {h: b for h, b, _a in sections(root, op)}
        for head, body, anchor in sections(root, new):
            if head not in before or before[head] == body:
                continue
            was, now = visible(before[head]), visible(body)
            verdict = "MARKS-ONLY" if was == now else "WORDING-MOVED"
            out.append((f"{os.path.relpath(rel, RESEARCH)}#{anchor}", verdict, was, now))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--diff", action="store_true")
    ap.add_argument("--pairs", action="store_true", help="read `_entry_owed.py` lines on stdin; classify each named pair")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    base = base_of(root)
    if not base:
        print("no merge base with origin/main", file=sys.stderr)
        return 2
    rows = moved(root, base)
    if a.pairs:
        verdicts = {k: v for k, v, _w, _n in rows}
        dispatch = 0
        for line in sys.stdin:
            line = line.strip()
            if " - prose at " not in line:
                continue
            cls, anchors, _at = line.split(" - ", 2)
            hit = [x for x in anchors.split() if verdicts.get(x) == "WORDING-MOVED"]
            if hit:
                dispatch += 1
            print(f"{'DISPATCH' if hit else 'MARKS-ONLY'} {cls} - {' '.join(hit) or anchors}")
        print(f"PAIRS dispatch={dispatch} (base {base[:8]})")
        return 0
    for key, verdict, was, now in rows:
        print(f"{verdict} {key}")
        if a.diff and verdict == "WORDING-MOVED":
            for line in difflib.unified_diff(was.split(". "), now.split(". "), lineterm="", n=0):
                print(f"    {line}")
    n_marks = sum(1 for r in rows if r[1] == "MARKS-ONLY")
    print(f"TOTAL moved={len(rows)} marks-only={n_marks} wording-moved={len(rows) - n_marks} (base {base[:8]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
