#!/usr/bin/env python3
"""How many research questions a page-session brief ASSIGNS (feature 274 D1): the one count the write cap rests on.

    _brief_load.py <record dir> <brief> ...     prints `<kind or write> <count> <brief>` and the sections counted

WHY (feature 274, research R1). After feature 250 the cost per thing checked held, but the largest context doubled,
and it was the write sessions: a write session's cost follows its turn count (r = 0.92), groups had grown to twice
R11's size, and because every turn re-reads the context so far a session's cost grows roughly with the square of its
length. One 272 write session cost 24.5 M over 109 turns. So a WRITE session takes at most four questions (CAP), and
the runner counts every brief with this helper before it starts one, whatever generator wrote it (spec, round 3: a
required declaration would have broken the other features' generators until each changed).

WHAT IS COUNTED - only what the brief assigns (spec, round 4): the `## Your items` section (to the next `## `), and
the `**Your questions:**` and `**Your pairs**` lines or blocks. Never a "do not edit" paragraph, which names other
sessions' sections and would count them. In an item line:
  - each section named: `<page>/NNN` (the last segment of a page's name is accepted as an alias), a backticked `NNN`
    or a bare range `NNN-MMM` under the page named last in the line, or else under the item list's most-named page;
  - a range is expanded against the page's actual `NNN-*.html` fragments; code references (`file.py:195-304`) are
    stripped first;
  - a line naming no section counts one question per distinct item id (`B30`, `D52`), and at least one.
In the check-brief form, `PAGE=<p> SECTION=<NNN>` counts one each; a pair (`KIND=X (SECTION=NNN)`) one per section.
It errs toward over-counting, the safe side for a cap. Prototyped on the real briefs: 269's V2 counts 9, C1 6 and X1
10; 272's S 8; 271's `g1-check-a` and 269's `h1-check-a` 2 each (plan D1).

THE EXEMPT KINDS (spec, Edge Cases). A brief that is not a group's writing declares one line,
`<!-- page-load: kind=<kind> -->`: `check` (a check-and-apply session, which the cap does not cover), `assertions`
(feature 250's FR-002 briefs, many assertions inside existing questions), `split` (splitting an over-cap question) or
`handover` (a group handed to another feature). Any other kind is refused, and so is a brief that assigns nothing
countable and declares no kind: the count never fails open.
"""

from __future__ import annotations

import math
import pathlib
import re
import sys

CAP = 4
KINDS = ("check", "assertions", "split", "handover")
KIND_LINE = re.compile(r"<!--\s*page-load:\s*kind=([\w-]+)\s*-->")
NOT_PAGES = {"sources", "citations", "assets"}  # the registry, the assembled citations and the images: never a page
FRAGMENT = re.compile(r"(\d{3})-.*\.html$")
CODE_REF = re.compile(r"[\w/.-]+\.(?:py|json|md|js|svg|txt|sh)(?::[\d,-]+)?")
ITEM_ID = re.compile(r"\b[A-Z]{1,2}\d{2,3}\b")


def pages(record: pathlib.Path) -> list[str]:
    """Every research page, as its path under the record (`fields`, `cities/defenses`): a directory holding a question
    fragment. Derived, never listed, so a page added later is counted without an edit here."""
    got = set()
    for f in record.rglob("[0-9][0-9][0-9]-*.html"):
        rel = f.parent.relative_to(record).as_posix()
        if rel != "." and rel.split("/")[0] not in NOT_PAGES and not f.name.endswith(".notes.html"):
            got.add(rel)
    return sorted(got)


def _aliases(names: list[str]) -> dict[str, str]:
    """Each page by its full name, and by its last segment where no other page shares it (`defenses`)."""
    out = {p: p for p in names}
    last: dict[str, list[str]] = {}
    for p in names:
        last.setdefault(p.split("/")[-1], []).append(p)
    for short, full in last.items():
        if len(full) == 1:
            out.setdefault(short, full[0])
    return out


def fragments(record: pathlib.Path, page: str, lo: int, hi: int) -> set[int]:
    """The page's question numbers in `lo..hi`, from its fragments on disk."""
    d = record / page
    got = {int(m.group(1)) for f in d.glob("[0-9][0-9][0-9]-*.html") if (m := FRAGMENT.match(f.name)) and not f.name.endswith(".notes.html")}
    return {n for n in got if lo <= n <= hi}


def declared(text: str) -> str:
    """The kind the brief declares, or "" when it declares none."""
    m = KIND_LINE.search(text)
    return m.group(1) if m else ""


def assignment_lists(text: str) -> tuple[str, str]:
    """(the `## Your items` section, the `**Your questions:**` and `**Your pairs**` blocks) - all a brief assigns."""
    m = re.search(r"^## Your items[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    items = m.group(1) if m else ""
    blocks = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"\*\*Your (?:questions|pairs)\b", line):
            block = [line]
            for nxt in lines[i + 1 :]:
                if not nxt.strip() or re.match(r"\*\*|#|\d+\.\s", nxt):
                    break
                block.append(nxt)
            blocks.append("\n".join(block))
    return items, "\n".join(blocks)


def count(text: str, record: pathlib.Path) -> tuple[int, list[str]]:
    """(questions assigned, what was counted: `page/NNN` for a section, the item id for a new question)."""
    alias = _aliases(pages(record))
    names = sorted(alias, key=len, reverse=True)
    page_re = "(?<![\\w-])(" + "|".join(re.escape(p) for p in names) + ")" if names else "(?!x)x"
    items, blocks = assignment_lists(text)
    sections: set[tuple[str, int]] = set()
    for p, s in re.findall(r"PAGE=([\w/-]+)\s+SECTION=(\d{3})", blocks):
        sections.add((alias.get(p, p), int(s)))
    blocks_left = re.sub(r"PAGE=[\w/-]+\s+SECTION=\d{3}", " ", blocks)
    for s in dict.fromkeys(re.findall(r"KIND=\w+\s*\(SECTION=(\d{3})\)", blocks_left)):
        sections.add(("?", int(s)))
    named = [alias[p] for p in re.findall(page_re + r"[/ ]", items)]
    main = max(dict.fromkeys(named), key=named.count) if named else None
    new: list[str] = []
    tok_re = re.compile(page_re + r"/(\d{3})(?:-(\d{3}))?|`(\d{3})(?:-(\d{3}))?`|\b(\d{3})-(\d{3})\b")
    for line in re.split(r"\n(?=- )", items):
        if not line.startswith("- "):
            continue
        got: set[tuple[str, int]] = set()
        page = main
        for tok in tok_re.finditer(CODE_REF.sub(" ", line)):
            if tok.group(1):
                page, lo, hi = alias[tok.group(1)], int(tok.group(2)), int(tok.group(3) or tok.group(2))
            elif page is None:
                continue
            elif tok.group(4):
                lo, hi = int(tok.group(4)), int(tok.group(5) or tok.group(4))
            else:
                lo, hi = int(tok.group(6)), int(tok.group(7))
            got |= {(page, n) for n in (fragments(record, page, lo, hi) if hi > lo else {lo})}
        if got:
            sections |= got
        else:
            ids = list(dict.fromkeys(ITEM_ID.findall(line.split("**")[0])))
            new += ids or [line[2:].split()[0]]
    detail = [f"{p}/{n:03d}" for p, n in sorted(sections)] + new
    return len(sections) + len(new), detail


def load(text: str, record: pathlib.Path) -> tuple[str, int, list[str]]:
    """(the declared kind or "", questions assigned, what was counted)."""
    n, detail = count(text, record)
    return declared(text), n, detail


def split_names(brief: pathlib.Path, n: int) -> list[str]:
    """The briefs a group of `n` questions splits into, at most CAP each: `v2-write.md` -> `v2a-write.md`, `v2b-...`."""
    stem = brief.stem
    group, tail = (stem[: -len("-write")], "-write") if stem.endswith("-write") else (stem, "")
    return [f"{group}{chr(97 + i)}{tail}{brief.suffix}" for i in range(math.ceil(n / CAP))]


def refusal(brief: pathlib.Path, text: str, record: pathlib.Path) -> str:
    """Why the runner must not start this brief, or "" when it may."""
    kind, n, detail = load(text, record)
    if kind:
        return "" if kind in KINDS else f"it declares kind={kind}, which is not an exempt kind ({', '.join(KINDS)})"
    if n == 0:
        return ("it assigns nothing the count can read (no `## Your items`, `**Your questions:**` or `**Your pairs**` naming "
                f"a question) and declares no kind - add `<!-- page-load: kind=<{'|'.join(KINDS)}> -->` if it is not a group's writing")
    if n > CAP:
        parts = split_names(brief, n)
        return (f"it assigns {n} questions ({', '.join(detail)}); a write session takes at most {CAP} (feature 274: a write "
                f"session's cost grows with the square of its length). Split it into {len(parts)} briefs of at most {CAP} - "
                f"{', '.join(parts)} - each with its own handoff, and queue them one after another; or, for a deliberate larger "
                "load, set WRITE_CAP_OK='<reason>'")
    return ""


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: _brief_load.py <record dir> <brief> ...", file=sys.stderr)
        return 2
    record = pathlib.Path(argv[0])
    bad = 0
    for b in map(pathlib.Path, argv[1:]):
        text = b.read_text(encoding="utf-8")
        kind, n, detail = load(text, record)
        why = refusal(b, text, record)
        bad += bool(why)
        print(f"{kind or 'write'} {n} {b.name}: {', '.join(detail) or '-'}" + (f"\n  REFUSED: {why}" if why else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
