#!/usr/bin/env python3
"""Search the GM's setting canon for EVERY term of a claim in one pass (feature 250 D16, research R7).

WHY. On `cities/fabric` two of three items were claims about the setting, and the write session ran about fifteen
greps through `budgets.md` and `l7r.md`, one a turn, each turn re-reading a context that peaked at 137,000 tokens
(R7). One command that takes every term at once, and names the heading each hit sits under, answers the same
question in one turn. `canon-read-hooks.sh` makes it the only way in: a direct read of a canon file is refused with
this command, and a second call within three tool calls is refused as an unfolded term.

    _canon.py "imperial road|merchant share|artisan"

Terms are plain, case-insensitive substrings separated by `|`. Per term: every hit as `file:line [heading] text`
(the line cut at 400 characters), at most 15 per term, then the count; a term with none says so, which is itself
the answer an absence note needs.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

ROOTS = (pathlib.Path("/host-l7r-repo/setting"), pathlib.Path("/host-l7r-repo/gm-assistant/setting"))
CAP = 15
WIDTH = 400


def canon_files(roots: tuple[pathlib.Path, ...] = ROOTS) -> list[pathlib.Path]:
    """The canon: every markdown and text file under the setting directories, their CLAUDE.md files excepted."""
    out: list[pathlib.Path] = []
    for root in roots:
        if root.is_dir():
            out += sorted(p for p in root.rglob("*") if p.suffix in (".md", ".txt") and p.name != "CLAUDE.md")
    return out


def search(terms: list[str], files: list[pathlib.Path]) -> dict[str, list[str]]:
    """term -> its hits, each `file:line [heading] text`, in file order."""
    hits: dict[str, list[str]] = {t: [] for t in terms}
    for f in files:
        heading = ""
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.startswith("#"):
                heading = line.lstrip("#").strip()
            low = line.lower()
            for t in terms:
                if t.lower() in low:
                    text = line.strip()
                    hits[t].append(f"{f}:{n} [{heading[:60]}] {text[:WIDTH]}{'...' if len(text) > WIDTH else ''}")
    return hits


def main(argv: list[str] | None = None, files: list[pathlib.Path] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("terms", help='the claim\'s terms, "a|b|c"')
    args = ap.parse_args(argv)
    terms = [t.strip() for t in args.terms.split("|") if t.strip()]
    if not terms:
        print('canon: no term given - TERMS="<a>|<b>|<c>", every term of the claim at once', file=sys.stderr)
        return 2
    found = search(terms, canon_files() if files is None else files)
    for t in terms:
        rows = found[t]
        print(f"== {t}: {len(rows)} hit(s){'' if len(rows) <= CAP else f', the first {CAP} shown'}")
        for r in rows[:CAP]:
            print(f"  {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
