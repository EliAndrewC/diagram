#!/usr/bin/env python3
"""FR-002's work list, derived: the real-world assertions each quote-check report found carrying no footnote.

The six reports (`specs/242-*/handoff/reports/*quotecheck.md`, `qc-*.md`) are verbatim agent returns, so
the listing has no one shape. What was measured on them (2026-09-21), and what this therefore does:

- THE OPENER is a line carrying "assertion" and "footnote" (which "unfootnoted" contains), case-blind,
  that is NOT itself a bullet or a table row - a listing's own bullets and a summary table's count row
  both carry the two words. It is a markdown heading in five reports and a plain line in one, which
  opens it three times, once per page.
- THE BLOCK ENDS at the next horizontal rule (`---`) or the next markdown heading at the opener's level
  or above (any `#`/`##` heading where the opener is a plain line). Never at a blank line: one report
  puts a blank between every item.
- AN ITEM is a top-level `- ` bullet in the block.
- ITS SECTION is, in order: the nearest bold-only line above it inside the block; the bullet's own
  leading `*italic*` prefix, quoted or not; a trailing `("...")`. ITS PAGE is a `<name>.html` named in a
  deeper heading inside the block (which also clears the section), else in the nearest bold line, else in
  the opener, else in the nearest heading above it; a report about one page names it nowhere, so that
  one is mapped by file name. A bullet that begins "Skipped", "Nothing else" or "Other sections" is the
  report's note of what it passed over, not an item.
- A report's OWN COUNT, where its summary table states one, is compared, and a mismatch fails.
- A report with no opener FAILS the run, so a new shape cannot silently drop a page.

    assertions.py            the counts per report and page
    assertions.py --list     every item
"""

from __future__ import annotations

import pathlib
import re
import sys

REPORTS = pathlib.Path(__file__).resolve().parents[2] / "242-cite-the-unfootnoted-assertions/handoff/reports"
NAMES = ("hw-quotecheck.md", "urban-quotecheck.md", "qc-buildings-vegetation.md", "qc-fabric-government-hinterland-ways.md", "qc-fields-religion-archetypes.md", "qc-river-cities-defenses-towns.md")
_BULLET = re.compile(r"^\s*[-*]\s")
_HEADING = re.compile(r"^(#{1,6})\s")
_BOLD = re.compile(r"^\*\*(.+?)\*\*[:.]?\s*$")
_PAGE = re.compile(r"([a-z][a-z-]+)\.html")
_ITALIC = re.compile(r"^-\s+\*\"?([^*]+?)\"?\*")
_NOT_AN_ITEM = ("skipped", "nothing else", "other sections")
#: a report about ONE page never names it in its listing
_ONE_PAGE = {"urban-quotecheck.md": "urban-features"}
_PAREN = re.compile(r'\("([^"]+)"\)')


def is_opener(line: str) -> bool:
    low = line.lower()
    return "assertion" in low and "footnote" in low and not _BULLET.match(line) and not line.lstrip().startswith("|")


def stated_count(lines: list[str]) -> int | None:
    """The total a report's own summary table gives for this class, where it gives one."""
    for line in lines:
        low = line.lower()
        if line.lstrip().startswith("|") and "unfootnoted" in low:
            cells = [c.strip(" *") for c in line.strip().strip("|").split("|")]
            numbers = [int(c) for c in cells[1:] if c.isdigit()]
            if numbers:
                return numbers[-1]
    return None


def page_above(lines: list[str], at: int) -> str:
    for line in reversed(lines[:at]):
        if _HEADING.match(line) and _PAGE.search(line):
            return _PAGE.search(line).group(1)  # type: ignore[union-attr]
    return ""


def items_of(lines: list[str]) -> list[dict]:
    out: list[dict] = []
    i = 0
    while i < len(lines):
        if not is_opener(lines[i]):
            i += 1
            continue
        head = _HEADING.match(lines[i])
        level = len(head.group(1)) if head else 2
        found = _PAGE.search(lines[i])
        page = found.group(1) if found else page_above(lines, i)
        section = ""
        i += 1
        while i < len(lines):
            line = lines[i]
            deeper = _HEADING.match(line)
            if line.strip() == "---" or (deeper and len(deeper.group(1)) <= level):
                break
            bold = _BOLD.match(line.strip())
            if deeper and _PAGE.search(line):
                page, section = _PAGE.search(line).group(1), ""  # type: ignore[union-attr]
            elif bold:
                section = bold.group(1)
                named = _PAGE.search(section)
                page = named.group(1) if named else page
            elif line.startswith("- ") and not line[2:].lstrip("*_ ").lower().startswith(_NOT_AN_ITEM):
                own = _ITALIC.match(line) or _PAREN.search(line)
                out.append({"page": page, "section": section or (own.group(1) if own else ""), "text": line[2:].strip()})
            i += 1
    return out


def main(argv: list[str]) -> int:
    failed = False
    total = 0
    all_pages: set[str] = set()
    for name in NAMES:
        lines = (REPORTS / name).read_text(encoding="utf-8").splitlines()
        items = [{**item, "page": item["page"] or _ONE_PAGE.get(name, "")} for item in items_of(lines)]
        stated = stated_count(lines)
        if not any(is_opener(line) for line in lines):
            print(f"FAIL {name}: no listing found - a new shape; read the report and extend the opener")
            failed = True
            continue
        pages: dict[str, int] = {}
        for item in items:
            pages[item["page"] or "?"] = pages.get(item["page"] or "?", 0) + 1
        bare = sum(1 for item in items if not item["section"])
        note = "" if stated is None else (f"  the report's own count: {stated}" + ("" if stated == len(items) else "  MISMATCH"))
        failed = failed or (stated is not None and stated != len(items))
        print(f"{name}: {len(items)} item(s), {bare} with no section found  {pages}{note}")
        total += len(items)
        all_pages.update(pages)
        if "--list" in argv:
            for item in items:
                print(f"    [{item['page']}] {item['section'][:50]} | {item['text'][:110]}")
    print(f"total: {total} item(s) over {len(NAMES)} reports and {len(all_pages)} page(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
