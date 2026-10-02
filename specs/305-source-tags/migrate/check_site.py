#!/usr/bin/env python3
"""Feature 305 SC-003, over the BUILT site: every listed work sits under exactly one section heading, the headings
follow `source-sections.json`'s order, and every work in full shows a label per tag, each with its explanation.

    python3 specs/305-source-tags/migrate/check_site.py [SITE_DIR]

Reads the question pages (`q/*.html`, their "Works cited here"), the registry index and the one-page record. Prints
the counts and every failure; exits 1 on any.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

RESEARCH = pathlib.Path(".claude/skills/diagram/research")
_SECTION = re.compile(r'<h3 class="works-section" id="(?:page-)?([^"]+)">')
_WORK = re.compile(r'<h4 id="(?:work-)?([a-z0-9][a-z0-9-]*)">.*?</h4>\s*(<p class="srctags">.*?</p>)', re.S)
_CHIP = re.compile(r'<span class="srctag srctag-(\w+)" data-def="([^"]+)" title="[^"]+">[^<]+</span>')


def check_list(name: str, text: str, order: list[str], fails: list[str]) -> tuple[int, int]:
    """One list of works: its section headings in order, each work under one heading with its labels."""
    heads = [(m.start(), m.group(1)) for m in _SECTION.finditer(text)]
    ids = [h for _at, h in heads]
    if ids != sorted(ids, key=order.index):
        fails.append(f"{name}: sections out of order: {ids}")
    works = 0
    for m in _WORK.finditer(text):
        works += 1
        above = [h for at, h in heads if at < m.start()]
        if not above:
            fails.append(f"{name}: work {m.group(1)} under no section heading")
        chips = _CHIP.findall(m.group(2))
        facets = {f for f, _d in chips}
        if not chips or not (facets == {"canon"} or {"period", "region", "kind"} <= facets):
            fails.append(f"{name}: work {m.group(1)} has labels {sorted(facets)}")
    return len(heads), works


def main() -> int:
    site = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else RESEARCH / "site"
    order = [s["id"] for s in json.loads((RESEARCH / "source-sections.json").read_text(encoding="utf-8"))["sections"]]
    fails: list[str] = []
    pages = sections = works = 0
    for page in sorted((site / "q").glob("*.html")):
        text = page.read_text(encoding="utf-8")
        if 'id="page-works"' not in text:
            continue
        pages += 1
        s, w = check_list(page.name, text.split('id="page-works"', 1)[1], order, fails)
        sections += s
        works += w
    s, w = check_list("all.html", (site / "all.html").read_text(encoding="utf-8"), order, fails)
    index = (site / "sources" / "index.html").read_text(encoding="utf-8")
    index_ids = _SECTION.findall(index)
    if index_ids != [i for i in order if i in index_ids]:
        fails.append(f"sources/index.html: sections out of order: {index_ids}")
    print(f"question pages with works: {pages}; their section headings: {sections}; works: {works}")
    print(f"all.html: {s} section headings, {w} works; sources/index.html: {len(index_ids)} sections")
    print("\n".join(fails[:40]) or "SC-003: every check passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
